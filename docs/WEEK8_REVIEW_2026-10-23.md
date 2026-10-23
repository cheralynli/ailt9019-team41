# Week 8 proposal and website review — 23 October 2026

## Basis

Reviewed the team-supplied submitted revised proposal (five pages, revised due
10 October), the current course-api branch, original rulebook provenance,
automated tests and a local browser preview. This report does not modify the
proposal or claim that unperformed evaluations have passed.

## What should be complete this week?

Week 8 is 19–25 October. Section 6 calls for adding Chess and Dominion, indexing
all six documents, freezing the source-checked 32-case answer key and running the
full evaluation (eight cases per game). Week 7 had called for a working cited
Catan/Pandemic prototype plus clarification/refusals and API/source checks.

| Requirement | Evidence now | Remaining work |
| --- | --- | --- |
| Course API integration | Adapter, hidden-key startup, user-supplied browser evidence | Rerun updated prompt with the actual group key |
| Six indexed documents | 467 excerpts; six pinned local files hash-verified | Permissions confirmation; extraction quality review |
| Catan and Pandemic core workflow | User-observed answers and strategy refusal | Expanded accuracy tests; precise Pandemic timing retest |
| Dominion | Indexed, routed and local retrieval tested | Real API answer and citation verification |
| Chess with commentary distinguished | Mixed excerpts explicitly labelled search-only | Separate and verify rules/commentary before enabling AI answers |
| Fixed 32-case evaluation | No completed answer key or scored run found in this checkout | Test owner freezes source-checked cases and records actual outputs |
| Shared deployed URL | Only localhost development server found | Deployment owner supplies accessible app URL |
| Player-first README | Added walkthrough and per-game response expectations | Validate with intended users |

The revised source table explicitly permits an unstated Dark Ages edition and an
unconfirmed English Pandemic PDF edition. Keep these labels honest; they are
not evidence of a newly introduced mismatch. The revised Chess source is the
2023 Laws plus commentary in PDF pages 16–67 of the 2025 Arbiters’ Manual,
matching this repository's source choice; separation remains unfinished.

## Fixes in this update

1. Replace the fixed “no AI connected” banner with server configuration and model
   information; no credentials are returned. Configured is not a live health or
   quota guarantee. Clearly display Chess as search-only.
2. Clear the previous answer, sources and submitted-question label when changing
   game/ruleset or selecting a new sample. This avoids presenting an old answer
   as applying to a new edition.
3. Label answer, refusal, clarification, unsupported input and API errors
   distinctly. Obvious unresolved references receive clarification before
   retrieval; explicit known mismatched game names are rejected.
4. Strengthen the prompt to preserve exceptions and timing boundaries, including
   “current Infection card” rather than the entire infection step. This is a
   prompt change, not proof that future live answers satisfy the condition.
5. Add a player walkthrough before developer instructions and a sequential
   official-source download script with exact hash validation. It refuses
   publisher file changes rather than silently altering the corpus.

The scope rules are deliberately conservative and do not implement a complete
semantic classifier. Chess remains blocked for AI use rather than treating
mixed commentary as official rules. No fabricated test outcomes or edited live
response screenshots are included.

## Verification

- 31 automated tests passed with all local PDFs/index files present. Provider
  requests are mocked; this does not measure real rule accuracy.
- `python scripts/download_rulebooks.py --check-only`: all six files verified.
  This checks the existing corpus; a fresh network download was not rerun.
- JavaScript syntax and Git whitespace checks passed.
- Local browser, without API credentials: accurate local-search banner;
  “Can I do that?” produces clarification; switching game resets the result;
  Chess displays its mixed-source warning and source excerpts.
- Live course-model answers after this update have not been retested because
  the key is supplied interactively by the member and is not stored in the repo.

## Group actions before and after the midterm

Midterm is due Monday 26 October (exact Moodle cutoff controls). Prepare a
real running workflow recording of at most 60 seconds, repository_link.txt,
and the completed one-page Word status sheet in one ZIP no larger than 100 MB.
Report the current limits and owners honestly; do not present all four games or
the full evaluation as complete. Ensure staff can access the submitted code.
The course API changes are in PR #1 until the team reviews and merges them.

For the fixed rules evaluation, the proposal requires 16 ordinary questions,
six needing two passages, four game/edition-boundary cases and six refusals:
26 answerable cases total. Pass requires at least 21/26 correct rulings,
24/26 supported citations and all six expected refusals.

Weeks 9–10 require five university students aged 18+ outside the team. Each
selects a game/edition, asks a sample question, locates a citation and recognises
a refusal. At least four of five must complete all four tasks without coaching.
Recruitment, observations and outcomes must be recorded, not inferred from
technical tests. Optional cached demos or a reusable skill come after must-haves.

Suggested ownership: API maintainer handles connection/configuration failures;
retrieval/source owner handles Chess separation; testing owner owns the frozen
answer key, Pandemic retest and usability study; deployment/submission owners
handle shared access, recording and the status sheet. Agree names as a team.
