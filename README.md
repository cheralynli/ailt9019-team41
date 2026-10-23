# Board Game Referee · Team 41

A local rules assistant: select a game/ruleset, ask a question, retrieve matching
rulebook passages and receive an explanation using the course-provided Alibaba
Cloud Bailian API. Answers cite original local passages and PDF pages.

## Player walkthrough

On a running application, choose the game and ruleset, enter a complete question,
and select **Ask BoardMaster**. Read the explanation and use **Open original PDF**
to check the cited passage. Every question is independent: avoid references such
as “that move” without describing it. A refusal means the request is outside the
assistant's scope or the supplied evidence is insufficient; it is not an API error.

| Game | Sample question | Expected response shape |
| --- | --- | --- |
| Catan / base | Can I build a settlement next to another settlement? | Distance-rule explanation plus base rulebook citation |
| Dominion / base | How many cards do I draw at the end of my turn? | Clean-up rule explanation plus base rulebook citation |
| Pandemic / base | What happens when an outbreak occurs? | Outbreak explanation with precise Infection-card timing plus citation |
| Chess | Can I castle while my king is in check? | Currently source excerpts only, with an explicit laws/commentary warning |

Try “Should I build a city or a settlement to win?” under Catan to check a
strategy refusal. Switching game or edition clears the previous result so its
answer cannot be mistaken for the new selection. The header reports server
configuration, not a guarantee of provider availability or quota.

This is a local development app. No shared hosted URL has been provided yet;
end-user access without local installation is still an outstanding proposal item.

## Developer setup

Requires Python 3.10 or newer. In this repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Download and hash-check the pinned official PDFs with:

```sh
python scripts/download_rulebooks.py
```

Alternatively, place the six PDFs in `rulebooks/` using the filenames in
`referee/sources.py`. The download script refuses changed files instead of
silently mixing versions. `--check-only` checks local files without network access.
Official download URLs, SHA-256 hashes and indexed ranges are recorded in
`docs/rulebook-sources.json`. Then build the local index:

```sh
python -m referee.indexer
```

The PDFs and generated index are Git-ignored. Page counts and hashes help verify
files; they do not establish an edition or permission for every use.

## Course API connection check

```sh
zsh scripts/start-course.zsh --check
```

Paste the emailed group API key at the hidden prompt. The key is not saved to
disk or returned to the parent terminal. This sends one synthetic test request
without rulebook text. Expected output: `Provider: course`, `Status: answer`,
three starting tokens in the explanation, and `Validated citations: 1`.

- Base URL: https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
- Protocol: OpenAI-compatible Chat Completions, served by Alibaba Cloud.
- Default model: `qwen3.8-flash`. Override with `export COURSE_MODEL="MODEL_ID"`.
- Key variable: `COURSE_API_KEY`; `.env` is ignored and not loaded automatically.
- Course notice: 25,000 credits shared per group, course-related work only.
  First-batch key expiry is 19 November 2026; contact teaching staff for top-ups
  or renewal. Never commit or record the key.

## Run the website

Stop any previous server with Ctrl+C, then:

```sh
zsh scripts/start-course.zsh
```

Enter the course key again and open http://127.0.0.1:8000. If the port is busy,
use `zsh scripts/start-course.zsh --port 8001`.

Select Catan / Base game and ask:

> Can I build a settlement next to another settlement?

Expected: no, because adjacent intersections must be vacant under the distance
rule; the cited base-rule passage is on PDF page 5. Use “Open original PDF” to
check context. If a PDF preview is blank, open its link in Safari or Chrome.

Without a configured key, `python app.py` serves keyword-search results only.
These are explicitly labelled and do not claim to be AI rulings.

## Data and error handling

Questions are not saved to disk. When the course API is enabled, questions and
up to three retrieved excerpts, with source labels, are sent to Alibaba Cloud.
Do not enter personal information. Confirm source-use permissions and provider
terms before deployment or broader testing. No chat history is maintained.

The backend uses only retrieved evidence, requests JSON and validates returned
citation IDs against the current passages. URLs, pages and quoted passages come
from local source metadata, not model-generated references. This prevents
invented source IDs; it does not prove every explanation is accurate.

Requests time out after 45 seconds; the browser waits 60 seconds. No automatic
retries are made. Only one course request runs at once per server process;
teammates using separate servers must still coordinate the shared quota.
Failures display sanitized diagnostic codes: timeout, network, busy, http_400,
http_access_denied, http_404, http_429, http_5xx or invalid_model_output. Raw
provider errors and credentials are not displayed. Refusals and clarification
requests contain no fabricated ruling or citations.

## Current evidence and limits

See `docs/COURSE_API_PROGRESS_2026-10-21.md` for user-observed Catan answering,
strategy refusal and Pandemic answering screenshots, with limitations. These
examples do not establish aggregate accuracy or replace the proposed 32-case
evaluation. Source provenance is recorded in `docs/rulebook-sources.json`.

- Six documents yield 467 local excerpts, filtered by game/ruleset. Expansion
  searches include base rules; base-only searches exclude expansions.
- Retrieval is a BM25-style keyword baseline, not semantic reasoning.
- Chess uses PDF pages 16–67 of the 355-page 2025 FIDE Arbiters’ Manual. Laws and
  commentary are not yet separated, so Chess remains search-only.
- Pandemic and Dark Ages edition labels still need verification.
- PDF extraction can omit diagrams and symbols; chunks can cut sentences.
- Pandemic wording about “infection step” versus “current Infection card” needs
  the testing owner's review. Other refusal/ambiguity cases remain to be tested.
- The server binds to localhost and is for local development, not production.
- The midterm recording, deployment and full evaluation remain outstanding.

## Tests and project map

```sh
python -m unittest discover -s tests -v
```

Tests mock the course API and do not use keys or spend credits. Local PDF checks
are skipped if the files/index are missing. They do not measure real model
accuracy.

```text
app.py                      Local HTTP server and /api endpoints
referee/model.py            Evidence prompt and citation validation
referee/course_api.py       Course API transport and local concurrency limit
referee/pipeline.py          Validation → retrieval → explanation/search/refusal
referee/sources.py           Source allowlist and base/expansion mapping
referee/indexer.py           PDF extraction and page-bounded chunks
referee/retrieval.py         Local keyword retrieval
scripts/start-course.zsh     Hidden-key startup and connection check
scripts/check_course.py      Synthetic live API check
static/                     Browser interface
```

`GET /api/games` reports catalogue and index counts. `POST /api/ask` accepts
`game`, `edition` (catalogue ruleset ID) and `question`. Responses contain
`status`, `message` and `citations`; failures may include `diagnostic`.
Invalid input returns HTTP 400; corrupt indexes return 503. Local PDF routes
serve only allowlisted files. The missing-key fallback remains local search.

Official API configuration reference:
https://help.aliyun.com/zh/model-studio/more-tools

## Website review — 23 October 2026

The submitted revised proposal targets university students aged 18+ and requires
five usability participants (at least four completing all four tasks unaided).
Week 8 calls for all six documents, Chess and Dominion integration, and the fixed
32-case rules evaluation. See `docs/WEEK8_REVIEW_2026-10-23.md` for the gap audit.

Recent fixes add truthful API configuration labels, clear results when changing
rulesets, distinguish clarification/refusal/error states, clarify obvious vague
questions before retrieval, reject explicit mismatched game names, and strengthen
the evidence prompt to preserve conditions and timing. Keyword scope checks are
conservative, not a complete semantic classifier. No live accuracy improvement
is claimed until the group reruns its real API test cases.
