import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = json.loads((HERE / 'RUN-INPUTS.json').read_text())
    for name, expected in manifest.items():
        assert digest(HERE / name) == expected, name
    plan = json.loads((HERE / 'RUN-PLAN.json').read_text())
    assert len(plan['fixtures']) == len(plan['suites']) == 1
    assert json.loads((HERE / 'SOURCE-ROLES.json').read_text()) == {}
    assert subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == plan['head']
    pins = json.loads((HERE / 'runtime-inputs/test-source-pins.json').read_text())
    for name, expected in pins.items():
        path = ROOT / name
        assert digest(path) == expected if expected is not None else not path.exists(), name
    retained = json.loads((HERE / 'runtime-inputs/retained-build.json').read_text())
    for name, expected in retained['binaries'].items():
        assert digest(ROOT / name) == expected, name
    for name in plan['fixtures']:
        assert not (ROOT / name).exists()
    spec = importlib.util.spec_from_file_location('probe_analysis', HERE / 'analyze.py')
    analysis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analysis)
    expected = json.loads((HERE / 'EXPECTED-BASELINE.json').read_text())
    url = expected['harness'][0]['test']
    events = [{'action': 'suite_start'}, {'action': 'test_start', 'test': url}]
    events += [{'action': 'test_status', **r} for r in expected['subtests']]
    events += [{'action': 'test_end', **expected['harness'][0]}, {'action': 'suite_end'}]
    rejected = []
    with tempfile.TemporaryDirectory(prefix='named-range-probe-check-') as directory:
        def parse(rows):
            path = Path(directory) / 'raw.jsonl'
            path.write_text(''.join((r if isinstance(r, str) else json.dumps(r)) + '\n' for r in rows))
            return analysis.parse(path)

        assert analysis.rows(parse(events)) == analysis.rows(expected)
        for name, rows in [
            ('missing-callback', events[:2] + events[3:]),
            ('duplicate-callback', events[:2] + [events[2]] + events[2:]),
            ('duplicate-harness', events[:-1] + [events[-2], events[-1]]),
            ('missing-harness', events[:-2] + [events[-1]]),
            ('missing-suite-end', events[:-1]),
            ('crash', events + [{'action': 'crash'}]),
            ('error-log', events + [{'action': 'log', 'level': 'ERROR'}]),
            ('duplicate-json-key', ['{"action":"suite_start","action":"suite_start"}'] + events[1:]),
        ]:
            try:
                parse(rows)
            except (AssertionError, ValueError):
                rejected.append(name)
            else:
                raise AssertionError(name)
        for name, index, field, value in [
            ('timeout', 2, 'status', 'TIMEOUT'),
            ('wrong-callback', 2, 'subtest', 'unrelated case'),
            ('wrong-harness', 4, 'status', 'FAIL'),
        ]:
            rows = copy.deepcopy(events)
            rows[index][field] = value
            try:
                parse(rows)
            except AssertionError:
                rejected.append(name)
            else:
                raise AssertionError(name)
        for index in [2, 3]:
            rows = copy.deepcopy(events)
            rows[index]['status'] = 'PASS' if rows[index]['status'] == 'FAIL' else 'FAIL'
            assert analysis.rows(parse(rows)) != analysis.rows(expected)
            rejected.append('changed-baseline-' + str(index))
    report = {'status': 'pass', 'runtime_inputs': len(manifest), 'native_test_pins': len(pins),
              'expected_callbacks': 2, 'expected_harness': 1, 'rejected_controls': rejected,
              'browser_execution': False, 'native_changes': False}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
