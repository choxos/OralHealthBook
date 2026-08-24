# Chapter 21: tobacco

**Two searches.** The first, in the original pass, covered only the Cochrane
review of dental-delivered cessation. The second was added after the chapter was
found to have skipped DBOH-074, the e-cigarette row, entirely.

## Search 1: tobacco cessation delivered by dental professionals

**Database:** PubMed
**Date run:** 21 August 2026

## Deferring to the Cochrane search

The cited source is a Cochrane review [@holliday2021] whose own search ran to
**February 2020** across the Cochrane Tobacco Addiction Group's Specialised
Register. No independent search of the primary literature was attempted.

## Query: is there a newer version?

```
Holliday Hong McColl interventions tobacco cessation delivered by dental
professionals Cochrane
```

**1 record.** PMID 33605440, CD005084.pub4, doi:10.1002/14651858.CD005084.pub4.
No `.pub5` found. Current version.

## Figures extracted, all from the structured abstract

| Comparison | RR | 95% CI | I2 | studies | n | certainty |
|---|---|---|---|---:|---:|---|
| Behavioural support, 1 session | 1.86 | 1.01 to 3.41 | 66% | 4 | 6328 | very low |
| Behavioural support, >1 session | 1.90 | 1.17 to 3.11 | 61% | 7 | 2639 | very low |
| Behavioural + NRT/e-cigarettes | 2.76 | 1.58 to 4.82 | 0% | 4 | 1221 | moderate |
| Behavioural support, school/college | 1.51 | 0.86 to 2.65 | 83% | 3 | 1020 | very low |

20 trials, 14,897 participants. Risk of bias as stated by the review: 3 low,
1 unclear, 16 high.

## Limitation: no full text

Cochrane reviews are deposited in PubMed Central but sit **outside** the PMC Open
Access subset. Verified on 21 August 2026 by four routes:

- PubMed MCP `get_full_text_article` returns an empty `full_text` field
- NCBI `efetch db=pmc` returns front matter only: no `<body>`, no `<table-wrap>`,
  no `<ref>`
- the PMC OA service returns `idIsNotOpenAccess`
- Europe PMC `fullTextXML` returns 404 and `supplementaryFiles` returns
  `"Article with id ... is not open access one"`

So for every Cochrane review in this book I have the structured abstract, which
carries the effect estimates, confidence intervals, heterogeneity, certainty
ratings, search dates and authors' conclusions, but **not** the risk-of-bias
table or the characteristics of included studies. Statements in the chapters
about risk of bias across included studies are the reviews' own summary
statements, quoted as such, and are marked that way in the text.


---

## Search 2: the e-cigarette row (DBOH-074)

**Date run:** 20 August 2026

### Why this was missed the first time

The chapter opened by stating that tobacco gets "five Strong recommendations
across two tables" and then audited three rows from table 3a. The actual count
across tables 3a and 3b is **seven** rows: six Strong and one Conditional.
DBOH-074 is the Conditional one, and it was neither quoted nor searched.

The miscount and the omission share a cause. I worked from the three-step
Ask/Advise/Act structure rather than from the extracted rows, and the e-cigarette
row does not fit that structure, so it fell out of the chapter without leaving a
gap that was visible from inside it. The extraction CSV had it correctly all
along, as did appendix A.

### The row

`DBOH-074`, table 3a, **Conditional**: "Acknowledge that e-cigarettes may be
helpful for some smokers for quitting or reducing smoking."

Chapter 13 table 15: "Recommendation based on low certainty evidence from one
systematic review; insufficient evidence to demonstrate the long-term effects."

Cited: Hartmann-Boyce J, McRobbie H, Bullen C, Begh R, Stead LF, Hajek P.
*Electronic cigarettes for smoking cessation.* Cochrane Database of Systematic
Reviews 2016; (9). doi:10.1002/14651858.CD010216.pub3

### Query

```
Electronic cigarettes for smoking cessation[Title] AND Cochrane Database Syst Rev[Journal]
```

**24 records**, and a narrower author query returning 19. Full version history and
the extracted figures are recorded once, in `ch32-half-life.md`, because chapter
32 argues from the same search. In summary:

- DBOH cites `.pub3`, which searched to January 2016.
- `.pub9` was published 29 January 2025 and was the current version on
  10 September 2025, the date of the DBOH edition audited here.
- `.pub9` reports **high** certainty that nicotine EC increase quit rates versus
  NRT: RR 1.59 (95% CI 1.30 to 1.93), I2 0%, 7 studies, 2,544 participants.
- `.pub10`, 10 November 2025, is current: RR 1.55 (95% CI 1.28 to 1.88), 104
  studies, 30,366 participants, high certainty.
- Every version from `.pub8` onward declares in its abstract that it is a living
  systematic review searched monthly.

### What this does and does not support

It supports the claim that DBOH's **certainty statement** for this row describes
a superseded evidence base.

It does **not** support a claim that the strength label is wrong. Conditional on
high-certainty benefit is a legitimate evidence-to-decision position given the
residual imprecision on serious adverse events, which persists in `.pub10`
(RR 1.22, 95% CI 0.73 to 2.03; 8 studies, 2,950 participants; low certainty).
The chapter is written to that narrower claim.
