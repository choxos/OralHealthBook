# Chapter 32: when was this last checked?

**Database:** PubMed
**Date run:** 20 August 2026; corrected and extended 8 September 2026

## Provenance

Unlike the Part II to Part V records, this one was written **at the same time as
the chapter** rather than reconstructed afterwards from a chapter's disclosure.
The searches below were run while drafting.

## Query 1: the version history of CD010216

The chapter's central example is DBOH-074, the e-cigarette recommendation, which
cites `CD010216.pub3`.

```
Electronic cigarettes for smoking cessation[Title] AND Cochrane Database Syst Rev[Journal]
```

**24 records.** Sorted by publication date. A second, narrower query:

```
Hartmann-Boyce[Author] AND Electronic cigarettes for smoking cessation[Title]
```

**19 records.**

Metadata retrieved and structured abstracts read for four versions:

| Version | PMID | Published | Search closed | Studies | Participants | RCTs |
|---|---|---|---|---:|---:|---:|
| `.pub3` | 27622384 | 14 Sep 2016 | Jan 2016 | 24 | 662 in the cessation MA | 3 |
| `.pub8` | 38189560 | 8 Jan 2024 | 1 Jul 2023 | 88 | 27,235 | 47 |
| `.pub9` | 39878158 | 29 Jan 2025 | 1 Feb 2024 | 90 | 29,044 | 49 |
| `.pub10` | 41212103 | 10 Nov 2025 | 1 Mar 2025 | 104 | 30,366 | 61 |

`.pub4` through `.pub7` were **not** retrieved. The chapter's phrase "superseded
seven times" is arithmetic on the version numbers, not a claim about four
abstracts I have read, and the chapter says so.

Nicotine EC versus NRT, abstinence at six months or longer:

| Version | RR | 95% CI | I2 | studies | n | certainty |
|---|---|---|---|---:|---:|---|
| `.pub3` | not pooled | - | - | 1 | 584 | very low |
| `.pub8` | 1.59 | 1.29 to 1.93 | 0% | 7 | 2,544 | high |
| `.pub9` | 1.59 | 1.30 to 1.93 | 0% | 7 | 2,544 | high |
| `.pub10` | 1.55 | 1.28 to 1.88 | 0% | 9 | 2,703 | high |

`.pub3` reported nicotine EC versus **placebo EC** at RR 2.29 (95% CI 1.05 to
4.96; 2 studies, 662 participants), GRADE low, and versus nicotine patch at
RR 1.26 (95% CI 0.68 to 2.34; 584 participants), GRADE very low. Its stated
conclusion includes "the long-term safety of ECs is unknown," which is what
DBOH's evidence statement paraphrases.

### The living-review declaration

`.pub8`, `.pub9` and `.pub10` each carry this sentence in the published abstract:

> To ensure the review continues to provide up-to-date information to
> decision-makers, this review is a living systematic review. We run searches
> monthly, with the review updated when relevant new evidence becomes available.

`.pub10` records funding from Cancer Research UK (PICCTR-2024/100012).

**The key date.** The DBOH edition audited in this book was published on
10 September 2025. The current version of CD010216 on that date was `.pub9`,
published 29 January 2025, which reported high certainty. DBOH cites `.pub3`
and reports low certainty.

## Query 2: the living systematic review methods literature

```
Elliott JH[Author] AND living systematic review[Title]
```

**5 records.** PMID 28912002, *J Clin Epidemiol* 2017;91:23-30,
doi:10.1016/j.jclinepi.2017.08.010 is the defining paper and the source of both
quoted phrases in the chapter: the "decay in review currency, accuracy, and
utility," and the three-part triage rule (evidence emerging rapidly, current
evidence uncertain, new research may change decisions).

## Not a search: the citation-age computation

@tbl-citation-age is computed by `scripts/extract_dboh.py`, not searched.

Method: for each of the 91 recommendations, take every 4-digit year in the range
1950 to 2029 appearing in the `references` column, take the **maximum** per row,
and subtract from 2025. Rows with no dated citation are excluded.

Results, written to `_variables.yml`:

| Metric | Value |
|---|---:|
| Recommendations with at least one dated citation | 74 of 91 |
| Median age of newest citation, at publication | 7 years |
| Newest citation 5 years or older | 64 of 74 |
| Newest citation 10 years or older | 16 of 74 |
| Newest citation from the publication year | 1 of 74 |
| Oldest | 13 years (DBOH-076, NICE PH39 2012, Strong) |

**Known limitations, both conservative.**

1. The year is read off the citation string, so a review whose own search closed
   years before publication is scored as younger than its evidence. Marinho 2013
   scores as 12 years old; its newest included trial is from 2012 and its search
   closed 13 May 2013.
2. The 17 recommendations citing nothing dated are excluded rather than counted
   as maximally stale.
3. `"NICE. Stop smoking services. 2008 [updated 2018]"` resolves to 2018, which
   is the intended behavior: the max-year rule treats an updated guidance
   document by its update.

**Negative check on the year regex.** The 1950 to 2029 window was chosen so that
DOI fragments and volume/page numbers cannot match. Verified against the actual
reference strings: `10.1002/14651858.CD008286.pub3` contributes no match
(`1465`, `1858`, `0082` all fall outside the window), and
`10.1136/bmjopen-2016-015410` correctly contributes 2016 only.

## Rows found resting on a superseded version of their own cited review

| Row | Cited | Current at DBOH's publication | Update published |
|---|---|---|---|
| DBOH-074 | `CD010216.pub3` (2016) | `CD010216.pub9` | 29 Jan 2025 |
| DBOH-084 | `CD010276.pub2` (2015) | `CD010276.pub3` | Jul 2021 |

DBOH-084 was already documented in `ch20-oral-cancer.md` during the first pass.
DBOH-074 was found only on the second pass, because the first pass did not audit
the row at all. See `ch21-tobacco.md`.

## This book's own instances of the same failure

Recorded here because the chapter argues from them:

- `ch09-toothpaste-amount.md`: identifier query for `CD007693` returned nothing
  useful; concluded the 2010 version was current; `CD007693.pub3` (2024) exists.
- `ch20-oral-cancer.md`: identifier query missed `CD010276.pub3` (2021), the same
  update DBOH missed.
- `ch05-brushing-frequency.md`: a date-limited known-item query could not have
  retrieved a review published after its date limit.

Common lesson, already recorded in `README.md`: searching for a review by its
identifier is not an update search.


---

## Correction: the anchor date was wrong

**Added:** 8 September 2026.

The original analysis treated **10 September 2025**, the date displayed at the
top of every DBOH chapter, as the date of the evidence review. It is not.

GOV.UK publication history for *Delivering Better Oral Health*, read 8 September
2026 at the publication's own page:

| Date | Change log entry, verbatim |
|---|---|
| 10 September 2025 | Updated to add 'Appendix: clinical case studies' and to make improvements to the layout and formatting. |
| 9 November 2021 | Two additional organisations listed in the "Endorsements" section. |
| 21 September 2021 | Reviewed and updated guidance in full. Update published as 4th edition. |
| 22 March 2017 | Uploaded latest version of documents and added quick guides. |
| 3 November 2014 | Update to main guidance document: third edition (October 2014). |
| 24 September 2014 | Update to guidance documents: third edition, September 2014. |
| 12 June 2014 | First published. |

The last full evidence review was **21 September 2021**. The 2025 change was
case studies and formatting.

### What this changes

`scripts/extract_dboh.py` now measures citation age against 2021, not 2025.

| Statistic | Anchored to 2025 (wrong) | Anchored to 2021 (correct) |
|---|---:|---:|
| Median age of newest citation | 7 years | **3 years** |
| Oldest | 13 years | **9 years** |
| Newest citation 5 years or older | 64 of 74 | **23 of 74** |
| Newest citation 10 years or older | 16 of 74 | **0 of 74** |

The chapter's original headline finding does not survive. It was an artifact of
the anchor.

### Superseded reviews, re-dated

`scripts/living/currency.R` compared cited Cochrane versions against the wrong
date too. Re-anchored to the 2021 review:

| Review | Cited | Latest at 21 Sep 2021 | Verdict |
|---|---|---|---|
| CD010216 | pub3 (2016) | **pub6** (14 Sep 2021) | superseded at the review |
| CD010276 | pub2 (2015) | **pub3** (20 Jul 2021) | superseded at the review |
| CD006103 | pub7 (2016) | pub7 | current at the review; pub8 is 2023 |
| CD013308 | pub1 (2019) | pub1 | current at the review; pub2 is 2023 |

So **2 of 12** were superseded when the evidence was reviewed, not 4. The other
two decayed afterwards, which is a fact about how long the guidance has been
displayed rather than a failure by the panel.

### CD010216.pub6, the version available at the review

PMID 34519354, doi:10.1002/14651858.CD010216.pub6, published 14 September 2021.
Searched to 1 May 2021. 61 studies, 16,759 participants, 34 RCTs.

Nicotine EC versus NRT: RR 1.53 (95% CI 1.21 to 1.93), I2 0%, 4 studies, 1,924
participants, **moderate** certainty, limited by imprecision.

It already declares itself a living systematic review searched monthly. So the
chapter's claim is that a moderate-certainty finding was available, not a
high-certainty one; high certainty first appears in `.pub8` (2024).

### Claims removed as unsupported

- That varnish trials stopped because nobody funded them. Not investigated.
  Protecting Teeth @3, a randomized nursery-school varnish study, was published
  in 2020, and this book's own varnish record says post-2013 primary trials were
  not searched.
- That ten years of monthly tooth-wear searching would return nothing.
- That the guideline and this book "failed by the same method". DBOH's per-row
  search procedures are not published and were not inspected.
- That citation age predicts how long the book will remain current. A snapshot
  of publication years contains no observation of a recommendation becoming
  obsolete.
