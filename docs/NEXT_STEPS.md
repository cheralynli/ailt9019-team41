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

1. Extend the observed strategy-refusal example with missing evidence, ambiguous questions and API failures
   with real inputs. Automated mocks do not verify model refusal behaviour.
2. Retest Pandemic chain reactions: the observed answer used “infection step” where the source says “current Infection card”.
3. Review the pinned Chess law extraction and run a live Chess answer test.
   Verified law-only excerpts are now eligible; commentary stays excluded.
4. Review the prepared frozen 32-case key, run `start-course.zsh --evaluate`,
   and grade the saved outputs as described in `evaluation/README.md`.
5. Run the course API live check with the emailed group key; confirm source-use permissions and deployment arrangements.
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
`CHESS_GUARD_FIX_2026-10-23.md`. The current automated suite has 33 passing tests.
This does not replace Chess source separation or the live 32-case evaluation.

The current extraction/evaluation implementation is documented in
`CHESS_AND_EVALUATION.md`; previous search-only descriptions are historical.
