# From skeleton to midterm demo

## Next build steps

1. Confirm the course API instructions (provider, endpoint, model, authentication and data-use terms). Never paste or commit the key.
2. Review the extracted passages and retrieval failures against the original PDFs. Six sources are indexed; confirm the remaining edition labels and separate Chess rules from commentary before AI use.
3. Implement the backend model adapter using retrieved evidence only. Validate citation IDs against retrieved passages. Add clarification and out-of-scope handling, including strategy and disputed-play requests.
4. Run a small real rules test with a source-checked answer key. Record actual outputs and failures. Do not count skeleton tests as ruling accuracy.
5. Run the proposed 32-case evaluation across all four games. The base/expansion source mapping is now implemented, but ranking and answers still need evaluation.

## Midterm handoff (26 October; Moodle cutoff is authoritative)

- A real input → processing → output demonstration in an MP4 of at most 60 seconds.
- `repository_link.txt`, accessible current code and reproducible README instructions. Upload/push only after the team approves; this starter does not do so.
- Completed companion one-page status template: real progress, test evidence, limitations, blockers with owners, three dated milestones over the next two weeks, each member’s actual contributions and scope decision.
- ZIP at most 100 MB; verify playback, staff repository access and Moodle group receipt.

The local search prototype now retrieves real passages and page references, but is not the completed AI core workflow. The team still needs to connect the model, verify its outputs and record the working path. Never present keyword results as generated AI answers.
