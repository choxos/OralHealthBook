#!/usr/bin/env python3
"""Extract every DBOH 2025 recommendation into machine-readable form.

This builds the book's spine. Chapter 2 of Delivering Better Oral Health
carries the recommendations and their strength labels; chapter 13 carries
the evidence statement and certainty rating behind each one. This script
parses both, joins them on the recommendation text, and writes:

    appraisals/dboh-2025.csv             one row per recommendation
    appraisals/dboh-2025-references.csv  the chapter 13 reference list
    appraisals/dboh-2025-unmatched.csv   rows that failed to join

Two derived columns do real work.

`n_components` counts the separable instructions inside a single
recommendation, by counting its bullets. This measures the book's central
argument directly: DBOH states that when a recommendation covers multiple
components it takes its strength "on the main component", so a Strong
label on a five-bullet recommendation tells the reader nothing about which
bullet earned it.

`certainty_terms` pulls every certainty phrase out of the evidence
statement. Where a Strong recommendation's own evidence statement contains
the words "low certainty", that is the guideline documenting the gap in
its own words, and it is the strongest material the book has.

Source: Delivering Better Oral Health, updated 10 September 2025.
Crown copyright, reproduced under the Open Government Licence v3.0.
"""

from __future__ import annotations

import csv
import re
import statistics
import sys
from difflib import SequenceMatcher
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "Books" / "DBOH_UK"
OUT = ROOT / "appraisals"

CH2 = SRC / "Chapter 2_ summary guidance tables for dental teams - GOV.UK.html"
CH13 = (
    SRC
    / "Chapter 13_ evidence base for recommendations in the summary guidance "
      "tables - GOV.UK.html"
)

STRENGTHS = ("Strong", "Conditional", "Good practice")

# Certainty phrases as DBOH words them. Order matters: "very low" must be
# tried before "low" or it gets swallowed.
CERTAINTY_PAT = re.compile(
    r"\b(very low|high|moderate|low)[- ]certainty\b"
    r"|\b(very low|high|moderate|low)\s+certainty\b",
    re.I,
)

# Which chapter-2 table belongs to which disease domain, taken from the
# chapter's own section headings.
DOMAIN_BY_TABLE = {
    "1": "dental caries",
    "2": "periodontal diseases",
    "3": "oral cancer",
    "4": "tooth wear",
}


# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------

def load(path: Path) -> Tag:
    if not path.exists():
        sys.exit(f"Not found: {path}\nExpected the archived DBOH pages under sources/.")
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    main = soup.find("main") or soup
    for junk in main(["script", "style"]):
        junk.decompose()
    return main


def cell_text(cell: Tag) -> str:
    """Readable text from a table cell.

    GOV.UK marks list items with a literal bullet and wraps abbreviations
    in <abbr>. Keep the bullets (n_components counts them) and unwrap the
    abbreviations to their short form, which is how the guideline reads
    on the page.
    """
    for br in cell.find_all("br"):
        br.replace_with("\n")
    for sup in cell.find_all("sup"):
        sup.decompose()  # footnote markers are captured separately
    txt = cell.get_text(" ", strip=False)
    txt = txt.replace("\xa0", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*", "\n", txt)
    return txt.strip()


def footnote_ids(cell: Tag) -> list[str]:
    out: list[str] = []
    for sup in cell.find_all("sup"):
        m = re.match(r"fnref:(\d+)", sup.get("id", "") or "")
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def table_caption(table: Tag) -> str:
    for prev in table.find_all_previous(["h2", "h3", "h4", "p"]):
        txt = prev.get_text(" ", strip=True).replace("\xa0", " ")
        if txt.lower().startswith("table"):
            return txt
    return ""


def normalise(text: str) -> str:
    """Aggressive normalisation for joining chapter 2 to chapter 13.

    The two chapters do not always word a recommendation identically, so
    the join collapses case, punctuation, bullets and whitespace. Rows
    that still fail to join are written to the unmatched file rather than
    silently dropped, because a wording difference between the advice
    table and the evidence table is itself worth a look.
    """
    t = text.lower()
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = re.sub(r"\bppm\s*fluoride\b", "ppm", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def count_components(rec: str) -> int:
    """How many separable instructions this recommendation contains."""
    bullets = len(re.findall(r"^\s*[•\-•]", rec, re.M))
    return max(bullets, 1)


def certainty_terms(evidence: str) -> list[str]:
    seen: list[str] = []
    for m in CERTAINTY_PAT.finditer(evidence):
        term = (m.group(1) or m.group(2)).lower()
        if term not in seen:
            seen.append(term)
    return seen


def split_strength(cell: str) -> tuple[str, str]:
    """Chapter 13's evidence cell starts with the strength label."""
    for s in STRENGTHS:
        if cell.lower().startswith(s.lower()):
            return s, cell[len(s):].strip()
    return "", cell.strip()


# Confident enough to merge without review; below this but above MATCH_FUZZY
# the row is merged and flagged so a human can look at it.
MATCH_STRONG = 0.90
MATCH_FUZZY = 0.72

# Joins below MATCH_STRONG that have been checked by hand, so a re-run does
# not re-raise them. Recorded here rather than in a side file because the
# judgment belongs next to the rule that produced it.
#
# Checked 2026-08-15 against DBOH 2025:
#   DBOH-051  orthodontic plaque control. Chapter 13 gives it a Good practice
#             row with no evidence text, so there is nothing to disagree with.
#   DBOH-053  brushing the gum line twice daily, joined to "very low-certainty
#             evidence that infrequent brushing is associated with
#             periodontitis". Correct, and note the evidence is about
#             INFREQUENT brushing, not about the gum line or the timing.
#   DBOH-066  tobacco ask/advise/act, joined to "moderate certainty evidence
#             that interventions for smoking cessation improve periodontal
#             health". Correct.
REVIEWED_JOINS = {"DBOH-051", "DBOH-053", "DBOH-066"}

# Chapter 2 recommendations with no chapter 13 counterpart at all.
#
#   DBOH-069  "Some medications can affect gingival health" points the reader
#             at the BNF instead of at evidence. A real gap in the guideline's
#             cross-referencing.
#
# DBOH-087, the tooth wear brushing row, used to be listed here and should not
# have been. It DOES have a chapter 13 counterpart, in table 21, and that
# counterpart carries the most interesting sentence in the guideline for this
# book's argument: "Good practice for preventing tooth wear. Strong
# recommendation for preventing dental caries and conditional for periodontal
# disease." The join scored 0.44 because chapter 2 spells the advice out while
# chapter 13 words it slightly differently, and marking it unmatched hid the
# sentence. A chapter was then written from this file rather than from the
# guideline, and got the fact backwards.
#
# The lesson is the one the book is about, so the fix is not to special-case
# the row but to make a silent drop impossible: anything that lands between
# MATCH_FUZZY and a confident join, or fails to join at all, is written to the
# unmatched CSV and must be signed off in REVIEWED_JOINS or here by hand.
KNOWN_UNMATCHED = {"DBOH-069"}

# Joins recovered by hand after the automatic matcher missed them. Keyed to the
# chapter 13 table they belong to, so the CSV can carry the evidence text even
# where the fuzzy score was too low to trust on its own.
MANUAL_JOINS = {
    "DBOH-087": 21,
}


def best_match(key: str, index: dict[str, list[dict]]) -> tuple[dict | None, float]:
    """Join chapter 2 to chapter 13 on recommendation text.

    The two chapters do not word every recommendation identically ("Minimise
    the amount and frequency..." against "Minimise amount and frequency..."),
    so an exact key lookup loses real matches. Score every candidate and keep
    the best, recording the score so a weak join is visible rather than
    silently trusted.
    """
    if key in index:
        return index[key][0], 1.0

    best: dict | None = None
    best_score = 0.0
    for k, rows in index.items():
        if not k:
            continue
        score = SequenceMatcher(None, key, k).ratio()
        if score > best_score:
            best, best_score = rows[0], score

    if best_score >= MATCH_FUZZY:
        return best, best_score
    return None, best_score


# ---------------------------------------------------------------------
# chapter 2: the recommendations
# ---------------------------------------------------------------------

def parse_ch2(main: Tag) -> list[dict]:
    rows: list[dict] = []
    for table in main.find_all("table"):
        cap = table_caption(table)
        m = re.match(r"table\s+(\d+)([a-z]?)\s*:?\s*(.*)", cap, re.I)
        if not m:
            continue
        group, letter, title = m.group(1), m.group(2), m.group(3)

        trs = table.find_all("tr")
        if not trs:
            continue
        header = [c.get_text(" ", strip=True) for c in trs[0].find_all(["th", "td"])]

        for tr in trs[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            texts = [cell_text(c) for c in cells]

            # Column layouts vary: 4 cols on the periodontitis-risk table
            # (leading "Risk"), 3 on most, 2 where there is no type column.
            risk = ""
            if header[:1] == ["Risk"] and len(texts) >= 4:
                risk, rec_type, rec, strength = texts[0], texts[1], texts[2], texts[3]
            elif len(texts) >= 3:
                rec_type, rec, strength = texts[0], texts[1], texts[2]
            else:
                rec_type, rec, strength = "", texts[0], texts[1]

            if not rec.strip():
                continue

            rows.append({
                "domain": DOMAIN_BY_TABLE.get(group, ""),
                "ch2_table": f"{group}{letter}",
                "ch2_table_title": title,
                "risk_factor": risk,
                "rec_type": rec_type,
                "recommendation": rec,
                "strength": strength.strip(),
                "n_components": count_components(rec),
            })
    return rows


# ---------------------------------------------------------------------
# chapter 13: the evidence base
# ---------------------------------------------------------------------

def parse_ch13(main: Tag) -> tuple[list[dict], dict[str, dict]]:
    rows: list[dict] = []
    for table in main.find_all("table"):
        cap = table_caption(table)
        m = re.match(r"table\s+(\d+)\s*:?\s*(.*)", cap, re.I)
        if not m:
            continue
        num, title = m.group(1), m.group(2)

        trs = table.find_all("tr")
        for tr in trs[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            rec = cell_text(cells[1])
            ev_cell = cells[2]
            # Read the footnote markers BEFORE cell_text(), which strips
            # the <sup> elements they live in.
            fns = footnote_ids(ev_cell)
            strength13, evidence = split_strength(cell_text(ev_cell))
            if not rec.strip():
                continue
            rows.append({
                "ch13_table": num,
                "ch13_table_title": title,
                "recommendation": rec,
                "strength_ch13": strength13,
                "evidence_base": evidence,
                "certainty_terms": certainty_terms(evidence),
                "footnotes": fns,
            })

    refs: dict[str, dict] = {}
    fdiv = main.find("div", class_="footnotes")
    if fdiv:
        for li in fdiv.find_all("li"):
            fid = re.match(r"fn:(\d+)", li.get("id", "") or "")
            if not fid:
                continue
            for back in li.find_all("a", class_="reversefootnote"):
                back.decompose()
            link = li.find("a", href=True)
            text = re.sub(r"\s+", " ", li.get_text(" ", strip=True)).strip(" .↩")
            refs[fid.group(1)] = {
                "n": fid.group(1),
                "citation": text,
                "url": link["href"] if link else "",
            }
    return rows, refs


# ---------------------------------------------------------------------
# join and write
# ---------------------------------------------------------------------

def main() -> int:
    ch2_rows = parse_ch2(load(CH2))
    ch13_rows, refs = parse_ch13(load(CH13))

    index: dict[str, list[dict]] = {}
    for r in ch13_rows:
        index.setdefault(normalise(r["recommendation"]), []).append(r)

    OUT.mkdir(parents=True, exist_ok=True)
    merged: list[dict] = []
    unmatched: list[dict] = []
    used: set[int] = set()

    # chapter 13 rows, flattened once so a manual join can find one by table
    ch13_by_table: dict[int, list[dict]] = {}
    for cands in index.values():
        for c in cands:
            # ch13_table comes off a regex group, so it is a string; key on
            # str() so MANUAL_JOINS can be written with plain integers.
            ch13_by_table.setdefault(str(c["ch13_table"]), []).append(c)

    for i, rec in enumerate(ch2_rows, start=1):
        rid = f"DBOH-{i:03d}"
        key = normalise(rec["recommendation"])
        ev, score = best_match(key, index)

        # A row the matcher cannot reach, joined by hand to a named chapter 13
        # table. Only ever used for ids listed in MANUAL_JOINS, and only when
        # the automatic match failed, so it cannot silently override a real one.
        if ev is None and rid in MANUAL_JOINS:
            cands = ch13_by_table.get(str(MANUAL_JOINS[rid]), [])
            if cands:
                ev = max(cands, key=lambda c: len(c["evidence_base"] or ""))
                score = -1.0        # marks a hand join in the audit column

        if ev is not None:
            used.add(id(ev))

        row = {
            "id": f"DBOH-{i:03d}",
            "domain": rec["domain"],
            "ch2_table": rec["ch2_table"],
            "population": rec["ch2_table_title"],
            "risk_factor": rec["risk_factor"],
            "rec_type": rec["rec_type"],
            "recommendation": rec["recommendation"].replace("\n", " | "),
            "strength": rec["strength"],
            "n_components": rec["n_components"],
            "ch13_table": ev["ch13_table"] if ev else "",
            "strength_ch13": ev["strength_ch13"] if ev else "",
            "evidence_base": (ev["evidence_base"].replace("\n", " ") if ev else ""),
            "certainty_terms": "; ".join(ev["certainty_terms"]) if ev else "",
            # The weakest certainty term appearing ANYWHERE in the evidence
            # statement. Not the certainty the recommendation rests on: the
            # statement often rates several components, and sometimes rates a
            # harm signal rather than the benefit. It marks a statement worth
            # reading. The adjudicated value goes in our_certainty, by hand.
            "weakest_certainty_mentioned": (
                _lowest(ev["certainty_terms"]) if ev and ev["certainty_terms"] else ""
            ),
            "footnotes": ";".join(ev["footnotes"]) if ev else "",
            "references": (
                " || ".join(
                    refs.get(f, {}).get("citation", f"[unresolved footnote {f}]")
                    for f in ev["footnotes"]
                )
                if ev else ""
            ),
            "strength_matches_ch13": (
                "" if not ev or not ev["strength_ch13"]
                else str(ev["strength_ch13"].lower() == rec["strength"].lower())
            ),
            "matched": "yes" if ev else "NO",
            "match_score": f"{score:.2f}",
            "match_needs_review": (
                "yes"
                if ev and score < MATCH_STRONG and f"DBOH-{i:03d}" not in REVIEWED_JOINS
                else ""
            ),
            "join_note": (
                "joined by hand" if score == -1.0
                else "checked by hand" if f"DBOH-{i:03d}" in REVIEWED_JOINS
                else "no chapter 13 counterpart"
                if f"DBOH-{i:03d}" in KNOWN_UNMATCHED else ""
            ),
            # Filled in by hand as each chapter is audited.
            "audited_in_chapter": "",
            "directness": "",
            "our_certainty": "",
            "verdict": "",
            "search_date": "",
        }
        merged.append(row)
        if not ev:
            unmatched.append(row)

    orphans = [r for r in ch13_rows if id(r) not in used]

    _write_csv(OUT / "dboh-2025.csv", merged)
    _write_csv(
        OUT / "dboh-2025-references.csv",
        [refs[k] for k in sorted(refs, key=int)],
    )
    _write_csv(OUT / "dboh-2025-unmatched.csv", unmatched)
    _write_variables(merged, refs)

    # --- report ------------------------------------------------------
    strong = [r for r in merged if r["strength"].lower().startswith("strong")]
    bundled_strong = [r for r in strong if r["n_components"] > 1]
    strong_with_low = [
        r for r in strong
        if r["weakest_certainty_mentioned"] in ("low", "very low")
    ]
    review = [r for r in merged if r["match_needs_review"]]
    surprises = [
        r for r in unmatched if r["id"] not in KNOWN_UNMATCHED
    ]

    print(f"chapter 2  : {len(ch2_rows)} recommendations")
    print(f"chapter 13 : {len(ch13_rows)} evidence rows, {len(refs)} references")
    print(f"joined     : {len(merged) - len(unmatched)}/{len(merged)}"
          f"  ({len(unmatched)} unmatched, {len(orphans)} ch13 orphans,"
          f" {len(review)} fuzzy joins to review)")
    if surprises:
        print("  ! new unmatched rows, not in KNOWN_UNMATCHED:")
        for r in surprises:
            print(f"    [{r['id']}] {r['recommendation'][:70]}")
    print()
    print(f"Strong recommendations              : {len(strong)}")
    print(f"  ...that bundle 2+ components      : {len(bundled_strong)}")
    print(f"  ...whose own evidence statement")
    print(f"     says low or very low certainty : {len(strong_with_low)}")
    print()
    print("Strong recommendations whose own evidence statement concedes")
    print("low or very low certainty for at least one component:")
    for r in strong_with_low:
        head = r["recommendation"].split(" | ")[0][:60]
        print(f"  [{r['id']}] {r['weakest_certainty_mentioned']:8} "
              f"{r['n_components']}c  {head}")

    print(f"\nwrote {OUT.relative_to(ROOT)}/dboh-2025.csv and 2 companions")
    return 0


# The year DBOH's audited edition was published. Citation ages are measured
# against this, not against today, so the figures describe how current the
# guideline was at the moment it was published rather than how current it is now.
EDITION_YEAR = 2025

# Publication years only: 1950 to 2029. Narrow enough that DOI fragments
# ("10.1002/14651858.CD008286.pub3") and volume/page numbers cannot match.
_YEAR = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")


def _citation_ages(rows: list[dict]) -> list[int]:
    """Age, in years at EDITION_YEAR, of the newest citation on each row.

    A recommendation is only as current as its most recent support, so this
    takes the maximum year per row and ignores the older references beneath
    it. "2008 [updated 2018]" resolves to 2018 for the same reason.

    This is a lower bound on staleness twice over: a review published in
    2013 closed its own search before 2013, and rows citing no dated source
    at all are excluded rather than counted as infinitely old.
    """
    ages = []
    for r in rows:
        years = [int(y) for y in _YEAR.findall(r.get("references") or "")]
        if years:
            ages.append(EDITION_YEAR - max(years))
    return ages


def _write_variables(rows: list[dict], refs: dict[str, dict]) -> None:
    """Write _variables.yml so the book never hand-types a count.

    Chapters cite these as {{< var dboh.strong >}}. If DBOH is updated and
    the extractor re-run, every number in the text moves with it. A book
    about other people's citation discipline cannot have a stale figure
    typed into a sentence.
    """
    def n(pred) -> int:
        return sum(1 for r in rows if pred(r))

    ages = _citation_ages(rows)
    strong = [r for r in rows if r["strength"] == "Strong"]
    good = [r for r in rows if r["strength"].startswith("Good practice")]

    biggest = max(rows, key=lambda r: int(r["n_components"]))
    biggest_strong = max(strong, key=lambda r: int(r["n_components"]))

    lines = [
        "# GENERATED by scripts/extract_dboh.py. Do not edit by hand.",
        "# Counts taken from Delivering Better Oral Health, 10 September 2025.",
        "dboh:",
        f"  edition: \"10 September 2025\"",
        f"  total: {len(rows)}",
        f"  strong: {len(strong)}",
        f"  conditional: {n(lambda r: r['strength'] == 'Conditional')}",
        f"  goodpractice: {len(good)}",
        f"  references: {len(refs)}",
        "  # Recommendations bundling two or more separable instructions",
        f"  bundled: {n(lambda r: int(r['n_components']) > 1)}",
        f"  bundled_strong: {sum(1 for r in strong if int(r['n_components']) > 1)}",
        f"  largest_bundle: {biggest['n_components']}",
        f"  largest_strong_bundle: {biggest_strong['n_components']}",
        f"  largest_strong_bundle_id: {biggest_strong['id']}",
        "  # Recommendations whose evidence statement names no certainty at all",
        f"  no_certainty_stated: {n(lambda r: not r['certainty_terms'])}",
        "  # Good practice points, which by definition have no research behind them",
        f"  goodpractice_with_evidence: "
        f"{sum(1 for r in good if r['evidence_base'].strip())}",
        "  # Strong recommendations conceding low or very low certainty",
        "  # for at least one of their components",
        f"  strong_conceding_low: "
        f"{sum(1 for r in strong if r['weakest_certainty_mentioned'] in ('low', 'very low'))}",
        "  # Join quality between chapter 2 and chapter 13",
        f"  joined: {n(lambda r: r['matched'] == 'yes')}",
        f"  unjoined: {n(lambda r: r['matched'] == 'NO')}",
        "  # Age of the newest citation supporting each recommendation, in",
        "  # years at the edition's own publication date. See _citation_ages.",
        f"  dated: {len(ages)}",
        f"  age_median: {int(statistics.median(ages))}",
        f"  age_max: {max(ages)}",
        f"  age_5plus: {sum(1 for a in ages if a >= 5)}",
        f"  age_10plus: {sum(1 for a in ages if a >= 10)}",
        f"  age_same_year: {sum(1 for a in ages if a == 0)}",
        f"  age_undated: {len(rows) - len(ages)}",
        "  # The publication year a median-aged recommendation rests on, so the",
        "  # prose never hard-codes an arithmetic result of the two above.",
        f"  age_median_year: {EDITION_YEAR - int(statistics.median(ages))}",
    ]
    (ROOT / "_variables.yml").write_text("\n".join(lines) + "\n")


def _lowest(terms: list[str]) -> str:
    order = ["very low", "low", "moderate", "high"]
    present = [t for t in order if t in terms]
    return present[0] if present else ""


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
