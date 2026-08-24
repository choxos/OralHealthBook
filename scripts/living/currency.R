#!/usr/bin/env Rscript
## Is any DBOH recommendation resting on a superseded version of its own
## cited review?
##
## The book found two of these by hand and by accident: DBOH-084 on
## CD010276.pub2 when .pub3 had been out since 2021, and DBOH-074 on
## CD010216.pub3 when .pub9 had been out since January 2025. This asks the
## question systematically, and finds more than two.
##
## Why this is the first tool in the pipeline: it needs no screening, no
## extraction, no model and no judgment. Cochrane puts the version in the
## DOI, so the whole comparison is one integer against another. It is the
## cheapest possible thing that would have caught the failure the book is
## about, and it runs in under a minute.
##
## What it cannot do: tell you whether an update changes a recommendation.
## Only a human reading both versions can. It tells you which rows are
## worth opening, which is the step that failed.
##
##   Rscript scripts/living/currency.R
##   Rscript scripts/living/currency.R --offline   # re-render saved results

here <- function() {
  f <- grep("--file=", commandArgs(FALSE), value = TRUE)
  if (length(f)) dirname(sub("--file=", "", f[1])) else "scripts/living"
}
source(file.path(here(), "_common.R"))

OUT <- "currency.csv"

# ---- which Cochrane reviews does DBOH cite, and at which version? --------
cited_reviews <- function() {
  refs <- read_dboh() |>
    select(dboh_id = id, strength, references) |>
    filter(!is.na(references), references != "") |>
    mutate(ref = str_split(references, fixed("||"))) |>
    tidyr::unnest(ref) |>
    mutate(ref = str_trim(ref)) |>
    filter(ref != "")

  parsed <- bind_cols(refs, parse_cochrane(refs$ref))

  # A citation may name the review without a versioned DOI. Keep it, with
  # version NA, so it reports as unknown rather than vanishing.
  bare <- is.na(parsed$review_id) &
    str_detect(parsed$ref, regex(RE_COCHRANE_ID, ignore_case = TRUE))
  parsed$review_id[bare] <- toupper(str_match(
    parsed$ref[bare], regex(RE_COCHRANE_ID, ignore_case = TRUE))[, 2])

  parsed |>
    filter(!is.na(review_id)) |>
    mutate(ref_year = newest_year(ref)) |>
    group_by(review_id) |>
    summarise(
      # If two rows cite different versions, the oldest is the exposure.
      cited_version = suppressWarnings(min(version, na.rm = TRUE)),
      cited_year    = suppressWarnings(max(ref_year, na.rm = TRUE)),
      dboh_ids      = paste(sort(unique(dboh_id)), collapse = " "),
      strengths     = paste(sort(unique(strength)), collapse = "; "),
      n_rows        = n_distinct(dboh_id),
      citation      = str_sub(dplyr::first(ref), 1, 200),
      .groups       = "drop"
    ) |>
    mutate(across(c(cited_version, cited_year),
                  ~ ifelse(is.finite(.x), as.integer(.x), NA_integer_))) |>
    arrange(review_id)
}

# ---- every published version of one review ------------------------------
review_versions <- function(rid) {
  pmids <- esearch(paste0(rid, "[All Fields]"))
  if (!length(pmids)) return(tibble())
  s <- esummary(pmids)
  if (!nrow(s)) return(tibble())
  s |>
    bind_cols(parse_cochrane(s$doi)) |>
    # Searching the bare ID also returns commentaries and summaries that
    # merely mention the review. Keep only records whose own DOI is one of
    # its versions.
    filter(!is.na(version), !is.na(review_id), toupper(review_id) == toupper(rid)) |>
    arrange(version)
}

blank_result <- function(r, status) {
  mutate(r, status = status, latest_version = NA_integer_,
         latest_date = as.Date(NA), latest_pmid = NA_character_,
         latest_doi = NA_character_, versions_behind = NA_integer_,
         years_behind = NA_integer_, newest_ever = NA_integer_,
         newest_ever_date = as.Date(NA))
}

check_one <- function(r) {
  versions <- tryCatch(review_versions(r$review_id), error = function(e) {
    cli_alert_danger("{r$review_id}: lookup failed ({conditionMessage(e)})")
    tibble()
  })
  if (!nrow(versions)) return(blank_result(r, "lookup-failed"))

  at_edition <- filter(versions, !is.na(date), date <= EDITION_DATE)
  current <- if (nrow(at_edition)) slice_max(at_edition, version, n = 1, with_ties = FALSE)
             else slice_min(versions, version, n = 1, with_ties = FALSE)
  newest  <- slice_max(versions, version, n = 1, with_ties = FALSE)

  status <- if (is.na(r$cited_version)) "version-unknown"
            else if (current$version > r$cited_version) "SUPERSEDED"
            else "current"
  behind <- if (status == "SUPERSEDED") current$version - r$cited_version else 0L
  yrs <- if (status == "SUPERSEDED" && !is.na(r$cited_year))
           as.integer(format(current$date, "%Y")) - r$cited_year else 0L

  cli_alert(sprintf("%-9s cited pub%-3s current at edition pub%-3s (%s)%s",
    r$review_id, ifelse(is.na(r$cited_version), "?", r$cited_version),
    current$version, format(current$date, "%Y"),
    if (status == "SUPERSEDED") "  <-- SUPERSEDED" else ""))

  mutate(r, status = status,
         latest_version = current$version, latest_date = current$date,
         latest_pmid = current$pmid, latest_doi = current$doi,
         versions_behind = as.integer(behind), years_behind = as.integer(yrs),
         newest_ever = newest$version, newest_ever_date = newest$date)
}

report <- function(res) {
  bad <- filter(res, status == "SUPERSEDED") |> arrange(desc(versions_behind))
  cli_h2("Superseded at the edition's own publication date: {nrow(bad)} of {nrow(res)}")
  if (!nrow(bad)) {
    cli_alert_success("Every cited Cochrane review was current on 10 September 2025.")
    return(invisible(res))
  }
  for (i in seq_len(nrow(bad))) {
    b <- bad[i, ]
    cli_par()
    cli_text("{.strong {b$review_id}} cited pub{b$cited_version} ({b$cited_year}); ",
             "current was pub{b$latest_version} ({format(b$latest_date, '%Y')})")
    cli_bullets(c(
      "*" = "{b$versions_behind} version{?s} and {b$years_behind} year{?s} behind",
      "*" = "affects {b$n_rows} row{?s}: {b$dboh_ids} [{b$strengths}]",
      "*" = "latest at edition: https://doi.org/{b$latest_doi}",
      "*" = "newest today: pub{b$newest_ever} ({format(b$newest_ever_date, '%Y-%m-%d')})"
    ))
    cli_end()
  }
  invisible(res)
}

main <- function(offline = FALSE) {
  ensure_dirs()
  path <- file.path(REGISTRY, OUT)
  if (offline) {
    if (!file.exists(path)) cli_abort("No saved results at {.path {path}}")
    return(report(read_csv(path, show_col_types = FALSE, progress = FALSE)))
  }

  reviews <- cited_reviews()
  cli_h1("Version currency of the Cochrane reviews DBOH cites")
  cli_alert_info("{nrow(reviews)} review{?s} across {sum(reviews$n_rows)} recommendation row{?s}.")
  cli_alert_info("Currency judged as at {format(EDITION_DATE, '%d %B %Y')}.")

  res <- map_dfr(seq_len(nrow(reviews)), ~ check_one(reviews[.x, ]))
  write_registry(res, OUT)
  report(res)
  invisible(res)
}

if (!interactive()) main(offline = "--offline" %in% commandArgs(TRUE))
