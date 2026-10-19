# Rulebook collection

`passages.json` is generated from the six allowlisted PDFs in `rulebooks/` by `python3 -m referee.indexer`. Both it and `index-report.json` are Git-ignored. The index contains normalized extracted text, not AI answers or a manually verified answer key.

After checking permission and verifying the source, extract passages into this shape:

```json
{
  "id": "unique-source-passage-id",
  "source_id": "allowlisted-source-id",
  "game": "catalogue-game-id",
  "edition": "catalogue-ruleset-id",
  "document": "Verified document title",
  "edition_label": "Human-readable edition",
  "page": 1,
  "kind": "rulebook_excerpt",
  "text": "Normalized text extracted from one PDF page."
}
```

This is a format example, not evidence. The loader adds a local, allowlisted PDF URL. Page numbers always identify PDF pages; Chess printed-page labels are recorded separately. Chunks are up to 180 words with 35-word overlap, never crossing pages. PDF extraction can lose symbols, diagrams and reading order; check original pages. No section headings are invented.

For Chess, only PDF pages 16–67 of the 2025 FIDE Arbiters’ Manual are indexed. They are marked `rules_and_commentary_unseparated` with a warning. Reliable rules/commentary separation remains a prerequisite for AI rulings; this search-only prototype must not claim it already distinguishes them.

The source mapping includes base rules for expansion searches and excludes expansions for base-only searches. Verify the Pandemic and Dark Ages editions before treating their selectors as definitive.

Keep raw downloads in ignored `data/raw/` if needed. Ignoring a file is not a licence or permission to process it. Do not commit full publisher PDFs without appropriate permission.
