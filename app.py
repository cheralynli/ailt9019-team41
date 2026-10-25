"""Local-only development server. Run: python3 app.py"""

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from referee.catalog import GAMES
from referee.pipeline import answer_question
from referee.corpus import load_passages
from referee.sources import SOURCE_BY_ID, allows_passage_answer

ROOT = Path(__file__).resolve().parent
STATIC = {"/": ("index.html", "text/html"), "/style.css": ("style.css", "text/css"), "/app.js": ("app.js", "text/javascript")}
STATIC.update({
    "/assets/board-background.png": ("assets/board-background.png", "image/png"),
    "/assets/Federo-Regular.ttf": ("assets/Federo-Regular.ttf", "font/ttf"),
    "/assets/DancingScript.ttf": ("assets/DancingScript.ttf", "font/ttf"),
})


class Handler(BaseHTTPRequestHandler):
    def send_data(self, status, body, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8" if content_type.startswith("text/") or content_type == "application/json" else content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if content_type != "application/pdf":
            self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # A browser may cancel a PDF download or navigate away.

    def send_json(self, status, payload):
        self.send_data(status, json.dumps(payload).encode())

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/games":
            try:
                passages = load_passages(ROOT / "data" / "passages.json")
            except (OSError, ValueError, TypeError):
                self.send_json(503, {"error": "Index could not be loaded. Rebuild with python3 -m referee.indexer."})
                return
            catalogue = [{**game, "answer_mode": "ai_ready" if any(
                p["game"] == game["id"] and allows_passage_answer(p) for p in passages) else "search_only"}
                         for game in GAMES]
            self.send_json(200, {"games": catalogue, "mode": "course" if os.environ.get("COURSE_API_KEY") else "search_only",
                                 "model": os.environ.get("COURSE_MODEL", "qwen3.8-flash") if os.environ.get("COURSE_API_KEY") else None, "passage_count": len(passages),
                                 "source_count": len({p["source_id"] for p in passages})})
        elif path.startswith("/api/sources/"):
            source = SOURCE_BY_ID.get(path.removeprefix("/api/sources/"))
            if source is None:
                self.send_json(404, {"error": "Unknown source."})
                return
            try:
                body = (ROOT / "rulebooks" / source["filename"]).read_bytes()
            except OSError:
                self.send_json(404, {"error": "This local PDF is missing."})
                return
            self.send_data(200, body, "application/pdf")
        elif path in STATIC:
            filename, content_type = STATIC[path]
            self.send_data(200, (ROOT / "static" / filename).read_bytes(), content_type)
        else:
            self.send_json(404, {"error": "Not found."})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/ask":
            self.send_json(404, {"error": "Not found."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                raise ValueError("Request is empty or too large.")
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Send the request as application/json.")
            payload = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError):
            self.send_json(400, {"error": "Send valid JSON under 16 KB."})
            return
        try:
            passages = load_passages(ROOT / "data" / "passages.json")
        except (OSError, ValueError, TypeError):
            self.send_json(503, {"error": "The local passage collection could not be loaded."})
            return
        try:
            response = answer_question(payload, passages)
        except ValueError as error:
            self.send_json(400, {"error": str(error)})
            return
        self.send_json(200, response)

    def log_message(self, format, *args):
        # Do not retain questions, request URLs or user history in logs.
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"BoardMaster (local rulebook search): http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
