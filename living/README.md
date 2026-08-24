# Living evidence

**Goal: a maintained database of current evidence for every recommendation in
*Delivering Better Oral Health*, and for every question the book asks.**

Full coverage is the target. This document is about the order of operations
that gets there, because the failure mode of a system like this is not
incompleteness. It is publishing a "current as of" date that the pipeline has
not actually earned.

Everything here is R. `scripts/living/*.R`. The book's own toolchain
(`extract_dboh.py` and friends) remains Python for now; it is a separate system
with a separate lifecycle, and this pipeline reads its CSV output rather than
its code.

---

## Why this exists

[Chapter 32](../parts/06-anyway/32-the-half-life-of-a-recommendation.qmd) found
that the median DBOH recommendation rested on evidence most recently published
seven years before the guideline appeared, and that at least two recommendations
cited a version of their own review that had already been superseded.

Both were found by accident. `currency.R` now asks the question systematically
and finds **four**, including two on `DBOH-072`, a Strong recommendation.

The book's complaint about the guideline applies to the book. It searched in
August 2026 and will decay on the same schedule. A dated static audit is honest
about where it stopped; the point of this system is to stop having to stop.

## The unit is the component, not the recommendation

DBOH chapter 13 states that when a recommendation covers multiple components,
the panel "based the strength of recommendation on the main component." That is
the book's central finding. A surveillance system keyed on recommendations would
rebuild the same defect one layer up: it would maintain one evidence state for a
row that contains four separate claims.

So the data model is:

```
recommendation  (91)   the guideline's row, as published
  └─ component  (136+) one separable instruction
       └─ question      one atomic decision claim, deduplicated across components
            └─ study         one investigation
                 └─ report        one publication of it
                      └─ effect        one estimate, one outcome, one time point
```

Components map to questions **many-to-one**. Five varnish rows across five
populations are not five review questions. Conversely `DBOH-084` is one
unbulleted sentence naming four different index tests with four different
evidence bases, and it is one row, one component by any typographic split, and
at least four questions.

That asymmetry is why `decompose.R` marks every row `needs_review = TRUE`.
Splitting on bullets is a fact about typography. It is a floor, not a
decomposition.

## Registry files

Generated into `living/registry/`. All are inputs to human work, not outputs of
it.

| File | Produced by | Status |
|---|---|---|
| `currency.csv` | `currency.R` | **Working.** Complete and trustworthy for Cochrane citations. |
| `components.csv` | `decompose.R` | Seed. Every row needs semantic review. |
| `triggers.csv` | `triggers.R` | Seed. Triage columns deliberately empty. |
| `questions.csv` | not yet written | Blocked on human review of `components.csv`. |

## What runs today

```sh
Rscript scripts/living/currency.R      # version currency, ~1 min, network
Rscript scripts/living/decompose.R     # 91 rows -> 136 components
Rscript scripts/living/triggers.R      # 23 chapters -> 23 update triggers
```

`currency.R` is the one piece that is finished and correct. It needs no
screening, no extraction, no model and no judgment: Cochrane puts the version in
the DOI, so the comparison is one integer against another. It is the cheapest
possible thing that would have caught the failure the book is about.

It is also the template for the whole system's discipline. It reports which rows
are worth a human opening. It does not claim to know whether an update changes a
recommendation, because only a human reading both versions can know that.

> **A bug worth recording.** The first version of this tool reported 2 of 12
> superseded when the answer is 4 of 12. PubMed returns dates as `2025/01/29`;
> the filter compared them against `2025-09-10`, and `/` sorts above `-` in
> ASCII, so every 2025 version was silently excluded. A currency checker that
> silently under-reports staleness is worse than no currency checker. Dates are
> now parsed to `Date` once, in `_common.R`, so no caller can repeat it.

## The triage rule

Not every question gets continuous updating, and this is the part most likely to
be argued with, so it is written down.

A question enters **living** mode only if all three hold, per the living
systematic review methods literature (Elliott 2017,
[10.1016/j.jclinepi.2017.08.010](https://doi.org/10.1016/j.jclinepi.2017.08.010)):

1. the decision matters,
2. the current answer is uncertain enough that new evidence could move it, **and**
3. new evidence is actually plausible.

The third is the one that gets skipped, and it is cheaply testable: query ICTRP
and ClinicalTrials.gov for registered ongoing trials matching the question. Zero
registered trials means annual surveillance, not monthly.

**Low certainty is not a trigger.** It usually means nobody is running the study.
The Cochrane review of recall intervals says in terms that "further studies
comparing dental recall intervals for adults in primary care seem unnecessary."
Monthly searching there produces a decade of confirmations that the trials still
do not exist.

Modes: `living` (monthly) | `annual` | `dormant` (registry alert only) |
`closed` (settled; re-open only on a registry hit).

Every question gets a mode and a `last_checked` date. **Full coverage means
every question has a state, not that every question is searched monthly.**

## Screening and extraction rules

These are constraints on the pipeline, not aspirations.

**Never majority-vote across models.** The costs are asymmetric: a missed
include is unrecoverable and silent, a false include costs thirty seconds.
Aggregate as **union for include, unanimity for exclude**. Any one model saying
include, a human looks.

**No autonomous exclusion.** Not now, and not until a validation set exists that
can support it. The bar: zero misses across at least 299 unseen eligible
reports, which by the rule of three gives a one-sided 95% lower bound of about
99% sensitivity, with zero misses in every pre-specified hard-case stratum. This
repository cannot currently supply that set.

**Models prioritize; they do not decide.** If more than one model is used, give
them different roles rather than votes: high-recall prioritizer, source-bound
extraction drafter, adversarial error finder. Correlated failure across frontier
models means three votes buy far less independence than they look like.

**Never average or vote on an extracted number.** A disagreement between 369
randomized, 281 completing and 131 in the selected subgroup is not three
opinions about one quantity. They are different denominators. Discrepancies go
back to the source.

**Every synthesis-critical field is human-verified**, and carries a pointer to
the exact table, cell or text span it came from. Meta-analysis is deterministic
code. Risk of bias, GRADE and evidence-to-decision judgments stay human.

## Retrieval is the binding constraint

More models do not fix this. Four failure modes are already documented in this
repository:

- Sjögren 1995 is a doctoral thesis supplement in *Swed Dent J Suppl*. No
  monthly PubMed screen surfaces it.
- Cochrane full texts sit outside the PMC Open Access subset, verified by four
  independent routes in `appraisals/searches/ch21-tobacco.md`.
- CENTRAL-only and non-English trials.
- Cochrane update status is not a PubMed field, which is exactly why
  `currency.R` has to reconstruct it from DOIs.

Europe PMC, CENTRAL, ICTRP and a Cochrane update-status feed are each worth more
than an additional model.

## State, and the rule about claiming currency

Every question carries separate timestamps for `searched`, `screened`,
`extracted`, `appraised`, `synthesized`, `published`.

**Nothing may display as current while any later stage is pending.** An
underfunded system that has searched recently but not screened, extracted and
adjudicated creates false reassurance, and that is worse than the book's honest
static date. This is the single rule the pipeline must not break.

## Next steps, in order

1. **Calibrate before building forward.** Run the retrieval design
   retrospectively against the 27 hand-written records in
   `appraisals/searches/`. If it does not recover Weintraub 2006, Wong 2024 and
   Walsh 2021, the three the book's second pass caught, it is not ready. This is
   a few hours and it settles the question with a number.
2. **Human pass over `components.csv`**, resolving prose bundles and assigning
   `question_id`. This is the gate on everything downstream.
3. **Score the triage columns** in `triggers.csv`. Expect few `living` rows.
4. **Extend currency checking beyond Cochrane.** NICE, SDCEP and journal
   citations decay too, but not in a way a DOI reveals. Different mechanism.
5. **Registered-trial monitoring** via ICTRP and ClinicalTrials.gov, which is
   what turns criterion 3 of the triage rule from a guess into a query.
6. **Consume existing living reviews rather than duplicating them.** CD010216 is
   already a living systematic review, searched monthly, funded by Cancer
   Research UK. What was missing was never a review. It was a subscription and
   somebody to read it.

## Findings so far

`currency.R`, run against the 10 September 2025 edition:

| Review | Cited | Current at edition | Behind | Rows affected |
|---|---|---|---|---|
| CD010216 | pub3 (2016) | pub9 (2025) | 6 versions, 9 years | DBOH-074 (Conditional) |
| CD006103 | pub7 (2016) | pub8 (2023) | 1 version, 7 years | DBOH-072 (**Strong**) |
| CD010276 | pub2 (2015) | pub3 (2021) | 1 version, 6 years | DBOH-084 (**Strong**) |
| CD013308 | pub1 (2019) | pub2 (2023) | 1 version, 4 years | DBOH-072 (**Strong**) |

`DBOH-072` is the Strong "Advise" recommendation naming varenicline and nicotine
replacement therapy. It rests on two reviews that were both superseded before
the guideline was published. The book does not yet report this.
