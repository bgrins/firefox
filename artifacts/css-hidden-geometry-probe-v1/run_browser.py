import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
assert sys.argv[1:] in (["release"], ["project"])
kind = sys.argv[1]
out = HERE / kind
out.mkdir()
binary = (Path("/Applications/Firefox.app/Contents/MacOS/firefox") if kind == "release"
          else REPO / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox")
native = json.loads((REPO / "artifacts/css-cssom-exact-traversal-standalone-v4/FINAL.json").read_text())
paths = [binary, binary.parent / "XUL", HERE / "probe.html", HERE / "probe.js", Path(__file__).resolve()]
paths += [REPO / name for name in {**native["sources"], **native["fixed_native_pins"]}]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

before = {str(p): digest(p) for p in paths}
rows = []

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        routes = {"/": ("probe.html", "text/html"), "/probe.js": ("probe.js", "text/javascript")}
        if self.path not in routes:
            self.send_error(404)
            return
        name, mime = routes[self.path]
        body = (HERE / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/result":
            self.send_error(404)
            return
        rows.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(204)
        self.end_headers()

server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
profile = out / "profile"
profile.mkdir()
command = [str(binary), "-headless", "-no-remote", "-profile", str(profile), f"http://127.0.0.1:{server.server_port}/"]
with (out / "browser.log").open("w") as log:
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    try:
        deadline = time.monotonic() + 90
        while process.poll() is None and not rows and time.monotonic() < deadline:
            time.sleep(.1)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
server.shutdown()
thread.join()
shutil.rmtree(profile)
after = {str(p): digest(p) for p in paths}
result = {"kind": kind, "command": command, "before": before, "after": after,
          "stable": before == after, "observations": rows, "profile_removed": True,
          "exit_after_termination": process.returncode}
(out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
assert len(rows) == 1 and "error" not in rows[0] and len(rows[0]["rows"]) == 32
assert before == after
print(json.dumps({"kind": kind, "rows": len(rows[0]["rows"]), "stable": before == after}))
