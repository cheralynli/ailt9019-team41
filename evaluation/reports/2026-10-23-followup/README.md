# Second live review — 23 October 2026

Run `20261023T083311521478Z` used `qwen3.8-flash` at clean commit
`c03c3fb19971809028f78274a6c13db7b6407b8f`. All 32 cases completed with zero API
errors, using the same frozen suite and indexed corpus as the first run.
Original results were preserved. Review is assistant-assisted and conservative;
independent team confirmation remains pending.

| Measure | First run | Second run | Required |
| --- | --- | --- | --- |
| Correct full rulings | 22/26 | 24/26 | 21/26 |
| Sufficient actual citations | 21/26 | 23/26 | 24/26 |
| Appropriate refusals | 6/6 | 6/6 | 6/6 |

The second run **does not pass** the citation threshold. These are developmental
results on a known fixed suite, not an independent held-out evaluation. No scored
answer, frozen case, or original run was rewritten to obtain a higher score.

## Fixed cases

CAT02 no longer adds unsupported mandatory trading timing. CAT05 now cites both
the shipping-route rule and base distance rule. CAT06 now correctly answers and
cites both ship cost and construction-turn movement. All six answerable Chess
rulings remain correct on the fixed questions. Both Chess refusal cases remain
appropriate.

## Outstanding cases

- **PAN01:** Still states exactly four actions, rather than up to four. Retrieved
  charts/examples show four actions but omit the explicit allowance on PDF page
  4. The frozen answer key's page 3 anchor locates the turn chart; page 4 is the
  stronger source for its expected optional-limit wording. This source-location
  clarification does not change the frozen question or expected answer.
- **PAN05:** Correctly states all-cures victory, but still describes eradication
  as preventing new cubes in cities of that color. This overbroad statement
  excludes other disease colors. Both full ruling and citations fail.
- **CHE05:** Correct king-capture prohibition and checkmate victory, but only
  cites PDF page 17 while also claiming immediate game end. The explicit timing
  provision is on page 28. Full ruling passes; citation sufficiency fails. The
  first run cited both locations, so this is a citation regression.

`review.assisted.csv` records all 32 decisions, generated answers, compact actual
source references and reasons. The summary includes input provenance and the
original raw-output hash. Full rulebook excerpts and credentials are not included.

## Follow-up changes, not yet validated by another live run

Count questions now prioritize an explicit numeric allowance/limit sharing the
question's subject, rather than relying on a worked example. Regression checks
confirm the retrieved evidence includes the actual up-to-four sentence for two
phrasings. The prompt adds a final cited-evidence check for immediate timing,
optional limits and disease-cube color, and limits comparison answers to the
requested defining distinction and outcome. All 48 automated tests pass without
live provider calls. Offline designated-anchor coverage remains 21/26; this is
not model accuracy and does not count alternative valid citations.

Run the same 32-case live evaluator again and review all outputs for regressions.
Do not combine a few new passing answers with previous outputs and describe it
as a new complete run. Prompt instructions do not guarantee semantic correctness.
