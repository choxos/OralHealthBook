.DEFAULT_GOAL := help
SHELL := /bin/bash

PDF  := dist/The-Evidence-Behind-KDP-6x9.pdf
EPUB := dist/The-Evidence-Behind-KDP-6x9.epub

.PHONY: help web print read pdf epub covers check preview clean deep-clean kdp all extract

help:  ## Show this help
	@grep -hE '^[a-z-]+:.*?##' $(MAKEFILE_LIST) \
	 | awk 'BEGIN{FS=":.*?## "}{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

web:  ## Build the free website into _book/
	quarto render --profile web

# One invocation, not two. Quarto cleans output-dir on each render, so
# `make pdf && make epub` leaves only the epub.
print:  ## Build both paid-edition formats into dist/
	quarto render --profile print

read:  ## Build the A4 single-sided reading copy into dist-reading/
	quarto render --profile read --to pdf

pdf: print  ## Build the KDP paperback PDF (builds the epub too)

epub: print  ## Build the Kindle EPUB (builds the PDF too)

covers:  ## Regenerate cover art (paperback spine tracks the PDF page count)
	python3 scripts/make_cover.py

check:  ## Run the citation and chapter-completeness checks
	python3 scripts/check_citations.py

check-strict:  ## Same, but draft gaps are errors. Run before publishing.
	python3 scripts/check_citations.py --strict

preview:  ## Live-reload the website
	quarto preview --profile web

validate: $(EPUB)  ## Validate the EPUB against the EPUB 3 spec
	@command -v epubcheck >/dev/null 2>&1 \
	  || { echo "epubcheck not installed: brew install epubcheck"; exit 1; }
	epubcheck $(EPUB)

kdp: check pdf epub covers validate  ## Full pre-upload build for Amazon
	@echo
	@echo "KDP upload package:"
	@ls -lh dist/ figures/cover-paperback.png figures/cover-ebook.png
	@echo
	@pdfinfo $(PDF) | grep -E 'Pages|Page size'
	@echo "Interior must be 432 x 648 pts. Spine width on the wrap is"
	@echo "computed from the page count above; if the count changed,"
	@echo "'make covers' again before uploading."

all: check web print covers  ## Everything

clean:  ## Remove build output, keep the freeze cache
	rm -rf _book dist dist-reading

deep-clean: clean  ## Also drop the Quarto freeze cache
	rm -rf .quarto _freeze

extract:  ## Re-extract DBOH 2025 into appraisals/, _variables.yml and the appendices
	python3 scripts/extract_dboh.py
	python3 scripts/make_appendices.py
