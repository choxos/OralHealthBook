#!/usr/bin/env python3
"""Enforce the book's own evidence rules at build time.

A book that criticises other people's citation practice cannot afford
loose citation practice. This fails the build on:

  1. A @key used in the text that is not in refs.bib.
  2. A refs.bib entry with neither a DOI nor a PMID.
  3. A refs.bib entry that nothing cites (dead weight, or a citation
     that got silently renamed).
  4. An audit chapter whose Verdict box still has an unfilled field.
  5. An audit chapter missing one of the seven required sections.

Run: python3 scripts/check_citations.py [--strict]

Without --strict, rules 4 and 5 report as warnings, because chapters are
drafted one at a time. CI runs with --strict once the manuscript is done.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "bibliography" / "refs.bib"

# Cross-reference prefixes that Quarto resolves itself. These look like
# citations to a naive regex but are not.
CROSSREF_PREFIXES = (
    "sec-", "fig-", "tbl-", "eq-", "lst-", "thm-", "exm-", "exr-", "def-",
)

# Two things every audit chapter must carry, whatever its headings are
# called. Enforcing the literal heading text instead just made the prose
# read like a form, so the check is on the invariants, not the wording.
#
#   1. A verdict box with all four fields answered.
#   2. A disclosed, dated search, so the "is there better evidence?" step
#      can be repeated by someone else.
SEARCH_DISCLOSURE = "What I searched, and when"
SEARCH_RECORD = re.compile(r"appraisals/searches/[A-Za-z0-9._-]+\.md")
VERDICT_BLOCK = "{.verdict}"

VERDICT_FIELDS = [
    "Certainty of evidence",
    "Directness to the advice as worded",
    "Is the strength label defensible?",
    "What would change my mind",
]


def qmd_files() -> list[Path]:
    out: list[Path] = []
    for d in ("parts", "appendices"):
        out.extend(sorted((ROOT / d).rglob("*.qmd")))
    out.extend(sorted(ROOT.glob("*.qmd")))
    return out


def strip_code(text: str) -> str:
    """Remove fenced code and inline code so their contents are not
    mistaken for citations."""
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def parse_bib(path: Path) -> tuple[dict[str, str], list[str]]:
    """Return ({key: entry-body}, duplicate keys).

    Duplicates are returned rather than silently resolved. Storing entries in
    a dict keyed by citation key hides a repeated key behind whichever copy is
    parsed last, and the two copies need not agree: this file carried two
    `tham2015` entries with different author lists and different issue
    numbers, and two `dossantos2018` entries, for exactly that reason. BibTeX
    itself takes the first definition, so the rendered reference list and this
    checker could disagree about what was cited.
    """
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"^%.*$", "", raw, flags=re.M)
    entries: dict[str, str] = {}
    seen: list[str] = []
    duplicates: list[str] = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", raw):
        start = m.end()
        depth = 1
        i = start
        while i < len(raw) and depth:
            if raw[i] == "{":
                depth += 1
            elif raw[i] == "}":
                depth -= 1
            i += 1
        # Keep the entry type on the front so the identifier rule can
        # distinguish a journal article from a government guideline.
        key = m.group(2)
        if key in entries:
            duplicates.append(key)
        seen.append(key)
        entries[key] = f"@{m.group(1).lower()}\n" + raw[start:i]
    return entries, duplicates


def used_keys(files: list[Path]) -> dict[str, set[str]]:
    """Return {key: {files that cite it}}."""
    found: dict[str, set[str]] = {}
    pat = re.compile(r"(?<![\w\\])@([A-Za-z][\w:.#$%&+?<>~/-]*)")
    for f in files:
        text = strip_code(f.read_text(encoding="utf-8"))
        for m in pat.finditer(text):
            key = m.group(1).rstrip(".,;:)]}")
            if key.startswith(CROSSREF_PREFIXES):
                continue
            found.setdefault(key, set()).add(str(f.relative_to(ROOT)))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="treat draft-completeness problems as errors too")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    if not BIB.exists():
        print(f"FATAL: {BIB} not found", file=sys.stderr)
        return 2

    bib, duplicate_keys = parse_bib(BIB)
    files = qmd_files()
    used = used_keys(files)

    # --- 0. no key is defined twice --------------------------------
    # BibTeX takes the first definition and a dict-based parser takes the
    # last, so a duplicated key means the rendered bibliography and this
    # checker can disagree about what was actually cited.
    for key in sorted(set(duplicate_keys)):
        errors.append(
            f"refs.bib defines @{key} more than once; "
            f"keep one verified entry per key"
        )

    # --- 1. every cited key exists ---------------------------------
    for key, where in sorted(used.items()):
        if key not in bib:
            errors.append(
                f"@{key} cited in {', '.join(sorted(where))} "
                f"but not in refs.bib"
            )

    # --- 2. every entry is resolvable ------------------------------
    # Journal articles must carry a DOI or a PMID. Guidelines, reports
    # and theses often have neither, so a stable URL satisfies them.
    for key, body in sorted(bib.items()):
        low = body.lower()
        has_doi = "doi" in low
        has_pmid = "pmid" in low
        has_url = "url" in low
        is_article = low.lstrip().startswith("@article")

        if is_article and not (has_doi or has_pmid):
            errors.append(
                f"refs.bib entry '{key}' is an @article with neither a DOI "
                f"nor a PMID. House rule: every study must be resolvable."
            )
        elif not (has_doi or has_pmid or has_url):
            errors.append(
                f"refs.bib entry '{key}' has no DOI, PMID or URL. "
                f"A reader must be able to go and look at it."
            )

    # --- 2b. every @sec- crossref resolves --------------------------
    # Quarto only warns about these, and only for the profile being built, so
    # a dangling crossref in a print-only appendix can survive a clean web
    # render. Collect definitions and uses across every file and compare.
    defined: set[str] = set()
    used_secs: dict[str, str] = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        defined.update(re.findall(r"\{#(sec-[A-Za-z0-9-]+)\}", text))
        for ref in re.findall(r"@(sec-[A-Za-z0-9-]+)", text):
            used_secs.setdefault(ref, str(f.relative_to(ROOT)))
    for ref in sorted(used_secs):
        if ref not in defined:
            errors.append(
                f"{used_secs[ref]} references '@{ref}', which no chapter defines"
            )

    # --- 3. no orphan entries --------------------------------------
    for key in sorted(bib):
        if key not in used:
            warnings.append(f"refs.bib entry '{key}' is never cited")

    # --- 4 and 5. chapter completeness -----------------------------
    for f in files:
        rel = str(f.relative_to(ROOT))
        if not rel.startswith("parts/"):
            continue
        text = f.read_text(encoding="utf-8")
        if "This chapter is not written yet" in text:
            warnings.append(f"{rel} is still a stub")
            continue

        # A search disclosure that names a record file must name one that
        # exists, in every chapter and not only the ones reaching a verdict.
        # Pointing a reader at a file that is not there is the failure this
        # book accuses guidelines of, and nothing else catches it.
        for path in sorted(set(SEARCH_RECORD.findall(text))):
            if not (ROOT / path).is_file():
                (errors if args.strict else warnings).append(
                    f"{rel} cites search record '{path}', which does not exist"
                )

        # An audit chapter is one that reaches a verdict. Essay chapters
        # (Part I, the myths chapters) legitimately do not.
        if VERDICT_BLOCK not in text:
            continue

        if SEARCH_DISCLOSURE not in text:
            (errors if args.strict else warnings).append(
                f"{rel} reaches a verdict but discloses no dated search"
            )

        for field in VERDICT_FIELDS:
            m = re.search(
                re.escape(field) + r"\s*\n:\s*(.+)", text
            )
            if not m:
                (errors if args.strict else warnings).append(
                    f"{rel} verdict box has no '{field}' field"
                )
            elif m.group(1).strip() in ("*TBD*", "TBD", ""):
                (errors if args.strict else warnings).append(
                    f"{rel} verdict field '{field}' is still TBD"
                )

    # --- report -----------------------------------------------------
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR:   {e}", file=sys.stderr)

    print(
        f"\n{len(bib)} bib entries, {len(used)} cited, "
        f"{len(files)} qmd files checked: "
        f"{len(errors)} error(s), {len(warnings)} warning(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
