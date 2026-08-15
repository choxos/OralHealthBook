#!/usr/bin/env python3
"""Generate chapter skeletons.

Every audit chapter in Parts II to IV follows the same seven-step
structure, which is what makes this a book rather than a collection of
blog posts. This writes that structure once so the chapters cannot
drift apart from each other.

Run once. It refuses to overwrite a file that already has content
beyond the skeleton, so it is safe to re-run after chapters are drafted.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

# (path, section-id, title, kind)
#   kind "audit"  -> full seven-step recommendation audit
#   kind "essay"  -> argued chapter, no single recommendation to audit
CHAPTERS = [
    # Part I -----------------------------------------------------------
    ("parts/01-method/01-why-audit.qmd", "sec-why-audit",
     "Why I audit dental advice", "essay"),
    ("parts/01-method/02-certainty-is-not-strength.qmd", "sec-certainty-strength",
     "Certainty is not strength", "essay"),
    ("parts/01-method/03-the-bundling-problem.qmd", "sec-bundling",
     "The bundling problem", "essay"),
    ("parts/01-method/04-how-i-did-this.qmd", "sec-method",
     "How I did this", "essay"),

    # Part II ----------------------------------------------------------
    ("parts/02-caries/05-brush-twice-daily.qmd", "sec-twice-daily",
     "Brush twice daily", "audit"),
    ("parts/02-caries/06-last-thing-at-night.qmd", "sec-last-thing",
     "Brush last thing at night", "audit"),
    ("parts/02-caries/07-spit-dont-rinse.qmd", "sec-spit",
     "Spit, don't rinse", "audit"),
    ("parts/02-caries/08-how-much-fluoride.qmd", "sec-ppm",
     "How much fluoride should be in your toothpaste?", "audit"),
    ("parts/02-caries/09-how-much-toothpaste.qmd", "sec-amount",
     "How much toothpaste, and does fluorosis matter?", "audit"),
    ("parts/02-caries/10-fluoride-varnish.qmd", "sec-varnish",
     "Fluoride varnish twice a year", "audit"),
    ("parts/02-caries/11-fissure-sealants.qmd", "sec-sealants",
     "Fissure sealants", "audit"),
    ("parts/02-caries/12-fluoride-mouth-rinse.qmd", "sec-rinse",
     "Fluoride mouth rinse", "audit"),
    ("parts/02-caries/13-sugar.qmd", "sec-sugar",
     "Sugar: how much is too much?", "audit"),
    ("parts/02-caries/14-breastfeeding.qmd", "sec-breastfeeding",
     "Breastfeeding and decay", "audit"),
    ("parts/02-caries/15-the-quieter-tier.qmd", "sec-quieter-tier",
     "The quieter tier: supervised brushing, sugar-free medicines, bedtime sugar",
     "audit"),

    # Part III ---------------------------------------------------------
    ("parts/03-gums/16-manual-or-powered.qmd", "sec-powered",
     "Manual or powered?", "audit"),
    ("parts/03-gums/17-flossing.qmd", "sec-flossing",
     "Flossing, and what replaced it", "audit"),
    ("parts/03-gums/18-toothbrush-design.qmd", "sec-brush-design",
     "Bristles, heads, and the two-minute rule", "audit"),
    ("parts/03-gums/19-scale-and-polish.qmd", "sec-scale-polish",
     "Scale, polish, and being told what to do", "audit"),

    # Part IV ----------------------------------------------------------
    ("parts/04-cancer-wear/20-oral-cancer-screening.qmd", "sec-cancer-screening",
     "Looking for oral cancer, and the tests you are told not to use", "audit"),
    ("parts/04-cancer-wear/21-tobacco.qmd", "sec-tobacco",
     "Tobacco: what a strong recommendation looks like", "audit"),
    ("parts/04-cancer-wear/22-alcohol.qmd", "sec-alcohol",
     "Alcohol, AUDIT-C, and the fourteen-unit line", "audit"),
    ("parts/04-cancer-wear/23-tooth-wear.qmd", "sec-wear",
     "Erosion, wear, and the acid myth", "audit"),

    # Part V -----------------------------------------------------------
    ("parts/05-questions/24-fluoridation-does-it-work.qmd", "sec-fluoridation-works",
     "Does water fluoridation work?", "audit"),
    ("parts/05-questions/25-fluoridation-is-it-harmful.qmd", "sec-fluoridation-harm",
     "Is water fluoridation harmful?", "audit"),
    ("parts/05-questions/26-filling-childrens-teeth.qmd", "sec-fiction",
     "Should children's baby teeth be filled?", "audit"),
    ("parts/05-questions/27-bad-breath.qmd", "sec-halitosis",
     "Bad breath", "audit"),
    ("parts/05-questions/28-six-month-checkup.qmd", "sec-recall",
     "Do you need a check-up every six months?", "audit"),
    ("parts/05-questions/29-the-toothpaste-aisle.qmd", "sec-aisle",
     "The toothpaste aisle", "essay"),
    ("parts/05-questions/30-short-answers.qmd", "sec-short-answers",
     "Short answers", "essay"),

    # Part VI ----------------------------------------------------------
    ("parts/06-anyway/31-what-i-actually-do.qmd", "sec-what-i-do",
     "What I actually do, and why", "essay"),
    ("parts/06-anyway/32-how-research-should-change.qmd", "sec-research",
     "How dental research should change", "essay"),
]

APPENDICES = [
    ("appendices/a-evidence-tables.qmd", "sec-app-evidence",
     "Evidence tables"),
    ("appendices/b-search-strategies.qmd", "sec-app-searches",
     "Search strategies"),
    ("appendices/c-appraisal-tools.qmd", "sec-app-tools",
     "The appraisal tools, and why each one"),
    ("appendices/d-glossary.qmd", "sec-app-glossary",
     "Glossary"),
]

AUDIT_BODY = """
::: {.callout-warning title="Draft"}
This chapter is not written yet. The skeleton below is the fixed
seven-step structure every audit chapter follows.
:::

## The advice

> *Quote the recommendation verbatim from DBOH 2025, chapter 2, with its
> strength label and the table it appears in.*

## What the guideline says its evidence is

> *Quote the matching row from DBOH 2025, chapter 13, with its certainty
> rating and cited reference.*

## Following the citation

*Read the cited source. Does it answer the question the advice asks?
Population, intervention, comparator, outcome, one at a time.*

## Appraising it

::: {.callout-note title="How I judged this" collapse="true"}
*Risk of bias, review quality, GRADE domains. Show the judgments, not
just the conclusion.*

::: {.content-visible when-profile="print"}
*The full domain-by-domain judgments are in @sec-app-evidence.*
:::

::: {.content-visible when-profile="web"}
*The full domain-by-domain judgments are in
[`appraisals/`](https://github.com/choxos/OralHealthBook/tree/main/appraisals).*
:::
:::

## Is there better evidence?

::: {.callout-note title="What I searched, and when" collapse="true"}
*Database, date, hits, what was screened in.*

::: {.content-visible when-profile="print"}
*The full search strategy is in @sec-app-searches.*
:::

::: {.content-visible when-profile="web"}
*The full search strategy is in
[`appraisals/searches/`](https://github.com/choxos/OralHealthBook/tree/main/appraisals/searches).*
:::
:::

## Verdict

::: {.verdict}
[Verdict]{.verdict-title}

Certainty of evidence
:   *TBD*

Directness to the advice as worded
:   *TBD*

Is the strength label defensible?
:   *TBD*

What would change my mind
:   *TBD*
:::

## What this means for you

*One paragraph. Plain language. No jargon, no hedging beyond what is
honest.*
"""

ESSAY_BODY = """
::: {.callout-warning title="Draft"}
This chapter is not written yet.
:::
"""


def build(sid: str, title: str, kind: str) -> str:
    body = AUDIT_BODY if kind == "audit" else ESSAY_BODY
    return f"# {title} {{#{sid}}}\n" + body


def build_appendix(sid: str, title: str) -> str:
    return (
        f"# {title} {{#{sid}}}\n\n"
        '::: {.callout-warning title="Draft"}\n'
        "This appendix is generated from `appraisals/` at build time.\n"
        ":::\n"
    )


def main() -> int:
    written, skipped = 0, 0
    for rel, sid, title, kind in CHAPTERS:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and "This chapter is not written yet" not in p.read_text():
            skipped += 1
            continue
        p.write_text(build(sid, title, kind))
        written += 1

    for rel, sid, title in APPENDICES:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and "generated from `appraisals/`" not in p.read_text():
            skipped += 1
            continue
        p.write_text(build_appendix(sid, title))
        written += 1

    print(f"wrote {written}, left {skipped} drafted file(s) alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
