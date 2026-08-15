# The Evidence Behind

*What we actually know about looking after your teeth*

An audit of the recommendations in [*Delivering Better Oral Health*][dboh]
(DBOH), the UK's national oral health guidance, as updated on 10 September
2025. For each recommendation the book asks one question: **does the evidence
the guideline cites answer the question the advice asks?**

Read it free at **<https://choxos.github.io/OralHealthBook>**.
A print and Kindle edition, which adds the full evidence tables, search
strategies and appraisal detail, is on Amazon.

---

## The argument

DBOH labels each recommendation Strong, Conditional, or Good practice, and
chapter 13 of the 2025 edition publishes the certainty rating behind every one.
Very few guidelines anywhere are that open, and the book gives it credit for
that. But chapter 13 also states the drafting rule that this book is about:

> When a recommendation covers multiple components, each GDG considered the
> underlying evidence for each component and based the strength of
> recommendation on the main component.

So a recommendation that bundles several pieces of advice takes its Strong
label from whichever component has the best evidence. "Brush last thing at
night and on one other occasion, with a toothpaste containing 1,350 to
1,500ppm fluoride, spitting out rather than rinsing" is one Strong
recommendation containing at least four separable instructions, whose evidence
DBOH itself rates from moderate down to low. A reader has no way to tell which
part earned the badge.

The book is **not** an argument for abandoning any of this advice. See
chapter 31.

## Method

Each audit chapter follows the same seven steps:

1. The advice, quoted verbatim from DBOH chapter 2, with its strength label.
2. What DBOH says its evidence is, quoted from chapter 13, with its certainty
   rating.
3. Follow the citation. Read the source. Does it match the advice on
   population, intervention, comparator and outcome?
4. Appraise it, with the judgments shown (RoB 2, ROBINS-I, AMSTAR 2, ROBIS).
5. Search for anything better, with a date-stamped, reproducible strategy.
6. A verdict box in a fixed format, including *what would change my mind*.
7. What this means for you, in plain language.

Every appraisal is published in machine-readable form under [`appraisals/`](appraisals/),
so the book's own claims can be checked the same way it checks everyone else's.

## Repository layout

```
index.qmd              Preface, disclaimer, declaration of interests
parts/                 The 31 chapters, one .qmd each
appendices/            Print-edition apparatus (excluded from the website)
appraisals/            Machine-readable appraisal data, one row per recommendation
bibliography/refs.bib  Every source, each with a DOI, PMID or stable URL
figures/               All figures, redrawn; drawing code in figures/src/
scripts/               Build, extraction and checking scripts
sources/               The archived DBOH and SIGN documents under audit
_extensions/kdp/       LaTeX template for the 6x9in paperback
```

## Building

Requires [Quarto](https://quarto.org) 1.8+, Python 3.12+ with `pillow` and
`beautifulsoup4`, R with `ggplot2`, and a LaTeX installation for the PDF.

```bash
make            # list all targets
make web        # free website          -> _book/
make print      # PDF and EPUB          -> dist/
make covers     # cover art             -> figures/
make check      # citation + chapter completeness checks
make kdp        # full pre-upload build for Amazon
```

`make check` fails the build if a cited key is missing from `refs.bib`, if a
journal article lacks a DOI or PMID, or if a verdict box is left unfilled. A
book that criticises other people's citation practice should not have loose
citation practice of its own.

The paperback wrap's spine width is computed from the actual page count of the
built PDF, so run `make pdf` before `make covers` whenever the manuscript
changes length.

## Licence

The text of the book is © 2026 Ahmad Sofi-Mahmudi, released under
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
Code in `scripts/` and `figures/src/` is MIT.

Material from *Delivering Better Oral Health* is Crown copyright, reproduced
under the [Open Government Licence v3.0][ogl]. Neither the Crown nor any of the
issuing bodies endorses this book or its conclusions. Passages from SIGN 138 and
other guidelines are quoted for the purposes of criticism and review. Fonts in
`_assets/fonts/` are under the GUST Font License; see the README there.

Every figure has been redrawn from the numbers reported in the cited source.
No figure is reproduced from a copyrighted paper.

[dboh]: https://www.gov.uk/government/publications/delivering-better-oral-health-an-evidence-based-toolkit-for-prevention
[ogl]: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
