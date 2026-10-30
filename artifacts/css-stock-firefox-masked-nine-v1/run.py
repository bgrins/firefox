import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlencode, urlsplit

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def authenticate(policy, application=False):
    pins = [policy['fixture_manifest'], policy['process_helper'], policy['bridge'], *policy['resources'].values()]
    if application:
        pins += list(policy['installed_app'].values())
    for pin in pins:
        path = Path(pin['path'])
        if not path.is_absolute():
            path = ROOT / path
        assert path.is_file() and not path.is_symlink(), str(path)
        assert path.stat().st_size == pin['bytes'] and digest(path) == pin['sha256'], str(path)
    assert policy['profile_preferences'] == {} and policy['feature_overrides'] is False
    assert len(policy['roster']) == policy['expected_pages'] == 4
    assert sum(map(len, policy['roster'].values())) == policy['expected_callbacks'] == 9
    assert set(policy['resources']) == set(policy['roster']) | {'/resources/testharness.js'}


def validate(payload, policy, run_id, page):
    assert isinstance(payload, dict) and set(payload) == {'run_id', 'page', 'tests', 'status', 'ua', 'supports'}
    assert payload['run_id'] == run_id and payload['page'] == page
    assert isinstance(payload['ua'], str) and re.search(r'Firefox/' + re.escape(policy['expected_version']) + r'(?:\s|$)', payload['ua'])
    assert set(payload['supports']) == {'typed_duration', 'literal_duration', 'variables'}
    assert all(type(v) is bool for v in payload['supports'].values())
    tests = payload['tests']
    assert isinstance(tests, list)
    assert [t['name'] for t in tests] == policy['roster'][page]
    for test in tests:
        assert set(test) == {'name', 'status', 'message', 'stack'}
        assert type(test['status']) is int and test['status'] in range(5)
        assert all(test[k] is None or isinstance(test[k], str) for k in ['message', 'stack'])
    status = payload['status']
    assert set(status) == {'status', 'message', 'stack'}
    assert type(status['status']) is int and status['status'] in range(4)
    assert all(status[k] is None or isinstance(status[k], str) for k in ['message', 'stack'])


def assessment(reports, policy):
    rows = [{'page': p['page'], **t} for p in reports for t in p['tests']]
    return {'complete': len(reports) == policy['expected_pages'], 'pages': len(reports),
            'missing_pages': [p for p in policy['roster'] if p not in {r['page'] for r in reports}],
            'callbacks': len(rows), 'pass': sum(r['status'] == 0 for r in rows),
            'fail': sum(r['status'] == 1 for r in rows), 'rows': rows,
            'other_callback_statuses': [r for r in rows if r['status'] not in [0, 1]],
            'endings': [p['status'] for p in reports],
            'all_callbacks_pass': len(rows) == 9 and all(r['status'] == 0 for r in rows),
            'all_endings_ok': len(reports) == 4 and all(p['status']['status'] == 0 for p in reports),
            'suite_pass': len(reports) == 4 and len(rows) == 9 and all(r['status'] == 0 for r in rows) and all(p['status']['status'] == 0 for p in reports),
            'profile_preference_overrides': False, 'native_acceptance': False}


class Receiver:
    def __init__(self, policy, output):
        self.policy, self.output = policy, output
        self.run_id, self.nonce = secrets.token_hex(16), secrets.token_hex(24)
        self.pages = list(policy['roster'])
        self.reports, self.errors = [], []
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.resources = {name: (ROOT / pin['path']).read_bytes() for name, pin in policy['resources'].items()}
        self.resources['/resources/testharnessreport.js'] = (HERE / 'testharnessreport.js').read_bytes()

    def url(self, index):
        return self.pages[index] + '?' + urlencode({'run': self.run_id, 'nonce': self.nonce})

    def receive(self, path, origin, body):
        assert path == '/report/' + self.nonce and origin == self.origin
        payload = json.loads(body)
        with self.lock:
            index = len(self.reports)
            assert index < len(self.pages)
            validate(payload, self.policy, self.run_id, self.pages[index])
            save(self.output / f'page-{index + 1}.json', payload)
            self.reports.append(payload)
            return {'next': self.url(index + 1) if index + 1 < len(self.pages) else None}

    def handler(self):
        receiver = self

        class Handler(BaseHTTPRequestHandler):
            def setup(self):
                super().setup()
                self.connection.settimeout(5)

            def log_message(self, *_args):
                pass

            def respond(self, code, body, content_type):
                self.send_response(code)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()

            def do_GET(self):
                path = urlsplit(self.path).path
                body = receiver.resources.get(path)
                if self.headers.get('Host') != receiver.host or body is None:
                    self.respond(404, b'Not found', 'text/plain')
                    return
                self.respond(200, body, 'text/javascript' if path.endswith('.js') else 'text/html; charset=utf-8')

            def do_POST(self):
                try:
                    assert self.headers.get('Host') == receiver.host
                    assert self.headers.get('Content-Type') == 'application/json'
                    size = int(self.headers.get('Content-Length', '0'))
                    assert 0 < size <= 2_000_000
                    self.connection.settimeout(5)
                    body = self.rfile.read(size)
                    assert len(body) == size
                    assert self.path == '/report/' + receiver.nonce and self.headers.get('Origin') == receiver.origin
                    with receiver.lock:
                        with (receiver.output / ('request-' + secrets.token_hex(8) + '.json')).open('xb') as stream:
                            stream.write(body)
                    reply = receiver.receive(self.path, self.headers.get('Origin'), body)
                    self.respond(200, json.dumps(reply).encode(), 'application/json')
                    if reply['next'] is None:
                        receiver.done.set()
                except Exception as error:
                    receiver.errors.append(repr(error))
                    self.respond(400, b'Invalid observation', 'text/plain')

        return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    policy = json.loads((HERE / 'POLICY.json').read_text())
    authenticate(policy)
    if not args.run:
        print('Saved fixture pins verified. Browser not launched.')
        return 0
    assert policy['execution_enabled'] is True, 'Root activation required'
    authenticate(policy, application=True)
    output = ROOT / policy['output']
    output.mkdir(mode=0o700)
    temporary = Path(tempfile.mkdtemp(prefix='css-stock-firefox-', dir='/private/tmp'))
    info = temporary.lstat()
    identity = [info.st_dev, info.st_ino]
    profile = temporary / 'profile'
    profile.mkdir(mode=0o700)
    save(output / 'TEMPORARY.json', {'path': str(temporary), 'identity': identity, 'profile': str(profile)})
    save(output / 'POLICY.json', policy)
    spec = importlib.util.spec_from_file_location('stock_owned_process_control', ROOT / policy['process_helper']['path'])
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    receiver = Receiver(policy, output)
    save(output / 'RESOURCES.json', {name: {'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
                                    for name, body in receiver.resources.items()})
    server = process = None
    serving = False
    error = None
    cleanup = {}
    stopped = threading.Event()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda *_args: stopped.set())
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 0), receiver.handler())
        server.daemon_threads = False
        receiver.host = f'127.0.0.1:{server.server_port}'
        receiver.origin = 'http://' + receiver.host
        save(output / 'BINDING.json', {'run_id': receiver.run_id, 'nonce': receiver.nonce, 'origin': receiver.origin})
        threading.Thread(target=server.serve_forever, daemon=True).start()
        serving = True
        command = [policy['installed_app']['MacOS/firefox']['path'], '--headless', '--no-remote',
                   '--new-instance', '--profile', str(profile), receiver.origin + receiver.url(0)]
        save(output / 'COMMAND.json', command)
        assert list(profile.iterdir()) == []
        env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME', 'LANG'] if k in os.environ}
        env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', TMPDIR=str(temporary))
        save(output / 'ENVIRONMENT.json', {'inherited_names': sorted(k for k in env if k != 'TMPDIR'),
            'TMPDIR': str(temporary), 'feature_environment_overrides': False, 'user_js_created': False})
        with (output / 'browser.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=temporary, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            save(output / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + policy['watchdog_seconds']
            while not receiver.done.wait(0.2):
                if stopped.is_set() or time.monotonic() >= deadline:
                    raise RuntimeError('Watchdog or cancellation before four reports')
                if process.poll() is not None:
                    raise RuntimeError('Browser exited before four reports: ' + str(process.returncode))
            assert not receiver.errors
    except BaseException as exc:
        error = repr(exc)
    finally:
        for sig in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(sig, signal.SIG_IGN)
        if server is not None:
            if serving:
                server.shutdown()
            server.server_close()
        try:
            cleanup = control.terminate(process)
            assert cleanup['owned_group_absent']
            census = subprocess.run(['ps', '-axo', 'pid=,command='], check=True, capture_output=True, text=True, timeout=10)
            remaining = [line for line in census.stdout.splitlines() if str(profile) in line]
            cleanup['remaining_profile_commands'] = remaining
            assert not remaining
            current = temporary.lstat()
            assert [current.st_dev, current.st_ino] == identity and stat.S_ISDIR(current.st_mode)
            assert current.st_uid == os.getuid() and not temporary.is_symlink()
            assert not (profile / 'user.js').exists(), 'Unexpected preference-override file'
            shutil.rmtree(temporary)
            cleanup['temporary_removed'] = True
        except BaseException as exc:
            cleanup['error'] = repr(exc)
            cleanup['temporary_removed'] = False
        save(output / 'CLEANUP.json', cleanup)
    try:
        authenticate(policy, application=True)
    except BaseException as exc:
        error = error or repr(exc)
    result = assessment(receiver.reports, policy)
    save(output / 'ASSESSMENT.json', result)
    save(output / 'SERVER-ERRORS.json', receiver.errors)
    complete = error is None and not receiver.errors and result['complete'] and cleanup.get('temporary_removed', False)
    save(output / 'RESULT.json', {'execution_complete': complete, 'error': error,
        'callbacks_pass': result['pass'], 'callbacks_fail': result['fail'], 'pages': result['pages'],
        'all_callbacks_pass': result['all_callbacks_pass'], 'all_endings_ok': result['all_endings_ok'],
        'suite_pass': result['suite_pass'], 'native_acceptance': False,
        'ordinary_failures_preserved': True, 'browser_returncode_after_owned_cleanup': process.returncode if process else None})
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
