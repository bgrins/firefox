import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--binary', required=True, type=Path)
parser.add_argument('cases', nargs='+')
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
binary = args.binary.resolve()

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

paths = [binary, binary.parent / 'XUL', ROOT / 'probe.html', Path(__file__).resolve(),
         REPO / 'servo/components/style/custom_properties.rs',
         REPO / 'servo/components/style/properties/cascade.rs']
before = {str(p): sha(p) for p in paths}
(out / 'BEFORE.json').write_text(json.dumps(before, indent=2) + '\n')
rows = []
for case in args.cases:
    if case not in ['plain', 'space', 'tab', 'newline', 'literal', 'comment', 'trailing', 'nested', 'minimal']:
        raise ValueError(case)
    folder = out / case
    folder.mkdir()
    done = threading.Event()
    events = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass

        def do_GET(self):
            if not self.path.startswith('/probe.html'):
                self.send_error(404)
                return
            page = ROOT / 'probe.html'
            if case == 'minimal':
                page = REPO / 'artifacts/css-attr-range-producers-v1/crash-minimal.html'
            body = page.read_bytes()
            (folder / 'served.html').write_bytes(body)
            events.append({'kind': 'get', 'path': self.path})
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            length = int(self.headers.get('Content-Length', '0'))
            if self.path not in ['/started', '/result'] or not 0 < length < 10000:
                self.send_error(400)
                return
            data = json.loads(self.rfile.read(length))
            events.append({'kind': self.path, 'data': data})
            self.send_response(200)
            self.end_headers()
            if self.path == '/result':
                done.set()

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    profile = Path(tempfile.mkdtemp(prefix='css-attr-offset-'))
    prefs = '''user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("app.update.disabledForTesting", true);
user_pref("network.captive-portal-service.enabled", false);
user_pref("network.connectivity-service.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
'''
    (profile / 'user.js').write_text(prefs)
    (folder / 'user.js').write_text(prefs)
    command = [str(binary), '-headless', '-no-remote', '-profile', str(profile),
               f'http://127.0.0.1:{server.server_port}/probe.html?case={case}']
    env = dict(os.environ, MOZ_HEADLESS='1', MOZ_NO_REMOTE='1', MOZ_CRASHREPORTER='1', MOZ_CRASHREPORTER_NO_REPORT='1', RUST_BACKTRACE='1')
    started = time.time()
    process = None
    try:
        with (folder / 'browser.log').open('w') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                       env=env, start_new_session=True)
            deadline = time.monotonic() + 15
            while not done.wait(0.1) and process.poll() is None and time.monotonic() < deadline:
                pass
            natural_exit = process.poll()
            if natural_exit is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
        row = {'case': case, 'command': command, 'events': events,
               'elapsed_seconds': time.time() - started, 'natural_parent_exit': natural_exit,
               'exit_after_owned_termination': process.returncode,
               'result_received': done.is_set()}
        (folder / 'RUN.json').write_text(json.dumps(row, indent=2) + '\n')
        rows.append(row)
        print(json.dumps(row), flush=True)
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
        server.shutdown()
        thread.join()
        server.server_close()
        dumps = profile / 'minidumps'
        if dumps.exists():
            shutil.copytree(dumps, folder / 'minidumps')
        shutil.rmtree(profile)
after = {str(p): sha(p) for p in paths}
(out / 'RUN.json').write_text(json.dumps({'before': before, 'after': after,
    'stable': before == after, 'rows': rows,
    'scope': 'Isolated profiles, default CSS preferences, synthetic local attributes. Missing callback alone is not a crash diagnosis.'}, indent=2) + '\n')
if before != after:
    raise RuntimeError('Inputs changed')
