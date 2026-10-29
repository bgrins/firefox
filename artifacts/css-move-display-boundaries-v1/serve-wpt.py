from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

root = Path(__file__).resolve().parents[2]
fixtures = root / "artifacts/css-move-shadow-animation-v1/candidate/testing/web-platform/tests/dom/nodes/moveBefore"
paths = {
    "/animation.html": fixtures / "shadow-descendant-css-animation-preserve.html",
    "/reactions.html": fixtures / "shadow-descendant-custom-element-reactions.html",
    "/resources/testharness.js": root / "testing/web-platform/tests/resources/testharness.js",
    "/resources/testharnessreport.js": root / "testing/web-platform/tests/resources/testharnessreport.js",
}
collector = b'''<script>
window.probeResults = {rows: [], complete: false};
add_result_callback(t => probeResults.rows.push({name: t.name, status: t.status, message: t.message}));
add_completion_callback((tests, status) => {
  probeResults.status = {status: status.status, message: status.message};
  probeResults.complete = true;
});
</script>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = paths.get(self.path)
        if path is None:
            self.send_error(404)
            return
        body = path.read_bytes()
        if self.path.endswith(".html"):
            anchor = b'<script src="/resources/testharnessreport.js"></script>'
            assert body.count(anchor) == 1
            body = body.replace(anchor, anchor + collector)
        self.send_response(200)
        self.send_header("Content-Type", "text/html" if self.path.endswith(".html") else "text/javascript")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = HTTPServer(("127.0.0.1", 0), Handler)
print(server.server_port, flush=True)
server.serve_forever()
