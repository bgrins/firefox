import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = json.loads((HERE / 'INPUTS.json').read_text())
TEST = next(p for p in INPUTS if p.endswith('.html'))
CONTROLS = ['grid-baseline-align-001.html', 'grid-baseline-align-cycles-001.html',
            'grid-baseline-justify-001.html']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(out, name, value):
    (out / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    phase = sys.argv[1]
    assert phase in ['baseline', 'build', 'fixed']
    out = HERE / phase
    assert not out.exists()
    version = 'candidate' if phase == 'fixed' else 'original'
    for path, hashes in INPUTS.items():
        assert sha(ROOT / path) == hashes.get(version, hashes['candidate']), path
        assert sha(HERE / 'candidate' / path) == hashes['candidate'], path
    authority = (HERE / 'build/BINARIES-AFTER.json' if phase == 'fixed' else
                 ROOT / 'artifacts/css-flex-unconstrained-history-native-trace-20261112-v1/restored-build-BINARIES.json')
    expected = json.loads(authority.read_text())

    def binaries():
        return {p: dict(sha256=sha(p), bytes=Path(p).stat().st_size) for p in expected}

    assert binaries() == expected
    out.mkdir()
    save(out, 'INPUTS.json', INPUTS)
    (out / 'runner.py').write_bytes(Path(__file__).read_bytes())
    save(out, 'BINARIES-BEFORE.json', expected)
    spec = importlib.util.spec_from_file_location('owned_process', HERE / 'process.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runner = module.Runner(out)
    env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
               MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))
    try:
        if phase == 'build':
            baseline = json.loads((HERE / 'baseline/RESULT.json').read_text())
            assert baseline['fail'] > 0 and baseline['controls_pass'] == 3
            for path, hashes in INPUTS.items():
                if 'original' in hashes:
                    (ROOT / path).write_bytes((HERE / 'candidate' / path).read_bytes())
            version = 'candidate'
            save(out, 'INSTALL.json', {p: sha(ROOT / p) for p in INPUTS})
            argv = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
            record, _ = runner.run(argv, ROOT, env, 'mach', timeout=1800)
            assert record['exit'] == 0
            assert binaries() != expected
            save(out, 'RESULT.json', dict(status='built', groups_absent=runner.safe_cleanup))
        else:
            if phase == 'fixed':
                assert json.loads((HERE / 'build/RESULT.json').read_text())['status'] == 'built'
            argv = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless',
                    '--no-pause-after-test', '--processes=1',
                    '--binary=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'),
                    '--log-raw=' + str(out / 'raw.log'),
                    '--log-wptreport=' + str(out / 'wptreport.json'), TEST]
            argv += [str(Path(TEST).parent / c) for c in CONTROLS]
            record, _ = runner.run(argv, ROOT, env, 'mach', timeout=300)
            results = json.loads((out / 'wptreport.json').read_text())['results']
            assert len(results) == 4
            result = next(r for r in results if r['test'].endswith(Path(TEST).name))
            assert result['status'] == 'OK' and len(result['subtests']) == 120
            assert all(t['status'] in ['PASS', 'FAIL'] for t in result['subtests'])
            failed = [t for t in result['subtests'] if t['status'] == 'FAIL']
            controls = [r for r in results if r is not result]
            assert {Path(r['test']).name for r in controls} == set(CONTROLS)
            assert all(r['status'] == 'PASS' for r in controls)
            assert record['exit'] == (1 if phase == 'baseline' else 0)
            assert bool(failed) == (phase == 'baseline')
            save(out, 'RESULT.json', dict(status=phase, passed=120-len(failed), fail=len(failed),
                 controls_pass=3, failures=failed, groups_absent=runner.safe_cleanup))
            assert binaries() == expected
    finally:
        save(out, 'BINARIES-AFTER.json', binaries())
        save(out, 'CLEANUP.json', dict(groups_absent=runner.safe_cleanup,
             sources_match=all(sha(ROOT / p) == h.get(version, h['candidate']) for p, h in INPUTS.items())))


if __name__ == '__main__':
    main()
