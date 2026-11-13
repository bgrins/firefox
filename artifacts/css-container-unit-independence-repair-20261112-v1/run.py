import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
BINARY = ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))
COMMANDS = []


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def binaries():
    return {str(path): {'sha256': sha(path), 'bytes': path.stat().st_size}
            for path in [BINARY, BINARY.with_name('XUL')]}


def run(label, argv, timeout):
    started = time.monotonic()
    with (HERE / (label + '.log')).open('x') as log:
        child = subprocess.Popen(argv, cwd=ROOT, env=ENV, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        save('LIVE.json', {'phase': label, 'pid': child.pid, 'status': 'running'})
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
    if code:
        raise RuntimeError(f'{label} exited {code}')


def main():
    entries = json.loads((HERE / 'INPUTS.json').read_text())
    authority = ROOT / 'artifacts/css-grid-consumed-cache-trace-20261112-v2/restored-build-BINARIES.json'
    before = binaries()
    assert before == json.loads(authority.read_text())
    save('before-BINARIES.json', before)
    for entry in entries:
        assert sha(ROOT / entry['path']) == entry['original_sha256']
        assert sha(HERE / 'candidate' / entry['path']) == entry['candidate_sha256']
    installed = []
    try:
        for entry in entries:
            (ROOT / entry['path']).write_bytes((HERE / 'candidate' / entry['path']).read_bytes())
            installed.append(entry)
        save('INSTALL.json', {'installed': [entry['path'] for entry in installed]})
        run('diff-check', ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                           'diff', '--check', '--', *[entry['path'] for entry in entries]], 60)
        run('build', [PYTHON, './mach', 'build', 'binaries', '-j2'], 1800)
        save('fixed-BINARIES.json', binaries())
        tests = [
            'css/css-conditional/container-queries/container-units-computational-independence.html',
            'css/css-conditional/container-queries/container-units-basic.html',
            'css/css-conditional/container-queries/container-units-small-viewport-fallback.html',
            'css/css-properties-values-api/register-property.html',
            'css/css-properties-values-api/at-property.html',
        ]
        run('wpt', [PYTHON, './mach', 'wpt', '--headless', '--no-pause-after-test',
            '--processes=1', '--binary=' + str(BINARY),
            '--log-raw=' + str(HERE / 'wpt-raw.log'),
            '--log-wptreport=' + str(HERE / 'wptreport.json'),
            *['testing/web-platform/tests/' + test for test in tests]], 600)
        results = json.loads((HERE / 'wptreport.json').read_text())['results']
        assert {r['test'] for r in results} == {'/' + test for test in tests}
        focused = next(r for r in results if r['test'] == '/' + tests[0])
        assert focused['status'] == 'OK' and len(focused['subtests']) == 106
        assert all(r['status'] == 'PASS' for r in focused['subtests'])
        for entry in entries:
            assert sha(ROOT / entry['path']) == entry['candidate_sha256']
        assert binaries() == json.loads((HERE / 'fixed-BINARIES.json').read_text())
        save('RESULT.json', {'status': 'passed', 'installed': True,
                            'focused_subtests_pass': 106,
                            'suite_files': len(results),
                            'suite_subtests': sum(len(r['subtests']) for r in results)})
    except BaseException as error:
        save('FAILURE.json', {'error': repr(error)})
        for entry in installed:
            assert sha(ROOT / entry['path']) == entry['candidate_sha256']
            (ROOT / entry['path']).write_bytes((HERE / 'original' / entry['path']).read_bytes())
        if binaries() != before:
            run('restored-build', [PYTHON, './mach', 'build', 'binaries', '-j2'], 1800)
        save('restored-BINARIES.json', binaries())
        save('RESTORATION.json', {'source_restored': all(
            sha(ROOT / entry['path']) == entry['original_sha256'] for entry in entries)})
        raise


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda signum, frame: (_ for _ in ()).throw(InterruptedError(signum)))
    main()
