import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import stat
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PREFS = '''user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("browser.startup.page", 0);
user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
'''


def group_members(pgid):
    result = subprocess.run(['ps', '-axo', 'pid=,pgid='], check=True,
                            capture_output=True, text=True, timeout=5)
    members = []
    saw_self = False
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            raise RuntimeError('invalid process-group census')
        pid, group = map(int, fields)
        saw_self = saw_self or pid == os.getpid()
        if group == pgid:
            members.append(pid)
    if not saw_self:
        raise RuntimeError('process-group census lacks current-process calibration')
    return sorted(members)


def terminate(process):
    if process is None:
        return {'method': 'no-process-created', 'owned_group_absent': True}
    try:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                break
            time.sleep(0.2)
        process.wait(timeout=10)
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return {'method': 'killpg', 'owned_group_absent': True}
        raise RuntimeError('owned benchmark process group remains')
    except PermissionError as error:
        permission_error = repr(error)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        else:
            process.wait(timeout=10)
        deadline = time.monotonic() + 5
        while True:
            members = group_members(process.pid)
            if not members:
                return {'method': 'direct-process-reap-and-pgid-census',
                        'group_operation_error': permission_error,
                        'owned_group_absent': True, 'remaining_members': []}
            if time.monotonic() >= deadline:
                raise RuntimeError('owned group members remain after direct-process cleanup: ' + repr(members))
            time.sleep(0.1)


def remove_profile(profile, identity):
    info = profile.lstat()
    if not stat.S_ISDIR(info.st_mode) or [info.st_dev, info.st_ino] != identity:
        raise RuntimeError('unknown profile root preserved')
    shutil.rmtree(profile)
    if profile.exists() or profile.is_symlink():
        raise RuntimeError('owned profile remains')


def run(root, directory, benchmark, label, binary_pins, resources, sha, need, verifier):
    directory.mkdir()
    profile = directory / 'profile'
    process = server = thread = log = None
    server_started = False
    identity = None
    failure = None
    cleanup_errors = []
    protocol_errors = []
    rows = []
    progress = []
    done = threading.Event()
    nonce = secrets.token_hex(16)
    prefix = '/' + nonce + '/'
    command = None
    dumps = []
    process_cleanup = None
    started = time.monotonic()
    def save(name, value):
        with (directory / name).open('x') as stream:
            stream.write(json.dumps(value, indent=2) + '\n')
    try:
        payloads = {name: (benchmark / name).read_bytes() for name in ('probe.html', 'benchmark.js')}
        for name in payloads:
            need(sha(benchmark / name) == resources[str((benchmark / name).relative_to(root))], 'served benchmark resource')
        wrapper = '''
let finished = false, sending = false;
const send = (kind, value) => fetch(PREFIX + kind, {
  method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(value)
});
const heartbeat = setInterval(() => {
  if (!finished && !sending && window.dormantLiteralBenchmarkResults) {
    sending = true;
    send("progress", window.dormantLiteralBenchmarkResults).finally(() => { sending = false; });
  }
}, 1000);
window.runDormantLiteralBenchmark("DORMANT_LITERAL_TIMING_V1", LABEL).then(result => {
  finished = true; clearInterval(heartbeat); return send("result", result);
}).catch(error => {
  finished = true; clearInterval(heartbeat);
  return send("result", {valid: false, error: String(error.stack || error)});
});
'''.replace('PREFIX', json.dumps(prefix)).replace('LABEL', json.dumps(label)).encode()
        payloads['capture.js'] = wrapper
        with (directory / 'capture.js').open('xb') as stream:
            stream.write(wrapper)
        payloads['probe.html'] += b'\n<script src="capture.js"></script>\n'
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass
            def setup(self):
                super().setup()
                self.connection.settimeout(3)
            def do_GET(self):
                routes = {prefix: ('probe.html', 'text/html'), prefix + 'benchmark.js': ('benchmark.js', 'text/javascript'), prefix + 'capture.js': ('capture.js', 'text/javascript')}
                if self.path not in routes:
                    self.send_error(404)
                    return
                name, mime = routes[self.path]
                body = payloads[name]
                self.send_response(200)
                self.send_header('Content-Type', mime)
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def do_POST(self):
                try:
                    need(self.path in (prefix + 'progress', prefix + 'result'), 'unknown POST')
                    size = int(self.headers.get('Content-Length', '0'))
                    need(0 < size <= 4 * 1024 * 1024, 'bounded JSON body')
                    body = self.rfile.read(size)
                    need(len(body) == size, 'complete JSON body')
                    value = json.loads(body)
                    need(isinstance(value, dict), 'object result')
                    if self.path.endswith('/progress'):
                        need(len(progress) < 650, 'bounded progress history')
                        name = 'progress-' + str(len(progress) + 1) + '.json'
                        save(name, value)
                        progress.append({'path': name, 'sha256': sha(directory / name)})
                    else:
                        need(not rows, 'single final result')
                        save('RAW.json', value)
                        rows.append(value)
                    self.send_response(204)
                    self.end_headers()
                    if rows:
                        done.set()
                except BaseException as error:
                    protocol_errors.append(repr(error))
                    done.set()
                    self.send_error(400)
        profile.mkdir(mode=0o700)
        info = profile.lstat()
        identity = [info.st_dev, info.st_ino]
        (profile / 'user.js').write_text(PREFS)
        save('PROFILE.json', {'path': str(profile), 'identity': identity, 'mode': stat.S_IMODE(info.st_mode), 'preferences': PREFS})
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        server_started = True
        binaries = [n for n in binary_pins if Path(n).name == 'firefox']
        need(len(binaries) == 1 and len(binary_pins) == 2, 'exact local binary pair')
        for name, digest in binary_pins.items():
            need(stat.S_ISREG((root / name).lstat().st_mode) and sha(root / name) == digest, 'actual phase binary')
        dump_dir = directory / 'crash-dumps'
        dump_dir.mkdir()
        command = [str(root / binaries[0]), '-headless', '-no-remote', '-profile', str(profile), f'http://127.0.0.1:{server.server_port}' + prefix]
        env = dict(os.environ, MOZ_CRASHREPORTER_NO_REPORT='1', MOZ_CRASHREPORTER='1', MOZ_CRASHREPORTER_DUMP_DIRECTORY=str(dump_dir))
        log = (directory / 'browser.log').open('x')
        process = subprocess.Popen(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + 600
        while not done.wait(0.1):
            need(process.poll() is None, 'browser exited before final result')
            need(time.monotonic() < deadline, '600-second browser deadline including setup waits')
        need(process.poll() is None, 'browser exited before controlled shutdown')
        need(not protocol_errors and len(rows) == 1, 'complete result protocol')
        need(rows[0].get('label') == label, 'phase result label')
        save('SUMMARY.json', verifier.verify(rows[0]))
    except BaseException as error:
        failure = repr(error)
    finally:
        try:
            process_cleanup = terminate(process)
        except BaseException as error:
            cleanup_errors.append('process: ' + repr(error))
        if log is not None:
            log.close()
        if server is not None:
            try:
                if server_started:
                    server.shutdown()
            except BaseException as error:
                cleanup_errors.append('server shutdown: ' + repr(error))
            finally:
                try:
                    server.server_close()
                except BaseException as error:
                    cleanup_errors.append('server close: ' + repr(error))
        if server_started:
            try:
                thread.join(timeout=5)
                if thread.is_alive():
                    cleanup_errors.append('server thread remains')
            except BaseException as error:
                cleanup_errors.append('server join: ' + repr(error))
        if identity is not None and not cleanup_errors:
            try:
                info = profile.lstat()
                need(stat.S_ISDIR(info.st_mode) and [info.st_dev, info.st_ino] == identity, 'profile root before dump retention')
                for path in sorted(profile.rglob('*.dmp')):
                    need(stat.S_ISREG(path.lstat().st_mode), 'regular crash dump')
                    destination = directory / ('retained-' + str(len(dumps)) + '.dmp')
                    with path.open('rb') as source, destination.open('xb') as target:
                        shutil.copyfileobj(source, target, 1024 * 1024)
                    dumps.append({'source': str(path.relative_to(profile)), 'path': destination.name, 'sha256': sha(destination)})
                remove_profile(profile, identity)
            except BaseException as error:
                cleanup_errors.append('profile: ' + repr(error))
        try:
            for path in sorted((directory / 'crash-dumps').glob('*.dmp')):
                need(stat.S_ISREG(path.lstat().st_mode), 'regular configured crash dump')
                dumps.append({'path': str(path.relative_to(directory)), 'sha256': sha(path)})
        except BaseException as error:
            cleanup_errors.append('crash retention: ' + repr(error))
        save('CLEANUP.json', {'owned_group_absent': bool(process_cleanup and process_cleanup['owned_group_absent']),
             'process_cleanup': process_cleanup,
             'profile_removed': identity is not None and not profile.exists() and not profile.is_symlink(),
             'profile_identity': identity, 'errors': cleanup_errors, 'retained_crash_dumps': dumps})
        save('RUN.json', {'command': command, 'binary_pins': binary_pins, 'label': label,
             'deadline_seconds': 600, 'elapsed_seconds': time.monotonic() - started,
             'exit_after_controlled_shutdown': process.returncode if process else None,
             'error': failure, 'protocol_errors': protocol_errors, 'progress': progress,
             'raw_sha256': sha(directory / 'RAW.json') if (directory / 'RAW.json').exists() else None})
    need(failure is None and not cleanup_errors and not dumps and not protocol_errors, 'benchmark correctness/process/cleanup failure')
    return read_result(directory)


def read_result(directory):
    return json.loads((directory / 'SUMMARY.json').read_text())
