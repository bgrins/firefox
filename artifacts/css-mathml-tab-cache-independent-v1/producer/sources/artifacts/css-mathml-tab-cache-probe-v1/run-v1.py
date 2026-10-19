import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "baseline-v1"
SURVEY = ROOT / "artifacts/css-hyphenation-tab-cache-caller-audit-v1"
HTML = SURVEY / "mathml-cache-origin.html"
FONT = SURVEY / "Ahem.ttf"
BINARY = ROOT / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox"
sys.path.insert(0, str(ROOT / "artifacts/css-spec-lean"))
assert hashlib.sha256((ROOT / "artifacts/css-spec-lean/browser_check.py").read_bytes()).hexdigest() == "5f5668dbdd00527a39f4f6f7a4536a73220a492e30639066a428530ae3e6bbf0"
from browser_check import Marionette


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unwrap(value):
    return value.get("value", value) if isinstance(value, dict) else value


def main():
    OUT.mkdir(exist_ok=False)
    paths = {HTML, FONT, BINARY, BINARY.parent / "XUL", Path(__file__).resolve(),
             ROOT / "artifacts/css-spec-lean/browser_check.py"}
    manifest = SURVEY / "MANIFEST.json"
    assert sha(manifest) == "357951d18e1dede5b0c9ec6646801d6a8f2e26f5db2da39adc5b4273bb85b346"
    paths.add(manifest)
    for name, expected in json.loads(manifest.read_text())["files"].items():
        assert sha(SURVEY/name) == expected, name
    for row in json.loads((SURVEY/"CURRENT-SOURCES.json").read_text()):
        path = ROOT/row["path"]
        assert sha(path) == row["sha256"], str(path)
        paths.add(path)
    paths.add(ROOT/"gfx/thebes/gfxTextRun.cpp")
    receipt = {"inputs_before": {str(p): sha(p) for p in sorted(paths)},
               "http": [], "mode": "MathML tab-cache source-origin diagnostic",
               "scope": "Local computed-style or geometry observations; no release-browser or final defect claim"}
    for path in sorted(paths):
        if path not in (BINARY, BINARY.parent / "XUL"):
            dest = OUT / "sources" / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
    html_route = "/" + str(HTML.relative_to(ROOT))
    resources = {html_route: (HTML.read_bytes(), "text/html"),
                 "/" + str(FONT.relative_to(ROOT)): (FONT.read_bytes(), "font/ttf")}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status = 200 if self.path in resources else 404
            data, content_type = resources.get(self.path, (b"", "text/plain"))
            receipt["http"].append({"path": self.path, "status": status,
                                    "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    profile = Path(tempfile.mkdtemp(prefix="profile-", dir=OUT))
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    prefs = {"marionette.port": port, "browser.shell.checkDefaultBrowser": False,
             "layout.css.devPixelsPerPx": "1.0"}
    (profile / "user.js").write_text("".join(
        f"user_pref({json.dumps(k)}, {json.dumps(v)});\n" for k, v in prefs.items()))
    receipt["preferences"] = prefs
    process = client = None
    failure = None
    try:
        with (OUT / "browser.log").open("w") as log:
            command = [str(BINARY), "--headless", "--marionette", "--no-remote", "--profile", str(profile)]
            receipt["command"] = command
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 45
            while True:
                if process.poll() is not None:
                    raise RuntimeError("Browser exited before connection")
                try:
                    connection = socket.create_connection(("127.0.0.1", port), timeout=1)
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(.1)
            connection.settimeout(60)
            client = Marionette(connection)
            receipt["session"] = client.request("WebDriver:NewSession", {"capabilities": {"alwaysMatch": {}}})
            client.request("WebDriver:SetTimeouts", {"script": 45000})
            url = f"http://127.0.0.1:{server.server_port}{html_route}"
            receipt["url"] = url
            client.request("WebDriver:Navigate", {"url": url})
            script = """const done = arguments[arguments.length-1];
              (async () => {
                for (let i=0; !window.probeResult && i<400; i++)
                  await new Promise(resolve => setTimeout(resolve, 50));
                const first = window.probeResult;
                if (!first) throw Error('Probe did not complete');
                const second = await window.runProbe();
                done({first, second});
              })().catch(error => done({error: String(error)}));"""
            result = unwrap(client.request("WebDriver:ExecuteAsyncScript", {"script": script, "args": [], "newSandbox": False}))
            receipt["observed"] = result
            assert "error" not in result, result
            assert all(result[k]["fontLoaded"] and len(result[k]["rows"]) == 12 for k in ["first","second"])
            receipt["summary"] = {"rows_per_run":12,"runs":2,"font_loaded":True,
              "scope":"Diagnostic observation only; no accepted native defect or normative MathML conformance claim"}

    except Exception as error:
        failure = error
        receipt["error"] = repr(error)
    finally:
        if client:
            try:
                client.request("WebDriver:DeleteSession", {})
            except Exception:
                pass
            client.close()
        if process:
            process.terminate()
            try:
                receipt["browser_exit_after_termination"] = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                receipt["browser_exit_after_kill"] = process.wait(timeout=15)
        server.shutdown()
        server.server_close()
        receipt["inputs_after"] = {str(p): sha(p) for p in sorted(paths)}
        (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if failure:
        raise failure
    assert receipt["inputs_before"] == receipt["inputs_after"]
    print(json.dumps({**receipt["summary"], "stable_pins": len(paths)}, indent=2))


if __name__ == "__main__":
    main()
