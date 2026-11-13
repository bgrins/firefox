import hashlib
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = ROOT / 'testing/web-platform/tests/css/cssom/block-used-margin-local-probe.html'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    expected = json.loads((ROOT / 'artifacts/css-container-unit-independence-repair-20261112-v1/fixed-BINARIES.json').read_text())
    def binaries():
        return {p: dict(sha256=sha(p), bytes=Path(p).stat().st_size) for p in expected}
    assert binaries() == expected
    assert not TARGET.exists() and not (HERE / 'COMMANDS.json').exists()
    spec = importlib.util.spec_from_file_location('owned_process', HERE / 'process.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runner = module.Runner(HERE)
    source = (HERE / 'diagnostic.html').read_bytes()
    TARGET.write_bytes(source)
    save('TEMPORARY-WPT.json', dict(path=str(TARGET), sha256=sha(TARGET)))
    save('BINARIES-BEFORE.json', binaries())
    argv = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless',
            '--no-pause-after-test', '--processes=1',
            '--binary=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'),
            '--log-raw=' + str(HERE / 'raw.log'),
            '--log-wptreport=' + str(HERE / 'wptreport.json'), str(TARGET.relative_to(ROOT))]
    env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZCONFIG=str(ROOT / 'mozconfig'),
               MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))
    try:
        record, _ = runner.run(argv, ROOT, env, 'mach', timeout=240)
        report = json.loads((HERE / 'wptreport.json').read_text())
        assert len(report['results']) == 1
        result = report['results'][0]
        observations = [json.loads(t['name'][4:]) for t in result['subtests'] if t['name'].startswith('OBS ')]
        assert record['exit'] == 0 and result['status'] == 'OK'
        assert len(observations) == len(result['subtests']) == 24
        assert all(t['status'] == 'PASS' for t in result['subtests'])
        save('OBSERVATIONS.json', observations)
        save('RESULT.json', dict(status='PASS observation probe only', observations=24,
             commands_terminal=True, groups_absent=record['group_absent'], normative_assertions=False))
    finally:
        if runner.safe_cleanup and TARGET.read_bytes() == source:
            TARGET.unlink()
        save('CLEANUP.json', dict(groups_absent=runner.safe_cleanup,
                                 temporary_removed=not TARGET.exists(), binaries_unchanged=binaries() == expected))
        save('BINARIES-AFTER.json', binaries())


if __name__ == '__main__':
    main()
