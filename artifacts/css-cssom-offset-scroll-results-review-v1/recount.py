import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
R = ROOT / 'artifacts/css-cssom-offset-scroll-comparison-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate(base, manifest):
    for name, digest in manifest.items():
        assert sha(base / name) == digest, name

assert sha(R / 'DRAFT-FILES.json') == '36c5b09da0fee41a2e25477d51529816d8a6d0b646fd7253b0d9cc1fae5dfe14'
authenticate(R, read(R / 'DRAFT-FILES.json'))
authenticate(ROOT, read(R / 'REFERENCES.json'))
c, state = read(R / 'CONFIG.json'), read(R / 'STATE.json')
producer = ROOT / 'artifacts/css-cssom-offset-scroll-comparison-v1'
for name in ('run.py', 'tests.py', 'baseline_gate.py'):
    assert (R / name).read_bytes() == (producer / name).read_bytes()
old_config = read(producer / 'CONFIG.json')
assert {key for key in c.keys() | old_config.keys() if c.get(key) != old_config.get(key)} == {'epoch', 'epoch_receipt', 'ready_for_execution'}
spec = importlib.util.spec_from_file_location('reviewed_tests', R / 'tests.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
before = read(R / 'BEFORE.json')
resources = read(R / 'RESOURCES.json')
fixture = next(iter(c['install']))
runs = {}
for phase, count, files in [('baseline', 61, 5), ('candidate', 141, 13)]:
    directory = R / ('wpt-' + phase)
    run = read(directory / 'RUN.json')
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
        assert run[key] == [e for e in events if e.get('action') == action]
    expected = c['baseline_expected_subtests'] if phase == 'baseline' else c['expected_subtests']
    assert run['complete'] is True and run['exit'] == (1 if phase == 'baseline' else 0)
    assert len(run['rows']) == len({(r['test'], r['subtest']) for r in run['rows']}) == count
    assert len(expected) == files
    assert Counter(e['test'] for e in run['starts']) == Counter(e['test'] for e in run['ends']) == Counter({t: 1 for t in expected})
    assert all(e['status'] == 'OK' for e in run['ends'])
    for test, names in expected.items():
        actual = [r['subtest'] for r in run['rows'] if r['test'] == test]
        assert len(actual) == len(names) == len(set(names)) and set(actual) == set(names)
    assert sum(e.get('action') == 'suite_start' for e in events) == sum(e.get('action') == 'suite_end' for e in events) == 1
    suite = next(e for e in events if e.get('action') == 'suite_start')
    assert suite['run_info']['os'] == 'mac' and suite['run_info']['revision'] == c['head']
    assert sorted(t for names in suite['tests'].values() for t in names) == sorted(expected)
    active = set()
    for event in events:
        if event.get('action') == 'test_start':
            assert event['test'] not in active
            active.add(event['test'])
        elif event.get('action') == 'test_status':
            assert event['test'] in active
        elif event.get('action') == 'test_end':
            assert event['test'] in active
            active.remove(event['test'])
    assert not active
    assert tests.infrastructure_faults(events) == run['infrastructure_faults'] == []
    assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    build = state['phases'][phase]
    assert build['build_exit'] == 0 and build['source_before_build'] == build['source_after_build']
    sources = {**c['head_pins'], **c['baseline_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    assert build['source_after_build']['sources'] == sources
    assert run['before'] == run['after'] == {**resources, **sources,
        fixture: sha(R / c['install'][fixture]), **build['binary_pins']}
    assert len(run['before']) == 318
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        assert build['source_after_build'][key] == before[key]
    runs[phase] = run

archive = ROOT / c['retained_baseline']
reanalysis = ROOT / c['reanalysis']
authenticate(archive, read(archive / 'FILES.json'))
authenticate(reanalysis, read(reanalysis / 'FILES.json'))
assert sha(reanalysis / 'FILES.json') == '66e7ac1437adf5dcf760bd771a3dd973e649d5dd5628d16ad5024fa7f8c99a95'
old = read(archive / 'wpt-baseline/RUN.json')
validated = read(reanalysis / 'BASELINE-REVALIDATED.json')
assert sha(archive / 'wpt-baseline/RUN.json') == validated['run_sha256']
assert sha(archive / 'wpt-baseline/raw.json') == validated['raw_sha256']
assert validated['revalidated_complete'] is True and old['complete'] is False
ac = read(archive / 'CONFIG.json')
assert ac['head_pins'] == c['head_pins'] and ac['baseline_pins'] == c['baseline_pins']
old_phase_resources = {**read(archive / 'RESOURCES.json'), **ac['head_pins'], **ac['baseline_pins']}
old_fixture = next(iter(ac['install']))
assert all(runs['baseline']['before'].get(n) == h for n, h in old_phase_resources.items() if n != old_fixture)
retained = [r for r in old['rows'] if r['test'] in c['expected_subtests']]
assert len(retained) == len({(r['test'], r['subtest']) for r in retained}) == 80
assert Counter(r['status'] for r in retained) == {'PASS': 76, 'FAIL': 4}
assert {r['test'] for r in retained}.isdisjoint(c['baseline_expected_subtests'])
combined = runs['baseline']['rows'] + retained
assert read(R / 'COMBINED-BASELINE.json')['rows'] == combined
def normalized(rows):
    return {(r['test'], r['subtest']): {k: r.get(k) for k in ('status', 'message', 'expected', 'known_intermittent')} for r in rows}
old_values, new_values = normalized(combined), normalized(runs['candidate']['rows'])
assert len(combined) == len(old_values) == len(new_values) == 141 and old_values.keys() == new_values.keys()
main = c['main_test']
main_old = [r for r in runs['baseline']['rows'] if r['test'] == main]
assert len(main_old) == 32
assert {r['subtest']: r['message'] for r in main_old if r['status'] == 'FAIL'} == c['baseline_failures']
assert all(r['status'] == 'PASS' for r in main_old if r['subtest'] not in c['baseline_failures'])
assert all(r['status'] == 'PASS' for r in runs['candidate']['rows'] if r['test'] == main)
assert all(new_values[k]['status'] == 'PASS' for k in old_values if old_values[k]['status'] == 'PASS')
retained_failures = [k for k in new_values if new_values[k]['status'] == 'FAIL']
assert len(retained_failures) == 4 and all(old_values[k] == new_values[k] for k in retained_failures)
repaired = [k for k in old_values if old_values[k]['status'] == 'FAIL' and new_values[k]['status'] == 'PASS']
assert set(repaired) == {(main, name) for name in c['baseline_failures']}
assert read(R / 'COMPARISON.json') == {'regressions': [], 'changed_failures': [], 'repaired': [list(k) for k in repaired], 'native_acceptance': False}
assert Counter(r['status'] for r in runs['baseline']['rows']) == {'PASS': 53, 'FAIL': 8}
assert Counter(r['status'] for r in combined) == {'PASS': 129, 'FAIL': 12}
assert Counter(r['status'] for r in runs['candidate']['rows']) == {'PASS': 137, 'FAIL': 4}
changed = {n for n in runs['baseline']['before'] if runs['baseline']['before'][n] != runs['candidate']['before'][n]}
assert changed == {'dom/base/Element.cpp'} | set(state['phases']['candidate']['binary_pins'])
assert state['lint_exit'] == 0 and state['paired_preservation_passed'] is True
receipt = {'status': 'RESULTS_VERIFIED_RESTORATION_PENDING', 'runtime_draft_sha256': sha(R / 'DRAFT-FILES.json'),
    'fresh_baseline': {'PASS': 53, 'FAIL': 8, 'files_OK': 5}, 'retained_baseline': {'PASS': 76, 'FAIL': 4},
    'combined_baseline': {'PASS': 129, 'FAIL': 12}, 'candidate': {'PASS': 137, 'FAIL': 4, 'files_OK': 13},
    'main_candidate_PASS': 32, 'fresh_controls_PASS': 29, 'repaired': [list(k) for k in repaired],
    'regressions': [], 'changed_failure_diagnostics': [], 'stable_phase_pins': 318,
    'changed_phase_inputs': sorted(changed), 'raw_pins': {phase: sha(R / ('wpt-' + phase) / 'raw.json') for phase in runs},
    'run_pins': {phase: sha(R / ('wpt-' + phase) / 'RUN.json') for phase in runs},
    'restoration_assessed': False, 'native_acceptance': False}
(D / 'RESULTS.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
