# Appraisal data

Every claim the book makes about *Delivering Better Oral Health* traces to a
row in here. The book asks readers not to take a guideline's word for what its
evidence says; it would be indefensible to then ask readers to take the book's
word for what the guideline says.

Regenerate with:

```bash
python3 scripts/extract_dboh.py
```

Source: *Delivering Better Oral Health*, updated 10 September 2025. Crown
copyright, reproduced under the [Open Government Licence v3.0][ogl].

## Files

| File | What it is |
|---|---|
| `dboh-2025.csv` | One row per recommendation. The spine of the book. |
| `dboh-2025-references.csv` | The 58 numbered references from chapter 13. |
| `dboh-2025-unmatched.csv` | Chapter 2 rows with no chapter 13 counterpart. |

## `dboh-2025.csv` columns

### Extracted from the guideline

| Column | Source |
|---|---|
| `id` | `DBOH-001`…`DBOH-091`, assigned in chapter 2 reading order |
| `domain` | caries, periodontal diseases, oral cancer, tooth wear |
| `ch2_table` | e.g. `1a`, the chapter 2 table it appears in |
| `population` | that table's title, i.e. who the advice is for |
| `risk_factor` | only on table 2d, which is organised by risk |
| `rec_type` | Advice, Professional intervention, or a VBA step |
| `recommendation` | the wording, verbatim. Bullets become ` \| ` |
| `strength` | Strong, Conditional, Good practice, as chapter 2 gives it |
| `ch13_table` | the chapter 13 table its evidence statement is in |
| `strength_ch13` | the strength as chapter 13 repeats it |
| `evidence_base` | chapter 13's evidence statement, verbatim |
| `footnotes` | chapter 13 footnote numbers cited in that statement |
| `references` | those footnotes resolved to their citations |

### Derived

| Column | Meaning |
|---|---|
| `n_components` | **Separable instructions in one recommendation**, by bullet count. This is the book's central argument made countable. |
| `certainty_terms` | Every certainty phrase in the evidence statement, in order. |
| `weakest_certainty_mentioned` | The weakest of those terms. **Read the caveat below.** |
| `strength_matches_ch13` | Whether chapter 2 and chapter 13 agree on the strength. |
| `matched`, `match_score` | Join quality between the two chapters. |
| `match_needs_review` | Fuzzy join not yet checked by a human. Should be empty. |
| `join_note` | Why a hand-checked or known-unmatched row is as it is. |

### Filled in by hand, as each chapter is written

`audited_in_chapter`, `directness`, `our_certainty`, `verdict`, `search_date`.

**These are empty, in every row, as the manuscript stands.** They were designed
as a machine-readable ledger of the book's own adjudications and that ledger has
not been built. The judgments themselves exist, in the Verdict box of each audit
chapter, in prose. What does not exist is a keyed table linking each one to its
recommendation, so nothing here should be described as a completed appraisal
archive, and the preface says so too.

`our_certainty` is intended to hold the adjudicated judgment;
`weakest_certainty_mentioned` is only a flag for where to look. Until the former
is populated, the book's certainty judgments are the ones written in the chapters,
and this file is an extraction of the guideline rather than a record of the
audit.

## Two caveats that matter

**`weakest_certainty_mentioned` is not the certainty the recommendation rests
on.** An evidence statement often rates several things at once. The
breastfeeding row reads "low certainty evidence of a dental caries-preventive
effect" and separately "very low certainty evidence of increase in dental
caries risk beyond 12 months breastfeeding"; the second is a *harm* signal, not
the basis of the advice. Taking the minimum across a statement is a way of
finding rows worth reading, not a verdict. The verdict goes in `our_certainty`,
by hand, with reasons.

**`n_components` counts bullets, not ideas.** A recommendation written as
flowing prose can bundle just as much as a bulleted one, and will score 1 here.
The count is a floor on how much is bundled, never a ceiling.

## What the data shows

Regenerating prints a summary. As of the 10 September 2025 edition:

- **91** recommendations: 28 Strong, 28 Conditional, 34 Good practice, and one
  whose strength column says only "Refer to British National Formulary".
- **16** bundle two or more separable instructions; **7** of those are Strong.
- The largest Strong bundle is **DBOH-009**, six instructions under one label:
  brush all tooth surfaces, at least twice a day, last thing at night and once
  more, with 1,000ppm+ fluoride toothpaste, a pea-sized amount, spitting rather
  than rinsing. Chapter 13 rates its components from moderate down to low, and
  calls the evidence for the pea-sized amount "inconclusive".
- **39** of the 91 evidence statements name no certainty level at all.
- Of 34 Good practice points, **14** carry an evidence statement anyway, which
  sits oddly with the guideline's own definition of the category.

None of these numbers is typed into the manuscript. They are written to
`_variables.yml` and cited in the text as `{{< var dboh.strong >}}`, so if the
guideline is updated and the extractor re-run, the prose moves with the data.

[ogl]: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
