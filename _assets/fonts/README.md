# Vendored fonts

Four OTF files from the **TeX Gyre** collection, copied here so
`scripts/make_cover.py` can render the cover art on any machine,
including CI runners with no TeX installation.

| File | Family | Used for |
|---|---|---|
| `texgyrepagella-regular.otf` | TeX Gyre Pagella | back-cover blurb |
| `texgyrepagella-bold.otf` | TeX Gyre Pagella | title, spine |
| `texgyrepagella-italic.otf` | TeX Gyre Pagella | subtitle |
| `texgyreheros-bold.otf` | TeX Gyre Heros | the "STRONG" stamp, author |

Pagella is the same face the print interior sets in, so the cover and the
pages match. That is the point of vendoring rather than substituting
whatever the runner happens to have.

## Licence

TeX Gyre fonts are distributed by [GUST](https://www.gust.org.pl/projects/e-foundry)
under the **GUST Font License (GFL)**, a LaTeX Project Public License
variant that explicitly permits redistribution and modification. They are
derived from the URW++ base-35 fonts released by URW++ under the AFPL/GPL.

Redistribution here is permitted. This directory is not covered by the
book's own licence.

Upstream: <https://www.gust.org.pl/projects/e-foundry/tex-gyre>
