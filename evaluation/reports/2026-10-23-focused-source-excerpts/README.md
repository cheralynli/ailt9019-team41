# Focused live review and source-extractive follow-up

## Preserved focused run

`20261023T111457076868Z` contains only DOM04 and PAN05 at clean commit
`13bfdd13f7725f3155cdf753e5ef4355641305f7`. Neither answer records a revision.
Both core rulings are correct, but additional claims are not fully supported by
the actual cited excerpts:

- DOM04 adds an exclusive Action/Buy-phase statement not established by its sole
  page-7 citation. The default discard destination and no immediate play are correct.
- PAN05 removes the previous city-color mistake but adds the Scientist four-card
  exception without citing its supporting source. Correct information elsewhere
  in the supplied evidence does not make an omitted citation sufficient.

This is a focused diagnostic, not a new 32-case score. The original outputs are
unchanged; `focused-live-review.json` records their hash and compact references.
These are assistant-assisted judgments pending independent team confirmation.

## Resulting implementation

Repeated prompt and pattern changes did not reliably stop unnecessary extra
claims. Two narrowly defined question intents now use **source-extractive
answers**, explicitly not generated explanations:

1. The default destination of a gained Dominion card and whether it is played
   immediately: quote the Supply-to-discard instruction, no-immediate-play rule
   and default-destination exception from the retrieved base rulebook.
2. Whether all four cures win with cubes remaining, contrasted with eradication:
   quote the all-cures win, cured-cubes-remain rule, eradication condition and the
   safeguard that removing an uncured disease's last cube has no effect.

Each displayed rule sentence must occur verbatim in a retrieved allowlisted
source with citation metadata. No page, URL, rule paraphrase or extra effect is
invented. If any necessary sentence is missing, the normal course-model path
remains available; no incomplete source answer is silently emitted. Matching
also requires the selected game and question intent. The frozen suite, case IDs
and expected-answer files are not consulted by runtime answering code.

This curated extraction policy was added during development, after observing
failures. It is not an independent benchmark discovery. Its source sentences and
selection are explicit in `referee/source_excerpt.py`, and unseen intents, source
wording, diagrams and other rules still need evaluation. Literal quotation limits
generative scope errors; a human must still check the relevance and completeness
of selected context. No guarantee is made for every paraphrase.

The UI labels these results **RULEBOOK EXCERPTS**, rather than AI explanations.
The configured answering path consumes zero provider requests for a complete
source-excerpt answer. Other questions still use the course API and existing
bounded revision checks. The server key configuration policy is unchanged.

## Validation

`local-excerpt-validation.json` records both original questions through the
production in-process pipeline, using the real indexed corpus, with provider
calls blocked and a synthetic configuration flag. Each displayed rule sentence
was verified literally inside its actual citation. Source-extractive answers
match only the two target cases in the fixed suite; the other 30 retain their
existing answering paths. Missing evidence, wrong source/metadata and alternate
wordings are covered by regression checks.

All 64 automated tests pass. JavaScript syntax and whitespace checks pass. These
are local deterministic checks, not a new live model run or a new aggregate
accuracy score. The last complete assisted live score remains 25/26 rulings,
25/26 citations and 6/6 refusals from the fourth run. Do not replace its two
focused outputs and call the merged set a new complete run. Independent team
confirmation is still pending; a fresh full run is needed for any new total.
