#!/usr/bin/env Rscript
## Split the 91 guideline rows into the separable instructions they contain.
##
## This is the step the book's whole argument implies. DBOH chapter 13 says
## the panel "based the strength of recommendation on the main component",
## so one Strong label can cover four instructions of differing certainty.
## A surveillance system keyed on recommendations would inherit exactly that
## defect. The unit has to be the component.
##
## IMPORTANT: this produces a FLOOR, not a decomposition. It splits on
## bullet markers and pipe separators, which is a typographic fact rather
## than a semantic one. It will over-split where a bullet continues a
## sentence, and under-split badly where a single prose row bundles several
## distinct claims. DBOH-084 is the standing example: one unbulleted
## sentence naming vital staining, oral cytology, light-based detection and
## oral spectroscopy, which are four different tests with four different
## evidence bases and one shared Strong label. This script emits it as one
## component and flags it for review.
##
## Every row therefore lands with needs_review = TRUE. Nothing downstream
## should treat this file as final until a human has been through it.
##
##   Rscript scripts/living/decompose.R

here <- function() {
  f <- grep("--file=", commandArgs(FALSE), value = TRUE)
  if (length(f)) dirname(sub("--file=", "", f[1])) else "scripts/living"
}
source(file.path(here(), "_common.R"))

## Separators actually present in the extracted text: a bullet, or the pipe
## the extractor uses where DBOH's HTML had a line break.
split_components <- function(text) {
  parts <- str_split(text, "\\s*(?:\\||•)\\s*")[[1]]
  parts <- str_trim(parts)
  parts <- parts[nzchar(parts)]
  # A lead-in like "Act on patient response:" is not an instruction; it is a
  # heading for the bullets under it. Keep it only if it is the whole row.
  if (length(parts) > 1) {
    lead <- str_detect(parts, ":$")
    if (any(lead) && !all(lead)) parts <- parts[!lead]
  }
  if (!length(parts)) parts <- str_trim(text)
  parts
}

## Rows where a single prose sentence is known to bundle several distinct
## claims that carry no bullet. Listed explicitly rather than guessed at,
## because a heuristic here would be exactly the kind of silent judgment
## this pipeline is supposed to avoid.
PROSE_BUNDLES <- c(
  "DBOH-084",  # four different index tests in one sentence
  "DBOH-074",  # "quitting or reducing smoking" are different outcomes
  "DBOH-081"   # pregnancy and planning pregnancy are different populations
)

main <- function() {
  dboh <- read_dboh()
  cli_h1("Decomposing {nrow(dboh)} recommendations into components")

  comps <- map_dfr(seq_len(nrow(dboh)), function(i) {
    r <- dboh[i, ]
    parts <- split_components(r$recommendation %||% "")
    tibble(
      component_id  = sprintf("%s-c%d", r$id, seq_along(parts)),
      dboh_id       = r$id,
      n_in_row      = length(parts),
      component_pos = seq_along(parts),
      domain        = r$domain,
      population    = r$population,
      ch2_table     = r$ch2_table,
      strength      = r$strength,
      # The strength label belongs to the row, not to this component. That
      # is the bundling problem, restated as a column: every component here
      # inherits a label that may have been earned by a sibling.
      strength_is_inherited = length(parts) > 1,
      text          = parts,
      certainty_row = r$certainty_terms,
      weakest_certainty_row = r$weakest_certainty_mentioned,
      evidence_row  = str_sub(r$evidence_base %||% "", 1, 400),
      prose_bundle  = r$id %in% PROSE_BUNDLES,
      needs_review  = TRUE,
      question_id   = NA_character_,   # filled by hand: many components map
      reviewed_by   = NA_character_,   # to one shared review question
      reviewed_on   = NA_character_
    )
  })

  write_registry(comps, "components.csv")

  cli_h2("Shape of the problem")
  cli_bullets(c(
    "*" = "{nrow(comps)} component{?s} from {nrow(dboh)} row{?s}",
    "*" = "{sum(comps$strength_is_inherited)} component{?s} carry a label earned by a sibling",
    "*" = "{sum(comps$prose_bundle)} row{?s} flagged as prose bundles the splitter cannot see",
    "*" = "largest row: {max(comps$n_in_row)} components"
  ))

  big <- comps |>
    filter(n_in_row > 1) |>
    distinct(dboh_id, n_in_row, strength) |>
    arrange(desc(n_in_row)) |>
    head(8)
  cli_h3("Most bundled rows")
  for (i in seq_len(nrow(big))) {
    cli_li("{big$dboh_id[i]}: {big$n_in_row[i]} components [{big$strength[i]}]")
  }

  cli_alert_warning(
    "Every row is needs_review = TRUE. This is a floor produced by splitting on
     typography, not a semantic decomposition. Do not build questions on it
     until a human has been through it.")
  invisible(comps)
}

if (!interactive()) main()
