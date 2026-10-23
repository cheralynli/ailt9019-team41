# Fixed rules evaluation v1

The source-checked baseline contains exactly 32 cases (eight per game):
16 ordinary, six requiring two source locations, four game/ruleset routing
checks, and six refusals. The refusals comprise two missing-data cases,
two unsupported/cross-game cases, one strategy request and one disputed-event
request. It was prepared before any scored live run. Independent team review of
the answer key is recommended before running the benchmark.

`cases.v1.sha256` freezes the file. A later correction needs a new version and
an explanation, not a silent edit to make a model output pass. Each answerable
case supplies a paraphrased expected ruling plus source ID, PDF page and a
short location anchor. Anchors are checked against local originals (law-only
extraction for Chess). They locate the rule; matching an anchor does not prove
semantic correctness. Missing-data refusals have scope explanations rather than
invented citations.

## Three distinct steps

1. `python scripts/evaluate.py`: offline retrieval preflight. No provider calls.
2. `zsh scripts/start-course.zsh --evaluate`: hidden group-key prompt, sequential
   live answers, evidence and CSV review sheet. Up to 32 calls; explicit scope
   refusals may be handled locally. Do not run multiple evaluators at once.
3. Review the original PDFs and recorded outputs, fill the CSV, then run
   `python scripts/evaluate.py --score evaluation/results/RUN/review.csv`.

For answerable cases, mark ruling_correct=yes only if the ruling, game, edition,
exceptions and timing agree with the key. Mark citation_correct=yes only if the
actual cited locations support all essential claims; the two-part cases require
support for both parts. Do not require exactly the gold location if a different
correct passage supports the same facts. For refusal cases, mark refusal_correct
only if the system appropriately declines without an invented ruling. An API
error or search-only response is not a correct model answer/refusal. Record
reviewer and reasoning in the notes column.

Scoring uses independent denominators: 26 for rulings, 26 for citations and six
for refusals. Thresholds are 21, 24 and six respectively. Every required field
must be reviewed before a pass is reported. A partial run is not complete.

## Artifacts and privacy

Each timestamped local results directory contains metadata.json, outputs.json,
review.csv and summary.json. It is Git-ignored to prevent accidental publication
of unreviewed results. No credentials are recorded. Metadata identifies the
model, suite/corpus hashes and Git commit/dirty state. Preserve original runs
before fixes and retest the same cases. After reviewing and removing anything
unintended, the team may deliberately attach the report for assessment.

## Current preflight result

The first law-separated, original-retrieval preflight covered all specified
locations/anchors for 13/26 answerable cases. General stemming, phrase matching,
larger page-bounded excerpts and six-result retrieval improved this to 19/26.
This is a development diagnostic, not a scored rules-test result. At that stage seven cases
still missed at least one specified anchor; see preflight.latest.json. Alternate
correct passages may exist, so live answers and their actual citations still
need review. No live accuracy or pass rate is claimed.


## First live baseline and follow-up

The first complete live run and assistant-assisted review are recorded in
[the baseline report](reports/2026-10-23-baseline/README.md). Conservative scores
are 22/26 full rulings, 21/26 sufficient citations and 6/6 refusals; the citation
threshold is not met. Independent team confirmation is pending. Subsequent
retrieval/prompt fixes require a new live run, not rescoring edited answers.

The post-baseline ship retrieval fix covers 21/26 designated reference sets in
the offline preflight. This remains separate from live semantic grading.
