# Board Game Referee · Team 41

A local starter for the AILT9019 project: ask a rules question, retrieve passages from the selected rulebook, and eventually receive an AI explanation with citations.

## Start the app

Requires Python 3.10 or newer. No API key is needed for local search. The web server has no third-party dependencies; rebuilding the index requires `pypdf`.

For a fresh checkout, create a virtual environment and build the index first:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m referee.indexer
```

Place the six approved PDFs in `rulebooks/` using the exact filenames listed in `referee/sources.py`. The PDFs and generated index are local-only and Git-ignored. Run the indexer again after replacing a source. It checks page counts and records SHA-256 hashes; a matching page count alone does not verify an edition. Do not replace a PDF without reviewing its source metadata.

```sh
python3 app.py
```

Open http://127.0.0.1:8000 in your browser. Stop the server with Ctrl+C.
If the port is busy, run `python3 app.py --port 8001` instead.

## Try it

1. Select a game and its ruleset.
2. Use “Try a sample question” or enter your own question.
3. Click “Ask BoardMaster”.
4. Read up to three matching excerpts with document, edition and PDF page references.
5. Use “Open original PDF” to check each result in context. These links serve only the six approved local files.

If the embedded browser shows a blank PDF preview, open the same local link in Safari or Chrome. Page-fragment navigation depends on the browser’s PDF viewer.

These are **keyword-search results, not AI rulings**. The model API is not connected. Some results may be irrelevant; all results need review. A page link identifies the source but does not prove that the passage answers the question.

Questions are not saved to disk and no external API calls are made. Each question is independent; there is no conversational memory. The local development server binds only to this computer. Do not expose it publicly or use it as a production server.

## What exists / what does not

- Working browser form, game/ruleset selection, sample questions, response and citation containers.
- Working Python JSON endpoint, input validation and a simple retrieval baseline with game/ruleset filtering.
- A PDF indexing command and a replaceable model adapter placeholder.
- Basic automated tests, **not** the proposed 32-question rules evaluation.
- No AI rulings, semantic scope checks, strategy/dispute detection, API integration or deployment yet.
- Six sources across four games are indexed locally. Expansion searches include their base rules; base-only searches exclude expansions. Dominion Dark Ages and Pandemic editions still need verification.
- Chess indexing is limited to PDF pages 16–67 of the 2025 Arbiters’ Manual. This section includes rules and commentary that are **not yet separated**; every Chess excerpt carries a warning. The extra equipment/tournament PDF is excluded and untouched.
- Extracted text can omit diagrams, symbols or columns. Chunk boundaries may cut sentences. Verify original pages before relying on results. A short/empty Seafarers page (31) is skipped and recorded in the index report.

## Project map

```text
app.py                   Local HTTP server and /api endpoints
referee/catalog.py       Games, rulesets and sample questions
referee/sources.py       Six-source allowlist and base/expansion mapping
referee/indexer.py       PDF extraction and page-bounded chunking
referee/corpus.py        Index loading and provenance validation
referee/pipeline.py      Validation → retrieval → answer/refusal flow
referee/retrieval.py     Simple keyword-search baseline
referee/model.py         Future course-model API adapter
static/                  Browser interface (HTML, CSS, JavaScript)
data/passages.json       Generated local excerpts (Git-ignored)
data/index-report.json   Page ranges, source hashes and skipped pages (Git-ignored)
data/README.md           Passage format and source-verification notes
tests/test_app.py        Skeleton tests
docs/NEXT_STEPS.md       Build order and midterm checklist
```

## Run the tests

```sh
python3 -m unittest discover -s tests -v
```

## Developer notes

`GET /api/games` returns the catalogue and index counts. `POST /api/ask` accepts a JSON object containing `game`, `edition` (the catalogue ruleset ID), and `question`. Responses include `status`, `message`, and `citations`. `search_only` means retrieved excerpts, not a generated ruling. Invalid input returns HTTP 400; corrupt indexes return 503. A missing index yields an explicit setup message. `GET /api/sources/<source-id>` serves only allowlisted local PDFs, with original PDF page fragments in citation links.

Search uses BM25-style keyword ranking, small vocabulary hints (such as castle/castling), and ruleset filtering. It is not semantic reasoning or a confidence-calibrated refusal system. Ordinary Chess searches exclude chunks mentioning Chess960 unless the question mentions it.

Next, confirm the course API provider and request format before implementing `referee/model.py`. Keep credentials on the backend, outside tracked files. `.env` is ignored, but this starter does not load it or make API calls. Never put a key in browser JavaScript, recordings or Git commits.

The user-supplied PDFs are processed only on this computer. Before deployment, sharing PDFs, or sending text to an external API, verify permissions and provider terms. Nothing commits, pushes, publishes or uploads files automatically.
