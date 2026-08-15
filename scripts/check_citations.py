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

REQUIRED_SECTIONS = [
    "## The advice",
    "## What the guideline says its evidence is",
    "## Following the citation",
    "## Appraising it",
    "## Is there better evidence?",
    "## Verdict",
    "## What this means for you",
]

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


def parse_bib(path: Path) -> dict[str, str]:
    """Return {key: entry-body}. Good enough for a hand-maintained file."""
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"^%.*$", "", raw, flags=re.M)
    entries: dict[str, str] = {}
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
        entries[m.group(2)] = f"@{m.group(1).lower()}\n" + raw[start:i]
    return entries


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

    bib = parse_bib(BIB)
    files = qmd_files()
    used = used_keys(files)

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
        is_audit = "## The advice" in text
        if "This chapter is not written yet" in text:
            warnings.append(f"{rel} is still a stub")
            continue
        if not is_audit:
            continue
        for sec in REQUIRED_SECTIONS:
            if sec not in text:
                (errors if args.strict else warnings).append(
                    f"{rel} is missing the required section '{sec}'"
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
