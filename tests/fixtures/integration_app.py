"""Minimal HTTP application used only by the Docker integration test."""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"python-app-manager integration test\n")

    def log_message(self, format: str, *args: object) -> None:
        return


port = int(os.environ.get("APP_PORT", "8000"))
HTTPServer(("127.0.0.1", port), Handler).serve_forever()
