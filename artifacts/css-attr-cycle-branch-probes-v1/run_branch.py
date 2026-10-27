import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent
if len(sys.argv) != 4:
    raise SystemExit("Usage: run_branch.py EXTERNAL_FILES_SHA256 raw|used ABSENT_OUTPUT_DIR")
assert sys.argv[2] in ("raw", "used")
case_dir = HERE / sys.argv[2]
out = Path(sys.argv[3])
assert out.is_absolute() and not out.exists()
out = out.resolve()
assert out != HERE and HERE not in out.parents and out not in HERE.parents

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

assert digest(HERE / "FILES.json") == sys.argv[1]
manifest = json.loads((HERE / "FILES.json").read_text())
for name, expected in manifest.items():
    path = HERE / name
    assert not path.is_symlink() and path.is_file() and digest(path) == expected, name
spec = importlib.util.spec_from_file_location("probe_validation", case_dir / "validate.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
pins = json.loads((HERE / "PINS.json").read_text())
repo = Path(pins["root"])
app = Path(pins["app"])
binary = app / "Contents/MacOS/firefox"
def head():
    return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                                    "rev-parse", "HEAD"], cwd=repo, text=True).strip()
def identity(path):
    return {"sha256": digest(path), "resolved": str(path.resolve()), "bytes": path.stat().st_size}
assert head() == pins["head"], "HEAD changed since preparation"
for name, expected in pins["files"].items():
    assert identity(Path(name)) == expected, name
for name, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert digest(repo / name) == expected, name
paths = ([Path(name) for name in pins["files"]] + [HERE / "FILES.json"] +
         [HERE / n for n in manifest] +
         [repo / name for name in json.loads((HERE / "REFERENCES.json").read_text())])
before = {str(p): identity(p) for p in paths}
head_before = head()
out.mkdir()
profile = out / "profile"
profile.mkdir()
rows = []

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        route = {"/": ("probe.html", "text/html"), "/probe.js": ("probe.js", "text/javascript")}
        if self.path not in route:
            self.send_error(404)
            return
        name, mime = route[self.path]
        body = (case_dir / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if self.path != "/result" or not 0 < length < 2_000_000 or rows:
            self.send_error(400)
            return
        rows.append(json.loads(self.rfile.read(length)))
        self.send_response(204)
        self.end_headers()

def owned_parents():
    matches = []
    lines = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True).splitlines()
    for line in lines:
        if not line.strip():
            continue
        pid, args = line.split(None, 1)
        if args.startswith(str(binary) + " ") and " -profile " + str(profile) + " " in args:
            matches.append(int(pid))
    return matches

server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
command = ["/usr/bin/open", "-W", "-n", "-g", "-a", str(app), "--args",
           "-headless", "-no-remote", "-profile", str(profile), f"http://127.0.0.1:{server.server_port}/"]
process = None
terminated = []
errors = []
thread.start()
try:
    with (out / "browser.log").open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 90
        while not rows and time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Launcher exited before the result")
            time.sleep(.1)
except BaseException as error:
    errors.append({"operation": "launch/wait", "error": repr(error)})
finally:
    try:
        terminated = owned_parents()
        for pid in terminated:
            try:
                if pid in owned_parents():
                    os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 10
        while owned_parents() and time.monotonic() < deadline:
            time.sleep(.1)
        if owned_parents():
            errors.append({"operation": "cleanup", "error": "Owned browser still running; profile retained"})
    except BaseException as error:
        errors.append({"operation": "owned-browser cleanup", "error": repr(error)})
    if process is not None:
        try:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        except BaseException as error:
            errors.append({"operation": "launcher cleanup", "error": repr(error)})
    server.shutdown()
    thread.join()
    server.server_close()
    if not errors:
        shutil.rmtree(profile)
after = {}
for path in paths:
    try:
        after[str(path)] = identity(path)
    except Exception as error:
        errors.append({"operation": "post-pin", "path": str(path), "error": repr(error)})
head_after = head()
result = {"case": sys.argv[2], "head_before": head_before, "head_after": head_after,
          "command": command, "before": before, "after": after, "stable": before == after and head_before == head_after,
          "observations": rows, "errors": errors, "profile_removed": not profile.exists(),
          "terminated_owned_parents": terminated,
          "launcher_exit": process.returncode if process is not None else None}
(out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
assert not errors and before == after and head_before == head_after and len(rows) == 1
summary = validation.summarize(rows[0])
(out / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
assert not summary["calibration_failures"], "Attribute calibration failed; interpretation blocked"
print(json.dumps(summary))
