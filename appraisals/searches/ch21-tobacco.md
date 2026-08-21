# Chapter 21: tobacco cessation delivered by dental professionals

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
