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

## Live results and remaining verification

The user ran the course API locally without sharing credentials. Three complete
32-case runs and assisted reviews are preserved under `evaluation/reports/`.
The third run records 24/26 correct full rulings, 24/26 sufficient citations and
6/6 appropriate refusals, meeting the configured development-suite thresholds.
All six answerable Chess cases use verified formal-law evidence and pass assisted
review; both Chess refusal cases also pass. These are known development cases,
not a held-out evaluation or a guarantee for all Chess questions.

Independent team confirmation is still required. PAN05 eradication scope and
DOM04 gained-card wording remain failures in the third run; see
`evaluation/reports/2026-10-23-third-run/README.md`. Earlier results were not
rewritten, and the fixed answer key has not been changed to fit model outputs.

The five-person adult usability study, shared hosting, course/source permission
confirmation and midterm recording/status sheet are not completed by this work.

Latest code validation: 48 automated tests passed with all local PDFs present;
offline designated-reference coverage is 21/26. This preflight metric is separate
from the actual live semantic grades above. Review-only documentation changes
after the third run do not change the tested generation code.
