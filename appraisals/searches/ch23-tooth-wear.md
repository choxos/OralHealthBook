# Chapter 23: tooth wear

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

## Queries

Systematic reviews of interventions to prevent tooth wear with a **wear**
outcome, and separately the post-acid brushing delay.

**No systematic review was identified that would support upgrading any of the
five Good practice recommendations**, which is consistent with DBOH assigning
Good practice throughout.

This is a thinner search than the Part II chapters received, and the chapter's
conclusion is correspondingly weaker: I did not find such evidence, rather than
it does not exist.

## Guideline text check, and a failure in my own tooling

The chapter's original claim that DBOH "tells you nothing" about the same
brushing advice carrying different labels in different tables was **wrong**.
Chapter 13 table 21 states it explicitly:

> Good practice for preventing tooth wear. Strong recommendation for preventing
> dental caries and conditional for periodontal disease.

The reason I missed it: `scripts/extract_dboh.py` failed to join this row
(`DBOH-087`) to its chapter 13 counterpart, scoring the fuzzy match at 0.44 and
filing it under `KNOWN_UNMATCHED`. The chapter was then written from the CSV
rather than from the guideline HTML.

Recorded here because it is the clearest instance in this project of the failure
mode the book is about: trusting a derived artifact instead of the source.
