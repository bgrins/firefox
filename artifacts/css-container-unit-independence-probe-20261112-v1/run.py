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
        save('LIVE.json', {'phase': label, 'pid': child.pid, 'status': 'running'})
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
            save('COMMANDS.json', COMMANDS)
            save('LIVE.json', {'phase': label, 'status': 'terminal', 'exit': child.returncode})
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
    before = binaries('before')
    assert before == json.loads(authority.read_text())
    path = 'testing/web-platform/tests/css/css-conditional/container-queries/container-units-computational-independence.html'
    run('upstream-baseline-2', [PYTHON, './mach', 'wpt', '--headless', '--no-pause-after-test',
        '--processes=1', '--binary=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'),
        '--log-raw=' + str(HERE / 'upstream-baseline-2-raw.log'),
        '--log-wptreport=' + str(HERE / 'upstream-baseline-2-wptreport.json'), path], 360, 0)
    assert binaries('after') == before
    report = json.loads((HERE / 'upstream-baseline-2-wptreport.json').read_text())
    save('BASELINE-OBSERVATIONS.json', report['results'])

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
    main()
