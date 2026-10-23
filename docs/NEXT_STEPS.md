# From course API integration to midterm demo

## Working now

- Python retrieval feeds server-side course API explanations with validated source IDs.
- Course API adapter added on 21 October: `qwen3.8-flash`, configured through COURSE_MODEL.
  Three user-observed browser cases are recorded in `COURSE_API_PROGRESS_2026-10-21.md`; screenshots do not include provider metadata.
- Hidden key prompt, live connection check, model listing and safe failure diagnostics.
- The rebuilt six-document corpus produces 227 indexed passages. Source URLs and hashes are tracked;
  PDFs and generated excerpts remain ignored.
- One live Catan distance-rule example was observed in the browser on 19 October
  2026. See `docs/API_PROGRESS_2026-10-19.md` for evidence and limitations.

## Next build steps

1. Have the testing owner confirm all 32 grades from the third preserved live run.
   Assisted review meets the configured thresholds (24/26 rulings, 24/26 citations,
   6/6 refusals); this is not independent human or held-out evaluation.
2. Retain and investigate PAN05 eradication-color scope and DOM04 gained-card
   wording failures. Do not describe the system as fully accurate. See
   `evaluation/reports/2026-10-23-third-run/README.md` for all decisions.
3. Expand testing beyond the known development suite, including ambiguity and
   realistic user tasks. Do not deliberately exhaust quota to test API failures;
   those paths also have automated mocked coverage.
4. Review the pinned Chess extraction and source-use permissions. Six answerable
   Chess questions now have correct live formal-law answers in the fixed suite;
   this is not evidence about all Chess positions, diagrams or dispute scenarios.
5. Confirm deployment arrangements and prepare the adult usability study.
   The current server remains a local development server.

## Midterm handoff (26 October; Moodle cutoff is authoritative)

- MP4 of at most 60 seconds showing a real input → processing → output.
- repository_link.txt, staff repository access and reproducible README instructions.
- One-page Word status sheet: progress, evidence, limitations, blockers and owners,
  three dated milestones, each member's completed work and scope decision.
- ZIP at most 100 MB; verify playback and Moodle group receipt.

See `WEEK8_REVIEW_2026-10-23.md` for the submitted-proposal audit, website fixes,
verification boundaries and the Week 8 / Weeks 9–10 requirements.

The Chess source-policy bypass found during review was fixed; see
`CHESS_GUARD_FIX_2026-10-23.md`. The current automated suite has 48 passing tests.
These program checks are separate from the documented live evaluation grades.

The current extraction/evaluation implementation is documented in
`CHESS_AND_EVALUATION.md`; previous search-only descriptions are historical.
