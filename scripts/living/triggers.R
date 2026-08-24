#!/usr/bin/env Rscript
## Harvest the book's own update rules out of the chapters.
##
## Every audit chapter ends with a Verdict box whose last field is "What
## would change my mind". Those were written by a human, before the fact,
## and they are the single most valuable asset this repository has for a
## surveillance system: they are pre-registered update triggers. Nobody
## wrote them to be machine-readable, which is why this script exists.
##
## What a harvested trigger is NOT: a query. "A cohort study measuring wear
## with a validated index against recorded dietary acid exposure over ten
## years or more" is a sentence, not a search strategy, and turning it into
## one is human work. This script captures the sentence, attaches it to the
## chapter and the verdict, and leaves four empty columns for the person who
## will do that work.
##
##   Rscript scripts/living/triggers.R

here <- function() {
  f <- grep("--file=", commandArgs(FALSE), value = TRUE)
  if (length(f)) dirname(sub("--file=", "", f[1])) else "scripts/living"
}
source(file.path(here(), "_common.R"))

## The four Verdict fields, in the fixed order the book uses.
VERDICT_FIELDS <- c(
  "Certainty of evidence",
  "Directness to the advice as worded",
  "Is the strength label defensible?",
  "What would change my mind"
)

chapter_files <- function() {
  list.files(file.path(ROOT, "parts"), pattern = "\\.qmd$",
             recursive = TRUE, full.names = TRUE) |> sort()
}

## Pull a definition-list body: everything from "Field name" on its own line
## through the following ":   " block, stopping at the next field or the end
## of the verdict div.
extract_field <- function(lines, field) {
  start <- which(str_trim(lines) == field)
  if (!length(start)) return(NA_character_)
  start <- start[1]
  stop_at <- c(
    which(str_trim(lines) %in% setdiff(VERDICT_FIELDS, field) & seq_along(lines) > start),
    which(str_trim(lines) == ":::" & seq_along(lines) > start),
    length(lines) + 1L
  )
  body <- lines[(start + 1):(min(stop_at) - 1)]
  body <- str_replace(body, "^:\\s{2,}", "")
  body <- str_trim(body)
  body <- body[nzchar(body)]
  if (!length(body)) return(NA_character_)
  txt <- paste(body, collapse = " ")
  # Strip the book's inline markup so the stored trigger is prose.
  txt <- str_replace_all(txt, "\\[([^]]*)\\]\\{[^}]*\\}", "\\1")
  txt <- str_replace_all(txt, "\\[Chapter -@([a-z-]+)\\]", "[\\1]")
  txt <- str_replace_all(txt, "\\*\\*|\\*", "")
  str_squish(txt)
}

main <- function() {
  files <- chapter_files()
  cli_h1("Harvesting update triggers from {length(files)} chapter{?s}")

  out <- map_dfr(files, function(f) {
    lines <- readLines(f, warn = FALSE)
    sec <- str_match(paste(lines, collapse = "\n"), "\\{#(sec-[a-z0-9-]+)\\}")[, 2]
    title <- str_trim(str_replace(
      str_replace(lines[str_detect(lines, "^# ")][1] %||% "", "^#\\s*", ""),
      "\\{#.*\\}$", ""))

    has_verdict <- any(str_detect(lines, fixed("{.verdict}")))
    if (!has_verdict) return(tibble())

    trig <- extract_field(lines, "What would change my mind")
    tibble(
      chapter_file = str_replace(f, fixed(paste0(ROOT, "/")), ""),
      sec_id       = sec %||% NA_character_,
      title        = title,
      certainty    = extract_field(lines, "Certainty of evidence"),
      directness   = extract_field(lines, "Directness to the advice as worded"),
      defensible   = extract_field(lines, "Is the strength label defensible?"),
      trigger      = trig,
      # To be filled by hand. A trigger is a sentence; these turn it into
      # something a search can test. Left empty deliberately: guessing them
      # would put an unreviewed judgment into the surveillance rule.
      eligible_designs   = NA_character_,
      critical_outcome   = NA_character_,
      min_followup       = NA_character_,
      decision_threshold = NA_character_,
      # Triage, per the living systematic review criteria: a question enters
      # living mode only if the decision matters, the current answer is
      # uncertain, AND new evidence is actually plausible. Scored by hand.
      triage_matters     = NA,
      triage_uncertain   = NA,
      triage_evidence_coming = NA,
      surveillance_mode  = NA_character_,  # living | annual | dormant | closed
      last_checked       = NA_character_
    )
  })

  write_registry(out, "triggers.csv")

  cli_h2("Coverage")
  cli_bullets(c(
    "*" = "{nrow(out)} chapter{?s} with a Verdict box",
    "*" = "{sum(!is.na(out$trigger))} with a harvested 'what would change my mind'",
    "v" = "{sum(is.na(out$trigger))} missing (should be 0)"
  ))

  missing <- filter(out, is.na(trigger))
  if (nrow(missing)) {
    cli_alert_danger("No trigger extracted from:")
    for (i in seq_len(nrow(missing))) cli_li(missing$chapter_file[i])
  }

  cli_h3("Sample")
  s <- filter(out, !is.na(trigger)) |> head(3)
  for (i in seq_len(nrow(s))) {
    cli_par()
    cli_text("{.strong {s$title[i]}}")
    cli_text(str_sub(s$trigger[i], 1, 240), if (nchar(s$trigger[i]) > 240) "..." else "")
    cli_end()
  }

  cli_alert_warning(
    "Triage columns are empty by design. Scoring them is the human decision
     that determines which questions get continuous surveillance and which
     get left alone.")
  invisible(out)
}

if (!interactive()) main()
