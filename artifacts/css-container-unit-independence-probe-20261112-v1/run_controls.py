import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'servo/components/style/values/specified/length.rs'
BASELINE = ROOT / 'artifacts/css-consumed-cache-natural-fragments-probe-20261112-v1'
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))
COMMANDS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def run(label, argv, timeout, expected):
    started = time.monotonic()
    with (HERE / (label + '.log')).open('x') as log:
        child = subprocess.Popen(argv, cwd=ROOT, env=ENV, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        save('CONTROL-LIVE.json', {'phase': label, 'pid': child.pid, 'status': 'running'})
        code = None
        try:
            code = child.wait(timeout=timeout)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            COMMANDS.append({'phase': label, 'argv': argv, 'exit': child.returncode,
                             'seconds': time.monotonic() - started,
                             'log_sha256': sha(HERE / (label + '.log'))})
            save('CONTROL-COMMANDS.json', COMMANDS)
            save('CONTROL-LIVE.json', {'phase': label, 'status': 'terminal', 'exit': child.returncode})
    if code != expected:
        raise RuntimeError(f'{label}: expected {expected}, got {code}')


def binaries(label):
    folder = ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS'
    result = {str(folder / name): {'sha256': sha(folder / name), 'bytes': (folder / name).stat().st_size}
              for name in ['firefox', 'XUL']}
    save(label + '-BINARIES.json', result)
    return result


def main():
    authority = ROOT / 'artifacts/css-grid-consumed-cache-trace-20261112-v2/restored-build-BINARIES.json'
    before = binaries('control-before')
    assert before == json.loads(authority.read_text())
    target = ROOT / 'testing/web-platform/tests/css/css-conditional/container-queries/container-unit-independence-local-probe.html'
    raw = (HERE / 'diagnostic.html').read_bytes()
    assert not target.exists()
    try:
        target.write_bytes(raw)
        run('unique-controls', [PYTHON, './mach', 'wpt', '--headless', '--no-pause-after-test',
            '--processes=1', '--binary=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'),
            '--log-raw=' + str(HERE / 'unique-controls-raw.log'),
            '--log-wptreport=' + str(HERE / 'unique-controls-wptreport.json'), str(target.relative_to(ROOT))], 360, 1)
        report = json.loads((HERE / 'unique-controls-wptreport.json').read_text())
        results = report['results']; assert len(results) == 1 and results[0]['status'] == 'OK'
        cases = json.loads((HERE / 'CASES.json').read_text())
        observed = []
        for entry in results[0]['subtests']:
            assert entry['name'].startswith('OBSERVATION ')
            row = json.loads(entry['name'].removeprefix('OBSERVATION '))
            expected = cases[len(observed)]
            assert all(row[k] == v for k,v in expected.items())
            row['status'] = entry['status']; row['message'] = entry.get('message'); observed.append(row)
        assert len(observed) == len(cases)
        save('CONTROL-OBSERVATIONS.json', observed)
        assert binaries('control-after') == before
    finally:
        if target.exists():
            assert target.read_bytes() == raw
            target.unlink()
        save('TEST-CLEANUP.json', {'owned_probe_removed': not target.exists()})

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
    main()
