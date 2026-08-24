## Shared helpers for the living evidence pipeline.
##
## Everything under scripts/living/ is R. The book's own toolchain
## (extract_dboh.py and friends) stays Python for now; this is a separate
## system with a separate lifecycle, and it reads the book's CSV output
## rather than its code.

suppressPackageStartupMessages({
  library(dplyr)
  library(stringr)
  library(tibble)
  library(purrr)
  library(readr)
  library(httr2)
  library(cli)
})

ROOT <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), "..", ".."),
                      mustWork = FALSE)
if (!dir.exists(file.path(ROOT, "appraisals"))) {
  ROOT <- normalizePath(getwd(), mustWork = TRUE)   # invoked from the repo root
}

LIVING   <- file.path(ROOT, "living")
REGISTRY <- file.path(LIVING, "registry")
DBOH_CSV <- file.path(ROOT, "appraisals", "dboh-2025.csv")

## The edition under surveillance. Currency is judged as at this date: a
## guideline can only be faulted for updates that already existed when it
## was published. Updates that appeared later are tracked separately, since
## they are what a living process would be catching now.
EDITION_DATE <- as.Date("2025-09-10")
EDITION_YEAR <- 2025

`%||%` <- function(x, y) if (is.null(x)) y else x

ensure_dirs <- function() {
  dir.create(REGISTRY, recursive = TRUE, showWarnings = FALSE)
}

# ---- Cochrane identifiers ------------------------------------------------
# Cochrane puts the version in the DOI: 10.1002/14651858.CD010216.pub9.
# A bare ID with no .pubN suffix is version 1.
RE_COCHRANE_DOI <- "10\\.1002/14651858\\.(CD\\d+)(?:\\.pub(\\d+))?"
RE_COCHRANE_ID  <- "\\b(CD\\d{6})\\b"
RE_YEAR         <- "\\b(19[5-9]\\d|20[0-2]\\d)\\b"

parse_cochrane <- function(x) {
  m <- str_match(x, regex(RE_COCHRANE_DOI, ignore_case = TRUE))
  tibble(
    review_id = toupper(m[, 2]),
    version   = ifelse(is.na(m[, 2]), NA_integer_,
                       ifelse(is.na(m[, 3]), 1L, as.integer(m[, 3])))
  )
}

newest_year <- function(x) {
  map_int(str_extract_all(x, RE_YEAR), function(y) {
    if (!length(y)) NA_integer_ else max(as.integer(y))
  })
}

# ---- NCBI E-utilities ----------------------------------------------------
# Rate limit is 3 requests/second, or 10 with a key. httr2 enforces it for
# us, so no hand-rolled sleeps and no accidental throttling.
EUTILS <- "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

eutils_req <- function(endpoint, ...) {
  key <- Sys.getenv("NCBI_API_KEY", "")
  req <- request(file.path(EUTILS, endpoint)) |>
    req_url_query(retmode = "json", ...) |>
    req_throttle(capacity = if (nzchar(key)) 8 else 2, fill_time_s = 1) |>
    req_retry(max_tries = 4, backoff = function(i) 2^i) |>
    req_user_agent("OralHealthBook living-evidence (github.com/choxos)")
  if (nzchar(key)) req <- req_url_query(req, api_key = key)
  req
}

eutils_json <- function(endpoint, ...) {
  eutils_req(endpoint, ...) |> req_perform() |> resp_body_json()
}

esearch <- function(term, retmax = 200) {
  res <- eutils_json("esearch.fcgi", db = "pubmed", term = term, retmax = retmax)
  as.character(unlist(res$esearchresult$idlist %||% list()))
}

#' Summaries for a set of PMIDs, as a tibble.
#'
#' PubMed reports dates as "2025/01/29 00:00". Comparing that to an ISO
#' string sorts "/" above "-", so every 2025 record silently fell outside a
#' `<= "2025-09-10"` filter in an earlier version of this tool and four
#' superseded reviews were reported as current. Dates are parsed to Date
#' here, once, so no caller can repeat that.
esummary <- function(pmids) {
  if (!length(pmids)) return(tibble())
  chunks <- split(pmids, ceiling(seq_along(pmids) / 200))
  map_dfr(chunks, function(ids) {
    res <- eutils_json("esummary.fcgi", db = "pubmed",
                       id = paste(ids, collapse = ","))
    map_dfr(ids, function(p) {
      r <- res$result[[p]]
      if (is.null(r)) return(tibble())
      doi <- r$articleids |>
        keep(~ identical(.x$idtype, "doi")) |>
        map_chr("value") |>
        first_or_na()
      tibble(
        pmid    = p,
        doi     = doi,
        title   = r$title %||% NA_character_,
        journal = r$source %||% NA_character_,
        date    = parse_pubmed_date(r$sortpubdate %||% r$pubdate %||% "")
      )
    })
  })
}

first_or_na <- function(x) if (length(x)) x[[1]] else NA_character_

parse_pubmed_date <- function(x) {
  x <- str_trim(str_replace(x %||% "", " .*$", ""))
  d <- suppressWarnings(as.Date(x, format = "%Y/%m/%d"))
  # Records dated to the month or year only ("2016/09", "2016") parse to NA
  # above; fall back to the first of the period rather than dropping them.
  if (is.na(d) && str_detect(x, "^\\d{4}/\\d{2}$")) {
    d <- as.Date(paste0(x, "/01"), format = "%Y/%m/%d")
  }
  if (is.na(d) && str_detect(x, "^\\d{4}$")) {
    d <- as.Date(paste0(x, "/01/01"), format = "%Y/%m/%d")
  }
  d
}

read_dboh <- function() {
  read_csv(DBOH_CSV, show_col_types = FALSE, progress = FALSE)
}

write_registry <- function(df, name) {
  ensure_dirs()
  path <- file.path(REGISTRY, name)
  write_csv(df, path, na = "")
  cli_alert_success("wrote {.path living/registry/{name}} ({nrow(df)} rows)")
  invisible(path)
}
