# Chapter 13: sugars and dental caries

::: provenance
**How this record was produced.** The searches below were run on the dates
stated and disclosed in the chapter at the time. This file was written up
afterwards, from that disclosure and from the working notes, when an audit found
that the chapter pointed at a record file that did not yet exist. It is therefore
a faithful account of what was done, not a contemporaneous log, and it is marked
as such because the alternative is to let a reader assume otherwise. Where a
search failed and had to be re-run, the failure is recorded first.
:::

**Database:** PubMed
**Date run:** 21 August 2026
**Question:** Is there a systematic review of sugars and caries more recent than
Moynihan and Kelly 2014 that is intended to inform guidelines?

## Result

None superseding it was identified. Moynihan PJ, Kelly SAM. Effect on caries of
restricting sugars intake: systematic review to inform WHO guidelines. *J Dent
Res* 2014;93(1):8-18. doi:10.1177/0022034513508954 remains the basis of WHO
guidance and of DBOH's citation.

## The review's own search

**1950 through November 2011**, multiple databases. The paper is dated 2014. An
earlier draft of the chapter gave the search end-date as 2013; it is November
2011, which makes the evidence base fifteen years old at the time of writing
rather than twelve.

## Full text and supplements

Held: full text plus all six supplementary files, including the GRADE profile
tables (`documentation/refs/`). Three things in the chapter come from those
tables rather than the paper:

- the upgrade is for **large effect size** only (SMD 0.82, 95% CI 0.67 to 0.97
  for DMFT; prevalence RR 7.15, 95% CI 2.82 to 8.14);
- "dose-response effect noted from Rugg-Gunn cohort study also supported by
  population studies **but not further upgraded**";
- the <5% body is three Japanese ecological studies from 1959 and 1960, rated
  very low after downgrading for risk of bias from per-capita data.

The first two corrected an earlier draft that listed consistency and
dose-response among the upgrade criteria applied.

## Gram figures

The chapter's gram equivalents are taken from DBOH chapter 10 (19 g at ages 4 to
6, 30 g from age 11, both at the 5% level) and from WHO's own 10% illustration of
roughly 50 g on a 2,000 kcal diet. An earlier draft gave figures I could not
source, and they have been removed.


---

## Correction: this search failed

**Added:** 8 September 2026, after an independent prepublication review.

The original entry recorded that I checked for a more recent systematic review of
sugars and caries intended to inform guidelines and found none superseding
Moynihan and Kelly 2014.

One exists:

- **PMID 35302414.** Moores CJ, Kelly SAM, Moynihan PJ. *Systematic Review of the
  Effect on Caries of Sugars Intake: Ten-Year Update.* J Dent Res
  2022;101(9):1034-1045. doi:10.1177/00220345221082918

### Why the query could not have found it

The search was built around the 2014 review's authors and title. That is a
known-item query: it retrieves the paper you already have. It cannot tell you a
successor exists, because every term in it describes the predecessor. This is the
same failure recorded in `ch09-toothpaste-amount.md`, `ch20-oral-cancer.md` and
`ch05-brushing-frequency.md`, and it is the subject of chapter 32.

A query that would have found it, run 8 September 2026:

```
(sugars OR "free sugars") AND (caries OR "dental decay")
AND systematic[sb] AND 2015:2026[dp]
```

### What the update changes

| Threshold | Moynihan and Kelly 2014 | Moores 2022 |
|---|---|---|
| Free sugars < 10% of energy | moderate | moderate, confirmed by new cohort data |
| Free sugars < 5% of energy | very low | **low** (upgraded) |

23 eligible studies from 488 new papers, covering 2011 to 2020: 4 cohort, 1
case-control, 12 cross-sectional, 6 ecological. Amalgamated with the original
review, 64 of 78 studies show at least one positive association between sugars
and caries, 20 of 78 null, 3 of 78 negative.

Authors' conclusion: the findings "support and strengthen original evidence
underpinning the WHO recommendations for sugars."

### Consequence for the audit

DBOH's evidence statement for the sugar rows reports very low certainty for the
5% threshold. That was correct for the review DBOH cites. The update predates the
10 September 2025 edition by more than three years, so this is a fourth instance
of the decay pattern in chapter 32, and the first one that is not a Cochrane
review. `scripts/living/currency.R` reads versions out of Cochrane DOIs and
therefore cannot detect this class at all.
