# Search records

One file per chapter. Each records the database, the query as run, the date, the
number of records returned, what was screened in, and what was concluded.

"I searched PubMed" is not a method. The point of this directory is that anyone
can re-run these and get the same set, or a larger one if something has been
published since.

## Conventions

- Queries are recorded **as submitted**, along with PubMed's own query
  translation where it materially changed the search.
- Every search has a **date run**. Results after that date are not in the book.
- Records screened in are listed by PMID with a one-line reason.
- A search that found nothing is recorded too. A null result is a finding, and
  an undocumented null result is indistinguishable from not having looked.

## Coverage

Searches were run in **PubMed only**. This is a real limitation and worth
stating: a full systematic search would add Embase, CENTRAL, CINAHL and trial
registries, and would have two people screening independently. This book has
one person and one database. Where a Cochrane review of the question exists, I
lean on its search rather than pretending mine substitutes for it.

| Chapter | File |
|---|---|
| 5. Brush twice daily | `ch05-brushing-frequency.md` |
| 6. Brush last thing at night | `ch06-brushing-timing.md` |
| 7. Spit, don't rinse | `ch07-post-brushing-rinsing.md` |
| 8. How much fluoride | `ch08-fluoride-concentration.md` |
| 9. How much toothpaste | `ch09-toothpaste-amount.md` |
| 10. Fluoride varnish | `ch10-fluoride-varnish.md` |
| 11. Fissure sealants | `ch11-sealants.md` |
| 12. Fluoride mouth rinse | `ch12-fluoride-rinse.md` |
| 13. Sugar | `ch13-sugar.md` |
| 14. Breastfeeding | `ch14-breastfeeding.md` |
| 15. The quieter tier | `ch15-quieter-tier.md` |
| 16. Manual or powered | `ch16-powered.md` |
| 17. Flossing | `ch17-interdental.md` |
| 18. Toothbrush design | `ch18-brush-design.md` |
| 19. Scale and polish | `ch19-scale-and-polish.md` |
| 20. Oral cancer screening | `ch20-oral-cancer.md` |
| 21. Tobacco | `ch21-tobacco.md` |
| 22. Alcohol | `ch22-alcohol.md` |
| 23. Tooth wear | `ch23-tooth-wear.md` |
| 24. Does fluoridation work | `ch24-fluoridation.md` |
| 25. Is fluoridation harmful | `ch25-fluoridation-harm.md` |
| 26. Filling children's teeth | `ch26-fiction.md` |
| 27. Bad breath | `ch27-halitosis.md` (no search run) |
| 28. Six-month check-up | `ch28-recall.md` |
| 29. The toothpaste aisle | `ch29-toothpaste-aisle.md` |
| 30. Short answers | `ch30-short-answers.md` (no search run) |

| 32. The half-life of a recommendation | `ch32-half-life.md` |

Chapters 1 to 4, 31 and 33 reach no verdict and have no search record.

## Searches that failed

Three searches in this book missed something that a better query would have
found, and each is recorded in its own file rather than quietly re-run:

- `ch09-toothpaste-amount.md`: an update search by Cochrane review ID missed
  CD007693.pub3 (2024).
- `ch20-oral-cancer.md`: the same failure mode missed CD010276.pub3 (2021).
- `ch05-brushing-frequency.md`: a date-limited known-item query could not have
  retrieved a frequency review published after 2018, and did not.
- `ch13-sugar.md`: a known-item query on the 2014 review's authors and title
  missed its own ten-year update (Moores 2022), which upgraded the evidence for
  the 5% threshold from very low to low.

The common lesson is that searching for a review by its identifier is not an
update search.

**DBOH fails the same way.** `ch32-half-life.md` records two recommendations
resting on a superseded version of their own cited review: DBOH-084 on
`CD010276.pub2` when `.pub3` had been out since 2021, and DBOH-074 on
`CD010216.pub3` when `.pub9` had been out since January 2025. The oral cancer
update is the one this book also missed on its first pass, by the same method,
four years later. Chapter 32 argues from that coincidence.
