# Chess law extraction and evaluation tooling — 23 October 2026

## Chess change

The prior safeguard correctly kept all mixed Chess text search-only. The new
extractor classifies all 52 selected pages of the exact pinned 2025 manual:

- PDF pp.16–56: upright Times New Roman body/bold text at >=11.5pt is law text.
  Italic/smaller/other typography is excluded from law evidence.
- PDF pp.57–62: non-law guidelines, explicitly described as not part of the
  Laws by the source. These are not official-law evidence.
- PDF pp.63–67: reference glossary, not official-law evidence.

The original PDF is unchanged. The filter operates on an in-memory content
stream while preserving original byte encoding and text positioning. It is a
format-specific extractor, not a general guarantee for other editions. Diagrams,
small symbols and unfamiliar typography are excluded conservatively; questions
requiring them may still need a refusal or original-source inspection.

The manual SHA-256 must match the reviewed file. At runtime, each Chess passage
ID, page and text must match a fresh cached extraction before it is eligible for
model use. Stored kind/profile flags alone cannot enable an answer. Missing or
misleading legacy index fields and altered text remain blocked. Verified text
can therefore reach the course model while annotation material cannot.

Rebuild with `python -m referee.indexer`. The current index has 227 passages,
including 41 verified Chess-law passages. Keep the generated index local.
Examples checked include the page-24 castling restrictions and page-37 law text
versus the separate commentary; Unicode punctuation/encoding is regression-tested.

## Evaluation work completed

Prepared a frozen 32-case key with source locations and expected rulings, plus
reference checking, sequential live execution, checkpointed outputs, a review CSV
and threshold scoring. See `evaluation/README.md`. Source-checked references are
not model outputs, and automated program tests do not establish answer accuracy.

The initial retrieval preflight found all designated evidence for 13/26 answerable
cases. General retrieval changes improve this to 19/26; the missing anchors are
recorded openly. These are development diagnostics before a scored live run.

## Remaining verification

No new live course API requests were made by the assistant because the course
key is entered interactively and is not stored. A member must run the live suite
and review the outputs. The current extraction enables the Chess path in code;
a correct live Chess response is still to be observed. Improve failures and
rerun the unchanged suite, retaining the earlier results.

The five-person adult usability study, shared hosting, course/source permission
confirmation and midterm recording/status sheet are not completed by this work.

Final local validation: 44 automated tests passed with all local PDFs present;
the offline 32-case run completed with 19/26 designated-reference coverage.
No model accuracy score has been produced.
