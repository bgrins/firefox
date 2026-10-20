import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUTPUT = ROOT / 'runtime-v1'
if OUTPUT.exists():
    raise RuntimeError('fresh runtime output required')
OUTPUT.mkdir()
PROFILE = OUTPUT / 'profile'
PROFILE.mkdir()
prefs = '''user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("app.update.disabledForTesting", true);
user_pref("network.captive-portal-service.enabled", false);
user_pref("network.connectivity-service.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
'''
(PROFILE / 'user.js').write_text(prefs)
(OUTPUT / 'user.js').write_text(prefs)
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

source_rows = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
for row in source_rows:
    if sha(REPO / row['local_path']) != row['sha256']:
        raise RuntimeError('source changed: ' + row['local_path'])
binary = REPO / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'
xul = binary.parent / 'XUL'
paths = [binary, xul, ROOT / 'probe.html', Path(__file__).resolve(), *[REPO / row['local_path'] for row in source_rows]]
before = {str(p.relative_to(REPO)): sha(p) for p in paths}
completed = threading.Event()
received = []

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return
    def do_GET(self):
        if self.path == '/probe.html':
            body = (ROOT / 'probe.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        if self.path != '/result' or length > 1000000:
            self.send_response(400)
            self.end_headers()
            return
        body = self.rfile.read(length)
        (OUTPUT / 'raw.json').write_bytes(body)
        received.append(json.loads(body))
        self.send_response(200)
        self.end_headers()
        completed.set()

server = HTTPServer(('127.0.0.1', 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
command = [str(binary), '-headless', '-no-remote', '-profile', str(PROFILE),
           f'http://127.0.0.1:{server.server_port}/probe.html']
env = dict(os.environ, MOZ_HEADLESS='1', MOZ_NO_REMOTE='1')
started = time.time()
with (OUTPUT / 'browser.log').open('w') as log:
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    done = completed.wait(55)
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)
server.shutdown()
thread.join()
after = {str(p.relative_to(REPO)): sha(p) for p in paths}
result = received[0] if received else None
rows = result.get('rows', []) if result else []
receipt = dict(command=command, started_epoch=started, elapsed_seconds=time.time()-started,
               browser_exit_after_owned_termination=process.returncode, callback_received=done,
               pins_before=before, pins_after=after, stable_pins=before == after,
               complete=bool(result and result.get('complete')), expected_rows=18,
               actual_rows=len(rows), unique_labels=len({r['label'] for r in rows}),
               failed_rows=[r for r in rows if r['failures']],
               calibration_failures=[r for r in rows if r['beforeFailures'] or r['refreshFailures']],
               compat_mode=result.get('compatMode') if result else None,
               scope='Fresh-profile diagnostic on existing root-built binary; no isolated rebuild or native refinement proof.')
(OUTPUT / 'RUN.json').write_text(json.dumps(receipt, indent=2) + '\n')
if not done or not receipt['complete'] or len(rows) != 18 or receipt['unique_labels'] != 18 or before != after:
    raise RuntimeError('incomplete or changed-input probe; inspect RUN.json')
print(json.dumps({'rows': len(rows), 'pass': len(rows)-len(receipt['failed_rows']), 'fail': len(receipt['failed_rows'])}))
