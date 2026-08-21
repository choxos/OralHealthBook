# Sources under audit

The documents this book examines, archived at the version that was read, so that
the extraction can be re-run against exactly the text quoted even after the
guideline is next updated.

## What is here

**`Books/DBOH_UK/`** — *Delivering Better Oral Health: an evidence-based toolkit
for prevention*, all thirteen chapters plus the appendix, as updated on
**10 September 2025**.

Crown copyright, redistributed here under the
[Open Government Licence v3.0][ogl], which permits copying and republishing,
including commercially, with attribution. Neither the Crown nor any of the
issuing bodies endorses this book or its conclusions.

`scripts/extract_dboh.py` parses these files directly. They are the input to
`appraisals/dboh-2025.csv`, which is the spine of the book.

**`BlogPosts/`** — the four Medium posts this book grew from, as HTML exports,
plus `Drafts.md`. The author's own work.

## What is deliberately not here

Two categories of third-party material are kept locally and excluded from the
repository by `.gitignore`. The book quotes both; it does not redistribute
either.

**`Books/SIGN_Scot/SIGN138.pdf`** — SIGN 138, *Dental interventions to prevent
caries in children* (Scottish Intercollegiate Guidelines Network, Healthcare
Improvement Scotland, 2014). Passages are quoted in the book for the purposes of
criticism and review under section 30 of the Copyright, Designs and Patents Act
1988. That does not extend to republishing the complete document.

To restore it, download the PDF from
<https://www.sign.ac.uk/our-guidelines/dental-interventions-to-prevent-caries-in-children/>
and save it as `sources/Books/SIGN_Scot/SIGN138.pdf`. Nothing in the build
depends on it; it was used for tracing citations by hand, and every passage the
book relies on is quoted in the text with its section number.

**Images inside the Medium exports** — the saved pages embed figures taken from
journal articles, including a forest plot and a data table reproduced from
copyrighted papers. Every figure in this book is redrawn from the numbers
reported in its source precisely so that none is reproduced, and the repository
holds to the same rule. The `_files/` sidecar directories are excluded entirely;
they also contained Medium's own scripts and stylesheets, which have no
evidential value.

[ogl]: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
