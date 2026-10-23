import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import os
import signal
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode, urlsplit

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--binary", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
parser.add_argument("--label", required=True)
parser.add_argument("--pin", action="append", default=[], type=Path)
args = parser.parse_args()
binary = args.binary.resolve(strict=True)
output = args.output.resolve()
if output.exists() or output == HERE or HERE in output.parents:
    raise RuntimeError("Output must be absent and outside the fixture capsule")
paths = [binary, *[HERE / name for name in ["probe.html", "benchmark.js", "CONFIG.json", "run.py", "validate.py", "cleanup.py"]], *[p.resolve(strict=True) for p in args.pin]]
xul = binary.parent / "XUL"
if xul.is_file(): paths.append(xul)
def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024): h.update(chunk)
    return h.hexdigest()
for path in paths:
    if not path.is_file(): raise RuntimeError(f"Not a file: {path}")
before = {str(p): digest(p) for p in paths}
config = json.loads((HERE / "CONFIG.json").read_text())
spec = importlib.util.spec_from_file_location("local_cost_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
cleanup_spec = importlib.util.spec_from_file_location("owned_process_cleanup", HERE / "cleanup.py")
cleanup = importlib.util.module_from_spec(cleanup_spec)
cleanup_spec.loader.exec_module(cleanup)
output.mkdir(parents=True)
profile = output / "profile"
profile.mkdir()
(output / "BEFORE.json").write_text(json.dumps(before, indent=2) + "\n")
child_env = dict(os.environ)
startup_environment = {"MOZ_DISABLE_SAFE_MODE_KEY": "1",
                       "MOZ_DISABLE_UPDATE_PROCESSING": "1",
                       "MOZ_SAFE_MODE_RESTART_inherited_present": "MOZ_SAFE_MODE_RESTART" in child_env,
                       "MOZ_SAFE_MODE_RESTART_removed": True}
child_env["MOZ_DISABLE_SAFE_MODE_KEY"] = "1"
child_env["MOZ_DISABLE_UPDATE_PROCESSING"] = "1"
child_env.pop("MOZ_SAFE_MODE_RESTART", None)
(output / "STARTUP-ENV.json").write_text(json.dumps(startup_environment, indent=2) + "\n")
posts = []
progress_count = 0
request_lock = threading.Lock()
def request_receipt(value):
    with request_lock:
        with (output / "REQUESTS.jsonl").open("a") as stream:
            stream.write(json.dumps({"monotonic": time.monotonic(), **value}) + "\n")

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(2)
    def log_message(self, *args): pass
    def do_GET(self):
        route = urlsplit(self.path).path
        request_receipt({"method": "GET", "route": route, "event": "received"})
        names = {"/": ("probe.html", "text/html"), "/benchmark.js": ("benchmark.js", "text/javascript"), "/CONFIG.json": ("CONFIG.json", "application/json")}
        if route not in names:
            self.send_error(404)
            return
        name, mime = names[route]
        body = (HERE / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        global progress_count
        route = urlsplit(self.path).path
        request_receipt({"method": "POST", "route": route, "event": "received"})
        if route == "/progress":
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                self.send_error(413)
                return
            try:
                value = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                request_receipt({"route": route, "event": "progress-rejected", "reason": "invalid-json"})
                self.send_error(400)
                return
            if (not isinstance(value, dict) or type(value.get("sequence")) is not int
                or value["sequence"] != progress_count or progress_count >= 300
                or value.get("stage") not in {"script-start", "config-ready", "fixture-start", "batch-begin", "batch-end", "result-ready", "fixture-error"}):
                request_receipt({"route": route, "event": "progress-rejected", "reason": "identity"})
                self.send_error(400)
                return
            progress_count += 1
            request_receipt({"method": "POST", "route": route, "event": "progress-persisted", "value": value})
            self.send_response(204)
            self.end_headers()
            return
        if route != "/result":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= 4000000:
            self.send_error(413)
            return
        try:
            posts.append(json.loads(self.rfile.read(length)))
        except Exception as error:
            posts.append({"complete": False, "error": str(error)})
        self.send_response(204)
        self.end_headers()
server = None
thread = None
command = None
process = None
failure = None
cleanup_errors = []
spawn = None
initial_members = []
termination = None
try:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    command = [str(binary), "-headless", "-no-remote", "-profile", str(profile), f"http://127.0.0.1:{server.server_port}/?" + urlencode({"label": args.label})]
    with (output / "browser.log").open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True, env=child_env)
        spawn = {"pid": process.pid, "expectedPgid": process.pid, "startNewSession": True, "startupEnvironment": startup_environment}
        (output / "SPAWN.json").write_text(json.dumps(spawn, indent=2) + "\n")
        initial_members = cleanup.members(process.pid)
        spawn["initialMembers"] = initial_members
        (output / "SPAWN.json").write_text(json.dumps(spawn, indent=2) + "\n")
        deadline = time.monotonic() + 75
        while process.poll() is None and not posts and time.monotonic() < deadline:
            time.sleep(0.1)
        if not posts:
            failure = "browser exited before receipt" if process.poll() is not None else "75-second runner deadline"
except BaseException as error:
    failure = repr(error)
finally:
    if process is not None:
        try:
            termination = cleanup.terminate_owned(process, initial_members)
            cleanup_errors.extend(termination["errors"])
        except BaseException as error:
            cleanup_errors.append('termination helper: ' + repr(error))
    try:
        if server is not None:
            if thread is not None and thread.is_alive(): server.shutdown()
            server.server_close()
        if thread is not None and thread.is_alive(): thread.join(timeout=3)
    except BaseException as error:
        cleanup_errors.append('HTTP cleanup: ' + repr(error))
    try:
        shutil.rmtree(profile)
    except OSError as error:
        cleanup_errors.append(repr(error))
after = {str(p): digest(p) if p.is_file() else None for p in paths}
result = {"startupEnvironment": startup_environment, "progressReceipts": progress_count, "label": args.label, "command": command, "before": before, "after": after, "stable": before == after, "observations": posts, "processExitAfterOwnedTermination": process.returncode if process is not None else None, "profileRemoved": not profile.exists(), "failure": failure, "cleanupErrors": cleanup_errors, "spawn": spawn, "termination": termination, "noLiveGroup": termination["noLiveGroup"] if termination else None, "terminal": termination["terminal"] if termination else process is None}
(output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
if failure or cleanup_errors or before != after or len(posts) != 1 or not termination or not termination["terminal"]:
    raise RuntimeError("Incomplete, failed, or unstable run; receipts retained")
summary = validator.validate(posts[0], config, args.label)
(output / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"stable": True, "rows": summary["measuredRows"], "queryReads": summary["queryReads"], "geometryMismatches": summary["geometryMismatches"]}))
