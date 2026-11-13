import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
BINARY = ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'
NATIVE = 'layout/generic/ReflowInput.cpp'
TEST = 'testing/web-platform/tests/css/cssom/resolved-margins-overconstrained-block.html'
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def binaries():
    return {str(p): dict(sha256=sha(p), bytes=p.stat().st_size)
            for p in [BINARY, BINARY.with_name('XUL')]}


def main():
    phase = sys.argv[1]
    assert phase in ('baseline', 'build', 'fixed')
    out = HERE / phase
    assert not out.exists()
    out.mkdir()
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    expected_native = inputs[NATIVE]['candidate' if phase == 'fixed' else 'original']
    assert sha(ROOT / NATIVE) == expected_native
    assert sha(ROOT / TEST) == inputs[TEST]['candidate']
    authority = (HERE / 'build/after-BINARIES.json' if phase == 'fixed' else
                 ROOT / 'artifacts/css-container-unit-independence-repair-20261112-v1/fixed-BINARIES.json')
    assert binaries() == json.loads(authority.read_text())
    save(out / 'before-BINARIES.json', binaries())
    spec = importlib.util.spec_from_file_location('owned_process', HERE / 'process.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runner = module.Runner(out)
    if phase == 'build':
        assert json.loads((HERE / 'baseline/RESULT.json').read_text())['fail'] == 66
        candidate = HERE / 'candidate' / NATIVE
        assert sha(candidate) == inputs[NATIVE]['candidate']
        (ROOT / NATIVE).write_bytes(candidate.read_bytes())
        save(out / 'INSTALL.json', dict(path=NATIVE, sha256=sha(ROOT / NATIVE)))
        expected_native = inputs[NATIVE]['candidate']
        argv = [PYTHON, './mach', 'build', 'binaries', '-j2']
        timeout = 1800
    else:
        tests = [TEST]
        if phase == 'fixed':
            tests += ['testing/web-platform/tests/css/cssom/computed-style-005.html',
                      'testing/web-platform/tests/css/cssom-view/cssom-getBoxQuads-001.html']
        argv = [PYTHON, './mach', 'wpt', '--headless', '--no-pause-after-test',
                '--processes=1', '--binary=' + str(BINARY),
                '--setpref=layout.css.getBoxQuads.enabled=true',
                '--log-raw=' + str(out / 'raw.log'),
                '--log-wptreport=' + str(out / 'wptreport.json'), *tests]
        timeout = 600
    try:
        command, _ = runner.run(argv, ROOT, ENV, phase, timeout=timeout)
        assert sha(ROOT / NATIVE) == expected_native
        assert sha(ROOT / TEST) == inputs[TEST]['candidate']
        if phase == 'build':
            assert command['exit'] == 0
            assert binaries() != json.loads((out / 'before-BINARIES.json').read_text())
            save(out / 'RESULT.json', dict(status='built', installed=True))
        else:
            results = json.loads((out / 'wptreport.json').read_text())['results']
            assert {r['test'] for r in results} == {
                '/' + t.removeprefix('testing/web-platform/tests/') for t in tests}
            assert all(r['status'] == 'OK' for r in results)
            focused = next(r for r in results if r['test'].endswith('/resolved-margins-overconstrained-block.html'))
            assert len(focused['subtests']) == 96
            passed = sum(t['status'] == 'PASS' for t in focused['subtests'])
            failed = sum(t['status'] == 'FAIL' for t in focused['subtests'])
            assert (passed, failed) == ((30, 66) if phase == 'baseline' else (96, 0))
            assert command['exit'] == (1 if phase == 'baseline' else 0)
            if phase == 'fixed':
                assert all(t['status'] == 'PASS' for r in results for t in r['subtests'])
            assert binaries() == json.loads((out / 'before-BINARIES.json').read_text())
            save(out / 'RESULT.json', dict(status='checked', pass_count=passed, fail=failed,
                 files=len(results), subtests=sum(len(r['subtests']) for r in results)))
    finally:
        save(out / 'after-BINARIES.json', binaries())
        save(out / 'CLEANUP.json', dict(groups_absent=runner.safe_cleanup,
             source_matches=sha(ROOT / NATIVE) == expected_native))


if __name__ == '__main__':
    main()
