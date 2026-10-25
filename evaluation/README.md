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
   live answers, evidence and CSV review sheet. Up to 64 sequential calls (at most
   two per case if a recognized scope error requires a content revision); explicit scope
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
still missed at least one specified anchor. Alternate
correct passages may exist, so live answers and their actual citations still
need review. This preflight makes no live accuracy claim; actual run reviews
are linked below.


## First live baseline and follow-up

The first complete live run and assistant-assisted review are recorded in
[the baseline report](reports/2026-10-23-baseline/README.md). Conservative scores
are 22/26 full rulings, 21/26 sufficient citations and 6/6 refusals; the citation
threshold is not met. Independent team confirmation is pending. Subsequent
retrieval/prompt fixes require a new live run, not rescoring edited answers.

The post-baseline ship retrieval fix covers 21/26 designated reference sets in
the offline preflight. This remains separate from live semantic grading.


The [second live review](reports/2026-10-23-followup/README.md) improves to
24/26 rulings and 23/26 sufficient citations, with 6/6 refusals. It still misses
the citation threshold. PAN01/PAN05 remain incorrect in scope, and CHE05 has a
citation timing regression. Another live run is required after the count-search
and final cited-evidence-check changes. Independent team confirmation is pending.


The [third complete live review](reports/2026-10-23-third-run/README.md) records
24/26 correct full rulings, 24/26 sufficient citations and 6/6 refusals. This
meets configured development-suite thresholds under assistant-assisted review;
independent team confirmation remains pending. PAN05 and DOM04 are retained as
failures. No raw outputs or frozen cases were edited, and no outputs from
different runs were combined. These are development results on a known suite,
not a held-out evaluation or a guarantee of correctness for other questions.


## Scope-check revision follow-up

The next live run may include one content revision per case for a recognized
Pandemic eradication-color or Dominion gain-event scope error. Review the final
answer and its actual citations, plus `answer_review` metadata where present.
A refusal after an unsuccessful repair is still a failed answerable case; never
credit detection alone as a correct answer. No transport failures are retried.
The offline detection replay is in `scope-replay.json`; it is not a new live
score. See `../docs/ANSWER_SCOPE_REVIEW_2026-10-23.md` for validation and limits.


## Fourth live run and focused follow-up

The [fourth complete run](reports/2026-10-23-fourth-run/README.md) records
25/26 rulings, 25/26 sufficient citations and 6/6 refusals under assisted review.
DOM04 passes without a revision; PAN05 still fails because a new city-color
wording escaped the initial detector. No successful live revision is established.
The subsequent detector extension needs another real check. Original grades
and results remain unchanged; independent team confirmation is pending.

To check only the two target cases before spending quota on another full run:

```sh
zsh scripts/start-course.zsh --evaluate --cases PAN05 DOM04
```

The original frozen questions are used. Focused runs cannot establish a complete
32-case pass and `--score` still requires all 32 distinct IDs. Do not combine a
focused run with earlier passing outputs and call it a fresh complete run.


## Source-extractive follow-up to the focused run

The next implementation uses complete literal source excerpts for two narrow
rule intents when all required sentences are retrieved. These answers are labeled
`answer_method=source_excerpt`, with zero provider requests, and must not be
reported as model-generated explanations. Other intents keep their existing API
path. The curated extraction policy was added after development-case failures.

Both targets pass local, real-corpus citation checks through the production
pipeline with provider calls blocked; this is not a new live 32-case result.
The last full run's grades remain unchanged. See
[the focused review and validation](reports/2026-10-23-focused-source-excerpts/README.md)
for provenance, literal outputs, scope and independent-review requirements.
