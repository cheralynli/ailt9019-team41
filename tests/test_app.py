"""Structural tests only. Synthetic passages are NOT real game rules."""

import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from app import Handler
from referee.pipeline import answer_question
from referee.retrieval import retrieve
from pathlib import Path
from unittest.mock import patch
from referee.corpus import load_passages
from referee.indexer import chunks, normalize
from referee.sources import RULESET_SOURCES


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"game": "chess", "edition": "laws-2023", "question": "testtoken"}
        self.passages = [
            {"source_id": "chess-laws", "game": "chess", "edition": "laws-2023", "text": "Synthetic testtoken fixture"},
            {"source_id": "catan-base", "game": "catan", "edition": "base-5", "text": "Synthetic testtoken fixture"},
            {"source_id": "other", "game": "chess", "edition": "other", "text": "Synthetic testtoken fixture"},
        ]

    def test_empty_corpus_is_not_ready(self):
        response = answer_question(self.payload, [])
        self.assertEqual(response["status"], "not_ready")
        self.assertEqual(response["citations"], [])

    def test_bad_input(self):
        for payload in (None, [], {}, {**self.payload, "question": "  "}, {**self.payload, "question": "x" * 2001}, {**self.payload, "game": []}):
            with self.subTest(payload=type(payload)):
                with self.assertRaises(ValueError):
                    answer_question(payload, [])

    def test_unsupported_game_and_edition(self):
        for override in ({"game": "monopoly"}, {"edition": "base-5"}):
            self.assertEqual(answer_question({**self.payload, **override}, [])["status"], "unsupported")

    def test_retrieval_filters_game_and_edition(self):
        self.assertEqual(retrieve("testtoken", "chess", "laws-2023", self.passages), self.passages[:1])

    def test_no_evidence(self):
        self.assertEqual(answer_question({**self.payload, "question": "unrelated"}, self.passages)["status"], "no_evidence")

    def test_model_stub_never_invents_ruling(self):
        response = answer_question(self.payload, self.passages)
        self.assertEqual(response["status"], "search_only")
        self.assertEqual(response["citations"], self.passages[:1])

    def test_expansion_includes_base_but_not_reverse(self):
        base = {"source_id": "catan-base", "game": "catan", "text": "testtoken"}
        expansion = {"source_id": "catan-seafarers", "game": "catan", "text": "testtoken"}
        self.assertEqual(retrieve("testtoken", "catan", "base-5", [base, expansion]), [base])
        self.assertEqual(retrieve("testtoken", "catan", "seafarers-5", [base, expansion]), [base, expansion])

    def test_stopword_only_query_returns_nothing(self):
        self.assertEqual(retrieve("the and", "chess", "laws-2023", self.passages), [])

    def test_chunks_keep_all_words(self):
        text = " ".join(str(i) for i in range(500))
        parts = list(chunks(text))
        self.assertTrue(all(len(p.split()) <= 180 for p in parts))
        self.assertEqual(set(text.split()), set(" ".join(parts).split()))
        self.assertEqual(normalize("ﬁrst\n  rule"), "first rule")


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request(method, path, body, {"Content-Type": "application/json"})
        response = connection.getresponse()
        status, data = response.status, response.read()
        connection.close()
        return status, data

    def test_static_files(self):
        for path in ("/", "/style.css", "/app.js"):
            self.assertEqual(self.request("GET", path)[0], 200)

    def test_catalogue(self):
        status, body = self.request("GET", "/api/games")
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)["games"]), 4)

    def test_question_round_trip(self):
        with patch("app.load_passages", return_value=[]):
            status, body = self.request("POST", "/api/ask", json.dumps({"game": "catan", "edition": "base-5", "question": "Can I build?"}))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "not_ready")

    def test_malformed_json(self):
        self.assertEqual(self.request("POST", "/api/ask", "{")[0], 400)

    def test_private_files_not_served(self):
        for path in ("/.env", "/.git/config", "/data/passages.json", "/../README.md", "/api/sources/../.env", "/api/sources/equipment"):
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_bad_corpus_returns_error(self):
        with patch("app.load_passages", side_effect=ValueError("bad index")):
            self.assertEqual(self.request("GET", "/api/games")[0], 503)

    @unittest.skipUnless(Path("rulebooks/Pandemic_Rulebook.pdf").exists(), "Local PDF not present")
    def test_original_pdf_is_served(self):
        status, body = self.request("GET", "/api/sources/pandemic-base")
        self.assertEqual(status, 200)
        self.assertEqual(body, Path("rulebooks/Pandemic_Rulebook.pdf").read_bytes())


@unittest.skipUnless(Path("data/passages.json").exists(), "Build the local index first")
class LocalIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.passages = load_passages(Path("data/passages.json"))

    def test_six_sources_and_chess_page_boundaries(self):
        self.assertEqual(len({p["source_id"] for p in self.passages}), 6)
        for p in self.passages:
            self.assertTrue(p["source_url"].endswith(f"#page={p['page']}"))
            if p["game"] == "chess":
                self.assertTrue(16 <= p["page"] <= 67)
                self.assertTrue(p["warning"])

    def test_all_rulesets_return_scoped_candidates(self):
        queries = {"catan": "settlement distance", "chess": "castle king check", "dominion": "draw cards clean up", "pandemic": "outbreak"}
        for (game, edition), allowed in RULESET_SOURCES.items():
            found = retrieve(queries[game], game, edition, self.passages)
            self.assertTrue(found)
            self.assertTrue(all(p["source_id"] in allowed for p in found))

    def test_representative_page_retrieval(self):
        # Smoke checks, NOT the team's 32-case accuracy evaluation.
        cases = [("chess", "laws-2023", "Can I castle while my king is in check?", 24),
                 ("pandemic", "base-en", "What happens when an outbreak occurs?", 7)]
        for game, edition, question, page in cases:
            self.assertEqual(retrieve(question, game, edition, self.passages)[0]["page"], page)


if __name__ == "__main__":
    unittest.main()
