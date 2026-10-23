# Fourth live review — 23 October 2026

Run `20261023T110703343791Z` used `qwen3.8-flash` at clean commit
`a8288812c828707a8ea11a5473f2ca6febd11eae`. All 32 cases completed without API
errors using the unchanged frozen suite and corpus. Every recorded citation ID,
source ID, page, text and classification matches the validated local corpus.

Assistant-assisted conservative review records **25/26 correct full rulings,
25/26 sufficient citations and 6/6 appropriate refusals**. Configured development
thresholds are met; independent team confirmation is pending. This known suite
was used during development and is not a held-out evaluation. Original outputs
and frozen cases were not edited or combined across runs.

## Target cases

- **DOM04 passes this run.** It correctly states the default discard destination
  and no immediate play, without making special card effects a prerequisite for
  ordinary later drawing or playing. There is no `answer_review` metadata, so
  this is a correct initial answer, not evidence of a successful revision.
- **PAN05 still fails.** The core win and cure/eradication distinction are correct,
  but the extra sentence says no new cubes are placed in cities of “that disease
  color.” Cube-color scope is still not preserved. The inserted word “disease”
  escaped the deployed detector, so no revision was requested. Both full-answer
  correctness and citation sufficiency remain no.

No answers in this run include `answer_review`; the live repair path has not
been demonstrated yet. The other 30 cases pass assisted review, including six
answerable Chess questions, both Chess refusals, the previous Catan fixes and
the explicit up-to-four Pandemic allowance.

## Subsequent change and validation

The detector now also covers “cities of that disease color,” while accepting an
explicit restriction on the cube color itself. Revision feedback explicitly
states that inserting “disease” after “cities” is not a valid scope repair and
asks the model to omit unrequested placement claims. A regression fixture uses
the exact new unsafe clause. These changes cannot retroactively repair this run.

All 58 program tests pass with mocked provider calls. The evaluator also supports
`--cases PAN05 DOM04` for a low-cost focused check using the original questions.
A focused run records `run_complete=false`, cannot be scored as a complete suite,
and does not change the fixed answer key. After verifying the target answers,
use a fresh complete 32-case run if a new aggregate score is required.
