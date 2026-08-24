# Chapter 32: the half-life of a recommendation

**Database:** PubMed
**Date run:** 20 August 2026

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
