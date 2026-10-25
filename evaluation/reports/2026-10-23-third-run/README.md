# Third live review — 23 October 2026

Run `20261023T083913914896Z` used `qwen3.8-flash` at clean commit
`7dc721dd469af52521e3a3e24d8b0dcb0cd18306`. All 32 cases completed without API
errors. The suite and corpus hashes match both previous runs. Every actual
citation ID, source ID, page, text and classification matches the validated local
corpus; this integrity check alone does not establish semantic correctness.

| Measure | First run | Second run | Third run | Required |
| --- | --- | --- | --- | --- |
| Correct full rulings | 22/26 | 24/26 | 24/26 | 21/26 |
| Sufficient actual citations | 21/26 | 23/26 | 24/26 | 24/26 |
| Appropriate refusals | 6/6 | 6/6 | 6/6 | 6/6 |

**Configured development-suite thresholds are met under assistant-assisted,
conservative review. Independent team confirmation is pending.** This is not a
claim of perfect accuracy, an independent human evaluation, or held-out model
performance. The suite was used during development. Original runs and frozen
cases were preserved; no passing answers from different runs were combined.

## Resolved in this run

PAN01 now says up to four actions and cites the explicit allowance on PDF page
4. CHE05 now cites both the king-capture/checkmate rule and the immediate-ending
rule on PDF pages 17 and 28. The previous Catan fixes remain effective. All six
answerable Chess questions and both Chess refusal questions pass assisted review.

## Known failures retained

- **PAN05:** The core all-cures win and cure/eradication contrast are correct, but
  the added prevention clause still describes cities of a color rather than
  restricting the affected disease-cube color. Other colors can enter those
  cities through outbreaks. Full-answer correctness and citation sufficiency
  remain marked no.
- **DOM04:** The default discard destination and no immediate play are correct.
  A new final sentence says the gained card only enters hand or gets played when
  a specific card effect instructs it. Without an immediate-on-gain qualifier,
  this excludes ordinary later draw/play. The cited page 7 does not support that
  broader restriction. Both fields are marked no conservatively; the team should
  confirm this scope judgment. This is a regression from earlier focused answers.

`review.assisted.csv` contains all 32 generated answers, compact actual source
references, decisions and reasons. `summary.json` records the original-output
hash and run metadata. Full copyrighted excerpts and credentials are omitted.
The timestamped original results and separate full assisted review stay local.

The latest implementation passed 48 automated tests before this run. This
follow-up only adds review artifacts and updates status documentation; it does
not change the tested generation code. Offline designated-anchor coverage is
21/26 and is not an accuracy score. Alternative valid citations were accepted.

## Handoff

The team can review and merge the implementation with these known limitations
explicitly recorded. A human testing owner should confirm all grades and review
the two wording failures. Improve them in a later change with regression checks
and another preserved complete run; do not claim they are fixed by this report.
The adult usability study, hosting and midterm deliverables remain separate work.
