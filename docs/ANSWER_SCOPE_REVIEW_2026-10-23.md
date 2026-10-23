# Bounded review for observed answer-scope errors

## Problem and resulting behavior

PAN05 repeatedly added an overbroad eradication claim about cities of a printed
color, rather than the color of the affected disease cubes. DOM04 once made a
card-effect condition apply to all future drawing/playing, rather than only the
immediate result of gaining. Their core answers were correct, but extra claims
failed conservative full-answer and citation review. More prompt instructions
alone did not consistently remove these errors.

The server now checks answer text for these known forms in the selected game.
It does not consult evaluation case IDs, expected answers or grading files.
A finding sends the original question/evidence, candidate draft and scope
feedback to the course model for one revision. The draft is explicitly untrusted
candidate text, not an instruction or new evidence. The revised JSON, status and
citation IDs are validated again against the original local evidence.

If the revised answer still matches a known unsafe form, it is not displayed.
The server returns a refusal with no citations and the sanitized diagnostic
`answer_scope_unresolved`. A safe-looking revision is not a guarantee of semantic
correctness: these checks cover observed English forms, not arbitrary paraphrases,
all game rules, or all possible claims. A conservative check can also flag a
context-dependent statement that a human might accept; source review remains
necessary. No rules are replaced with benchmark answer strings.

## Request budget and UI

A normal answer or refusal uses one provider request. A detected scope error may
use one additional sequential request; there are no content-revision loops and
no transport retries. A 32-case run uses at most 64 calls. The shared quota and
one-in-flight-call-per-process limit still apply. Each call keeps the existing
45-second provider timeout; the browser wait is extended to 110 seconds to allow
for revision. An interrupted browser request does not guarantee cancellation of
an already running server call.

Successful revisions include `answer_review` metadata (revision count and finding
codes) in the recorded evaluation output. Persistent failures include the
unresolved codes. The evaluator records the per-case request bound in run
metadata. Raw provider errors and credentials are never included. The draft and
same evidence may be sent to the same course provider during a revision; normal
app requests still do not create chat logs.

## Validation and limits

- All 58 automated tests passed, with provider calls mocked.
- New tests replay three observed Pandemic error forms and the Dominion error,
  distinguish focused statements and explicitly immediate gain exceptions,
  verify revised citation validation, bound the call count to two, and reject a
  persistent bad revision without displaying its answer.
- Offline replay considered all 96 responses in the three preserved live runs.
  It flagged PAN05 in all three, plus DOM04 in the third, with no other responses
  flagged. This checks detection on known examples, not repair quality or
  correctness of unflagged responses. Details: `evaluation/scope-replay.json`.
- JavaScript syntax and whitespace checks passed. The frozen 32-case key and
  all original results remain unchanged. The third-run assisted score is still
  historical (24/26 rulings, 24/26 citations, 6/6 refusals).

**A new live run and manual/assisted review are still required.** This change
has not yet demonstrated that the real model successfully revises PAN05 or
DOM04; if it refuses after a failed revision, that answerable case must still
be graded incorrect. Run `zsh scripts/start-course.zsh --evaluate`, preserve
all 32 new outputs, inspect revision metadata, and review all cases for regressions.
Independent team confirmation of final grades remains pending.


## Fourth-run observation

The fourth live run did not trigger a revision. DOM04 was initially correct;
PAN05 still said “cities of that disease color,” which escaped the original
pattern. The check now covers this variant and feedback explicitly rejects
moving the color qualifier to cities. This exact new clause is regression-tested,
as is a safe statement that qualifies the cubes themselves. A successful live
revision is still unverified. Use the focused `--cases PAN05 DOM04` run before
another full-suite run; focused results cannot establish an aggregate pass.


## Source-extractive alternative after the focused run

The focused run still added unsupported claims without triggering a revision.
The two explicit rule intents now use complete literal retrieved-source answers
before model generation, labeled RULEBOOK EXCERPTS. No API request is made when
this source path succeeds; absent required text falls back to the model path.
These curated source spans and intent matching are not a general semantic
validator or an independent benchmark method. Runtime code never reads case IDs
or expected answers. Other question intents retain the bounded scope checks.
Both targets pass local production-pipeline tests with real sources and provider
calls blocked; all 64 tests pass. See
`evaluation/reports/2026-10-23-focused-source-excerpts/README.md` for the full
preserved observation, extraction policy and validation limits.
