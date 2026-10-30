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


def authenticate(policy, browser, application=False):
    assert policy['fixture_manifest'] is not None
    pins = [policy['fixture_manifest'], policy['process_helper'], *policy['resources'].values(), *policy['references'].values()]
    if application and browser == 'firefox':
        pins += list(policy['browsers'][browser]['app_pins'].values())
    for pin in pins:
        path = Path(pin['path'])
        if not path.is_absolute():
            path = ROOT / path
        assert path.is_file() and not path.is_symlink(), str(path)
        assert digest(path) == pin['sha256'], str(path)
    assert policy['profile_preferences'] == {} and policy['feature_overrides'] is False
    if application and browser == 'chrome':
        selected = policy['browsers'][browser]
        inventory = json.loads((ROOT / selected['inventory']['path']).read_text())
        portable = Path(inventory['root'])
        assert str(portable) == selected['portable_root'] and not portable.is_symlink()
        assert [portable.stat().st_dev, portable.stat().st_ino] == inventory['root_identity']
        expected = set()
        for row in inventory['entries']:
            assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
            file = portable / row['path']
            expected.add(row['path'])
            info = file.lstat()
            assert [info.st_dev, info.st_ino] == row['identity'] and stat.S_IMODE(info.st_mode) == row['mode']
            if row['kind'] == 'file':
                assert stat.S_ISREG(info.st_mode) and info.st_size == row['bytes'] and digest(file) == row['sha256']
            elif row['kind'] == 'symlink':
                assert stat.S_ISLNK(info.st_mode) and os.readlink(file) == row['target']
            else:
                assert row['kind'] == 'directory' and stat.S_ISDIR(info.st_mode)
        actual = set()
        for directory, dirs, files in os.walk(portable, followlinks=False):
            actual.update(str((Path(directory) / name).relative_to(portable)) for name in dirs + files)
        assert actual == expected
        binary = Path(selected['binary'])
        assert binary.is_relative_to(portable)
        binary_rows = [row for row in inventory['entries'] if row['path'] == str(binary.relative_to(portable))]
        assert len(binary_rows) == 1 and binary_rows[0]['kind'] == 'file'
        assert binary_rows[0]['sha256'] == selected['binary_sha256']


def validate(payload, run_id, browser):
    assert isinstance(payload, dict) and set(payload) == {'run_id', 'report'} and payload['run_id'] == run_id
    report = payload['report']
    assert set(report) == {'schema', 'status', 'userAgent', 'contextualTimingVerdict', 'observations'}
    assert report['schema'] == 'partial-base-observation-v1' and report['contextualTimingVerdict'] is None
    assert report['status'] in ['complete', 'incomplete']
    pattern = r'Firefox/158\.0(?:\s|$)' if browser == 'firefox' else r'(?:Headless)?Chrome/156\.0\.\d+\.\d+(?:\s|$)'
    assert isinstance(report['userAgent'], str) and re.search(pattern, report['userAgent'])
    cases = [('contextual-24', 'contextual', 24), ('literal-24', 'literal', 24), ('contextual-32', 'contextual', 32), ('literal-32', 'literal', 32)]
    assert len(report['observations']) == 4
    def number(value):
        return value is None or type(value) in (int, float) or (isinstance(value, dict) and set(value) == {'nonfinite'} and value['nonfinite'] in ['NaN', 'Infinity', '-Infinity'])

    def details(value):
        assert set(value) == {'opacity', 'font', 'cssDuration', 'timings'}
        assert number(value['opacity']) and isinstance(value['font'], str) and isinstance(value['cssDuration'], str)
        assert len(value['timings']) == 2
        for timing in value['timings']:
            assert set(timing) == {'duration', 'computedDuration', 'progress', 'time', 'state'}
            assert all(number(timing[key]) or timing[key] == 'auto' for key in ['duration', 'computedDuration'])
            assert number(timing['progress']) and number(timing['time']) and isinstance(timing['state'], str)

    for row, expected in zip(report['observations'], cases):
        assert set(row) == {'id', 'mode', 'finalFont', 'authoredInitialFont', 'stage', 'error', 'acquired', 'initial', 'samples', 'beforeMembership', 'membership', 'afterMembership', 'referenceChecks', 'contextualTimingVerdict'}
        assert (row['id'], row['mode'], row['finalFont']) == expected
        assert row['authoredInitialFont'] == 16 and row['contextualTimingVerdict'] is None
        assert isinstance(row['samples'], list) and len(row['samples']) <= 4
        assert [sample['phase'] for sample in row['samples']] == ['first-read', 'passive-frame-1', 'passive-frame-2', 'passive-frame-3'][:len(row['samples'])]
        assert all(set(sample) == {'phase', 'opacity'} for sample in row['samples'])
        assert all(number(sample['opacity']) for sample in row['samples'])
        assert isinstance(row['referenceChecks'], list) and row['referenceChecks']
        assert all(set(check) == {'name', 'passed'} and isinstance(check['name'], str) and type(check['passed']) is bool for check in row['referenceChecks'])
        if row['error'] is None:
            assert row['stage'] == 'complete' and len(row['samples']) == 4
            assert all(isinstance(row[key], dict) for key in ['initial', 'beforeMembership', 'membership', 'afterMembership'])
        else:
            assert set(row['error']) == {'name', 'message', 'stack'}
        for key in ['initial', 'beforeMembership', 'afterMembership']:
            if row[key] is not None:
                details(row[key])
        if row['membership'] is not None:
            membership = row['membership']
            assert set(membership) == {'count', 'currentNames', 'held'}
            assert type(membership['count']) is int and isinstance(membership['currentNames'], list)
            assert len(membership['held']) == 2
            assert all(set(item) == {'name', 'animation', 'effect'} and isinstance(item['name'], str) and type(item['animation']) is bool and type(item['effect']) is bool for item in membership['held'])
    assert (report['status'] == 'complete') == all(row['error'] is None for row in report['observations'])
    return report


def census():
    text = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,pgid=,command='], text=True, timeout=10)
    rows = [dict(pid=int(f[0]), ppid=int(f[1]), pgid=int(f[2]), command=f[3])
            for line in text.splitlines() if len(f := line.split(None, 3)) == 4]
    assert any(row['pid'] == os.getpid() for row in rows)
    return rows


def firefox_relaunch_group(rows, binary, profile, url):
    mains = [row for row in rows if row['command'].startswith(binary + ' ') and '--profile ' + profile + ' ' in row['command']]
    assert len(mains) == 1
    main = mains[0]
    assert main['pid'] == main['pgid'] and url in main['command']
    group = [row for row in rows if row['pgid'] == main['pgid']]
    prefix = '/Applications/Firefox.app/Contents/MacOS/plugin-container.app/'
    assert all(row == main or (row['ppid'] == main['pid'] and row['command'].startswith(prefix)
               and '-profile ' + profile + ' ' in row['command']) for row in group)
    return main, group


def cleanup_owned(process, control, browser, binary, profile, url, temporary, identity):
    receipt = {'temporary_removed': False, 'relaunch_cleanup': None}
    try:
        receipt['initial_group'] = control.terminate(process)
        assert receipt['initial_group']['owned_group_absent']
        rows = census()
        remaining = [row for row in rows if str(profile) in row['command']]
        if remaining and browser == 'firefox':
            assert not (profile / 'user.js').exists()
            main, group = firefox_relaunch_group(rows, binary, str(profile), url)
            assert firefox_relaunch_group(census(), binary, str(profile), url) == (main, group)
            receipt['relaunch_cleanup'] = {'before': group, 'signal': 'SIGTERM'}
            os.killpg(main['pgid'], signal.SIGTERM)
            for _ in range(40):
                rows = census()
                remaining = [row for row in rows if row['pgid'] == main['pgid'] or str(profile) in row['command']]
                if not remaining:
                    break
                time.sleep(0.25)
        receipt['remaining_profile_commands'] = remaining
        assert not remaining
        current = temporary.lstat()
        assert [current.st_dev, current.st_ino] == identity and stat.S_ISDIR(current.st_mode)
        assert current.st_uid == os.getuid() and not temporary.is_symlink()
        assert not (profile / 'user.js').exists()
        shutil.rmtree(temporary)
        receipt['temporary_removed'] = True
    except BaseException as exc:
        receipt['error'] = repr(exc)
    return receipt


class Receiver:
    def __init__(self, policy, browser, output):
        self.browser, self.output = browser, output
        self.run_id, self.nonce = secrets.token_hex(16), secrets.token_hex(24)
        self.report, self.errors = None, []
        self.done, self.lock = threading.Event(), threading.Lock()
        self.resources = {name: (ROOT / pin['path']).read_bytes() for name, pin in policy['resources'].items()}
        self.resources['/observe.html'] += b'\n<script src="/report.js" defer></script>\n'

    def url(self):
        return '/observe.html?' + urlencode({'run': self.run_id, 'nonce': self.nonce})

    def receive(self, path, origin, body):
        assert path == '/report/' + self.nonce and origin == self.origin
        payload = json.loads(body)
        report = validate(payload, self.run_id, self.browser)
        with self.lock:
            assert self.report is None
            save(self.output / 'REPORT.json', payload)
            self.report = report
        return {'accepted': True}

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
                    receiver.done.set()
                except Exception as error:
                    receiver.errors.append(repr(error))
                    self.respond(400, b'Invalid observation', 'text/plain')

        return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--browser', choices=['firefox', 'chrome'], required=True)
    args = parser.parse_args()
    policy = json.loads((HERE / 'POLICY.json').read_text())
    authenticate(policy, args.browser)
    if not args.run:
        print('Saved fixture pins verified. Browser not launched.')
        return 0
    assert policy['execution_enabled'] is True, 'Root activation required'
    authenticate(policy, args.browser, application=True)
    selected = policy['browsers'][args.browser]
    output = ROOT / selected['output']
    output.mkdir(mode=0o700)
    temporary = Path(tempfile.mkdtemp(prefix='css-partial-base-', dir='/private/tmp'))
    info = temporary.lstat()
    identity = [info.st_dev, info.st_ino]
    profile = temporary / 'profile'
    profile.mkdir(mode=0o700)
    save(output / 'TEMPORARY.json', {'path': str(temporary), 'identity': identity, 'profile': str(profile)})
    save(output / 'POLICY.json', policy)
    spec = importlib.util.spec_from_file_location('stock_owned_process_control', ROOT / policy['process_helper']['path'])
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    receiver = Receiver(policy, args.browser, output)
    save(output / 'RESOURCES.json', {name: {'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
                                    for name, body in receiver.resources.items()})
    server = process = None
    serving = False
    url = None
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
        url = receiver.origin + receiver.url()
        if args.browser == 'firefox':
            command = [selected['binary'], '--headless', '--no-remote', '--new-instance', '--profile', str(profile), url]
        else:
            command = [selected['binary'], '--headless=new', '--no-first-run', '--no-default-browser-check', '--user-data-dir=' + str(profile), url]
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
                    raise RuntimeError('Watchdog or cancellation before report')
                if process.poll() is not None:
                    assert args.browser == 'firefox', 'Launcher exited before report'
                    main_process, group = firefox_relaunch_group(census(), selected['binary'], str(profile), url)
                    receipt = output / 'RELAUNCH-ADMISSION.json'
                    if not receipt.exists():
                        save(receipt, {'main': main_process, 'group': group, 'launcher_returncode': process.returncode})
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
        cleanup = cleanup_owned(process, control, args.browser, selected['binary'], profile, url, temporary, identity)
        save(output / 'CLEANUP.json', cleanup)
    try:
        authenticate(policy, args.browser, application=True)
    except BaseException as exc:
        error = error or repr(exc)
    save(output / 'SERVER-ERRORS.json', receiver.errors)
    observation_complete = receiver.report is not None and receiver.report['status'] == 'complete'
    reference_checks_pass = receiver.report is not None and all(check['passed'] for item in receiver.report['observations'] for check in item['referenceChecks'])
    complete = error is None and not receiver.errors and receiver.report is not None and cleanup.get('temporary_removed', False)
    save(output / 'RESULT.json', {'execution_complete': complete, 'observation_complete': observation_complete,
        'reference_checks_pass': reference_checks_pass, 'contextual_timing_verdict': None, 'error': error,
        'report_received': receiver.report is not None, 'cleanup_complete': cleanup.get('temporary_removed', False),
        'native_acceptance': False, 'launcher_returncode_after_cleanup': process.returncode if process else None})
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
