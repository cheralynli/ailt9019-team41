# Mac verification — 19 November 2026

Tested commit: `623a66768654a8bbb351f566e4a4c08614118185`.
Python 3.14.3, existing Mac virtual environment and local corpus/index.
This was not a fresh-clone check and made no live model requests.

Commands and captured outputs (all exit codes zero):

| Command | Output |
| --- | --- |
| `.venv/bin/python -m unittest discover -s tests -v` | [python-tests.txt](python-tests.txt): 67 passed, no skips |
| `node --test tests/test_ui.cjs` | [ui-tests.txt](ui-tests.txt): 10 passed, no skips |
| `.venv/bin/python scripts/evaluate.py` | [preflight.txt](preflight.txt): 32 processed, designated reference coverage 21/26 |
| `.venv/bin/python -m pip check` | [dependencies.txt](dependencies.txt): no broken requirements |

Retrieval checks do not measure model answer accuracy. The Linux fresh-clone
summary and historical 16 November Mac reproduction remain separate records.
