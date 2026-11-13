# Complete live evaluation — 12 November 2026

Run `20261112T155755901888Z` completed all 32 frozen v1 cases at clean commit
`159e217` using `qwen3.8-flash`. Lu Weidi manually compared each recorded
answer and citation with the frozen key and original PDFs. The reviewed result
is 26/26 correct rulings, 26/26 supported citations and 6/6 correct refusals.
This exceeds the configured thresholds of 21, 24 and six.

The run contains 26 answer states, five refusal states and one unsupported
cross-game state. DOM04 and PAN05 are literal source-extractive answers and use
zero provider requests. CAT02 gives only the required settlement resources and
does not repeat the unsolicited sequencing statement that failed the 6 November
run. CAT08 declines strategy advice, and CHE07 rejects a combined
Monopoly/Chess request without inventing a ruling.

This is a manual human review by a project member, not an independent or
held-out assessment. The suite was used during development, so the result does
not establish accuracy on new phrasings. Original outputs, metadata and the
completed review CSV remain in the local result directory and were not edited.
The compact score and run metadata are recorded in `summary.json`.
