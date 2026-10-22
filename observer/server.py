"""Localhost server: the dashboard, raw corpus files for drill-through, and artifact markdown."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from . import config
from .config import Paths
from .parse import raw_path_for


def make_handler(p: Paths):
    corpus = p.corpus.resolve()
    artifacts = p.artifacts.resolve()

    class Handler(SimpleHTTPRequestHandler):
        def send_text(self, body: bytes, ctype: str, status: int = 200):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def safe_file(self, base, path):
            path = path.resolve()
            return path if path.is_file() and path.is_relative_to(base) else None

        def do_GET(self):
            route = unquote(self.path.split("?")[0])
            if route in ("/", "/index.html"):
                f = p.dashboard / "index.html"
                if not f.exists():
                    return self.send_text(b"Dashboard not built; run build-dashboard.", "text/plain", 404)
                return self.send_text(f.read_bytes(), "text/html; charset=utf-8")
            if route == "/report.json" and (p.out / "report.json").exists():
                return self.send_text((p.out / "report.json").read_bytes(), "application/json")
            if route.startswith("/raw/"):
                f = self.safe_file(corpus, raw_path_for(route[5:], p.corpus))
                if f:
                    return self.send_text(f.read_bytes(), "text/plain; charset=utf-8")
            if route.startswith("/artifacts/"):
                f = self.safe_file(artifacts, p.artifacts / route[len("/artifacts/"):])
                if f:
                    return self.send_text(f.read_bytes(), "text/markdown; charset=utf-8")
            self.send_text(b"Not found", "text/plain", 404)

        def log_message(self, *args):
            pass

    return Handler


def serve(p: Paths, port: int = config.PORT) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(p))
    print(f'{{"url": "http://127.0.0.1:{port}/"}}', flush=True)
    httpd.serve_forever()
