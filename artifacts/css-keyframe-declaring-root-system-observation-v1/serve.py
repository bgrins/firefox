import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
fixture = ROOT / "artifacts/css-contextual-easing-declaring-root-boundary-20261029-v1/declaring-root-easing.tentative.html"
harness = ROOT / "artifacts/css-contextual-easing-regression-plan-v1/capture/testing/web-platform/tests/resources/testharness.js"
reporter = ROOT / "artifacts/css-contextual-easing-regression-plan-v1/capture/testing/web-platform/tests/resources/testharnessreport.js"
sha = lambda body: hashlib.sha256(body).hexdigest()
html = fixture.read_bytes()
assert sha(html) == "30556c2b86c91e26e58783b557d326ec6320708bf1e3bdedb0e59ab28a697d58"
assert html.count(b"<body>") == 1
served_html = html.replace(b"<body>", b'<script src="/record.js"></script>\n<body>', 1)
resources = {
    "/case.html": (served_html, "text/html; charset=utf-8"),
    "/record.js": ((HERE / "record.js").read_bytes(), "text/javascript"),
    "/resources/testharness.js": (harness.read_bytes(), "text/javascript"),
    "/resources/testharnessreport.js": (reporter.read_bytes(), "text/javascript"),
}
assert sha(resources["/resources/testharness.js"][0]) == "7a108d7cfa98ac413ddb38f82fd509fb2037dfcc25ccf466567520cbb6bdf1fa"
assert sha(resources["/resources/testharnessreport.js"][0]) == "3777176fc736b0a78cf7617b9613b220f635daae7536ec7ebb99c61dbb525aae"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        entry = resources.get(urlsplit(self.path).path)
        if entry is None:
            self.send_error(404)
            return
        body, mime = entry
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), Handler)
with (HERE / "SERVER.json").open("x") as stream:
    json.dump({"pid": os.getpid(), "port": server.server_port,
               "fixture_sha256": sha(html),
               "served_sha256": {name: sha(body) for name, (body, _) in resources.items()}},
              stream, indent=2, sort_keys=True)
    stream.write("\n")
try:
    server.serve_forever(poll_interval=0.1)
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
    with (HERE / "CLOSED.json").open("x") as stream:
        json.dump({"pid": os.getpid(), "server_closed": True}, stream)
        stream.write("\n")
