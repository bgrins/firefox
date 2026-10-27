import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
R = ROOT / 'artifacts/css-cssom-client-comparison-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate(mapping, base):
    for name, digest in mapping.items():
        assert sha(base / name) == digest, name
def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

assert sha(R / 'DRAFT-FILES.json') == '67935750362c281b5d3413a6a9c8516915d962a2b2f6458c30f3f5104366dd1d'
authenticate(read(R / 'DRAFT-FILES.json'), R)
authenticate(read(R / 'REFERENCES.json'), ROOT)
c, state = read(R / 'CONFIG.json'), read(R / 'STATE.json')
producer = ROOT / 'artifacts/css-cssom-client-comparison-v1'
for name in ('run.py', 'tests.py', 'reuse.py', 'epoch_gate.py', 'baseline_gate.py'):
    assert (R / name).read_bytes() == (producer / name).read_bytes()
old_config = read(producer / 'CONFIG.json')
assert {key for key in c.keys() | old_config.keys() if c.get(key) != old_config.get(key)} == {'epoch', 'epoch_receipt', 'ready_for_execution'}
tests = load('client_tests', R / 'tests.py')
before, resources = read(R / 'BEFORE.json'), read(R / 'RESOURCES.json')
fixture = next(iter(c['install']))
assert len(c['guard_sources']) == 48 and len(c['sources']) == 31
assert len(c['install']) == 1
epoch = ROOT / c['epoch']
authenticate(read(epoch / 'FILES.json'), epoch)
installation = read(epoch / 'INSTALLATION.json')
existing_wpt = installation['owned_test']
assert existing_wpt in c['existing_tests'] and existing_wpt != fixture
assert resources[existing_wpt] == c['existing_test_pins'][existing_wpt] == installation['owned_test_sha256']
runs = {}
for phase, count, files in [('baseline', 29, 8), ('candidate', 170, 21)]:
    directory = R / ('wpt-' + phase)
    run = read(directory / 'RUN.json')
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
        assert run[key] == [e for e in events if e.get('action') == action]
    expected = c['baseline_expected_subtests'] if phase == 'baseline' else c['expected_subtests']
    assert run['complete'] is True and run['exit'] in (0, 1)
    assert run['exit'] == 0 or any(r['status'] == 'FAIL' for r in run['rows'])
    assert len(run['rows']) == len({(r['test'], r['subtest']) for r in run['rows']}) == count
    assert len(expected) == files
    assert Counter(e['test'] for e in run['starts']) == Counter(e['test'] for e in run['ends']) == Counter({t: 1 for t in expected})
    assert all(e['status'] == 'OK' for e in run['ends'])
    assert all(r['status'] in ('PASS', 'FAIL') for r in run['rows'])
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
    tests.require_phase(SimpleNamespace(CONFIG=c, need=need), phase, run)
    build = state['phases'][phase]
    assert build['build_exit'] == 0 and build['source_before_build'] == build['source_after_build']
    sources = {**c['head_pins'], **c['baseline_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    assert build['source_after_build']['sources'] == sources
    assert run['before'] == run['after'] == {**resources, **sources,
        fixture: sha(R / c['install'][fixture]), **build['binary_pins']}
    assert run['before'][existing_wpt] == installation['owned_test_sha256']
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        assert build['source_after_build'][key] == before[key]
    runs[phase] = run

baseline_resources = {**resources, **c['head_pins'], **c['baseline_pins'], fixture: sha(R / c['install'][fixture])}
wpt = SimpleNamespace(CONFIG=c, ROOT=ROOT, HERE=R, need=need)
reuse = load('client_reuse', R / 'reuse.py')
retained = reuse.validate(wpt, load, sha, authenticate, baseline_resources)
assert len(retained['rows']) == 141
assert Counter(r['status'] for r in retained['rows']) == {'PASS': 129, 'FAIL': 12}
assert {r['test'] for r in retained['rows']}.isdisjoint(c['baseline_expected_subtests'])
combined = runs['baseline']['rows'] + retained['rows']
assert read(R / 'COMBINED-BASELINE.json')['rows'] == combined
def normalized(rows):
    return {(r['test'], r['subtest']): {k: r.get(k) for k in ('status', 'message', 'expected', 'known_intermittent')} for r in rows}
old_values, new_values = normalized(combined), normalized(runs['candidate']['rows'])
assert len(combined) == len(old_values) == len(new_values) == 170 and old_values.keys() == new_values.keys()
main = set(c['main_tests'])
selected = [r for r in runs['candidate']['rows'] if r['test'] in main]
assert len(selected) == 40 and all(r['status'] == 'PASS' for r in selected)
assert all(new_values[k]['status'] == 'PASS' for k in old_values if old_values[k]['status'] == 'PASS')
retained_failures = [k for k in new_values if new_values[k]['status'] == 'FAIL']
assert all(old_values[k] == new_values[k] for k in retained_failures)
repaired = [k for k in old_values if old_values[k]['status'] == 'FAIL' and new_values[k]['status'] == 'PASS']
main_repairs = [k for k in repaired if k[0] in main]
control_repairs = [k for k in repaired if k[0] not in main]
assert len(main_repairs) == 10
assert read(R / 'COMPARISON.json') == {'regressions': [], 'changed_failures': [], 'repaired': [list(k) for k in repaired], 'native_acceptance': False}
assert read(R / 'REPAIR-CLASSIFICATION.json') == {'main_repairs': [list(k) for k in main_repairs], 'control_fail_to_pass': [list(k) for k in control_repairs], 'new_bug_count': None}
changed = {n for n in runs['baseline']['before'] if runs['baseline']['before'][n] != runs['candidate']['before'][n]}
assert changed == {'dom/base/Element.cpp', 'dom/base/Element.h'} | set(state['phases']['candidate']['binary_pins'])
assert state['lint_exit'] == 0 and state['paired_preservation_passed'] is True
receipt = {'status': 'RESULTS_VERIFIED_RESTORATION_PENDING', 'runtime_draft_sha256': sha(R / 'DRAFT-FILES.json'),
    'fresh_baseline': dict(Counter(r['status'] for r in runs['baseline']['rows'])),
    'retained_baseline': {'PASS': 129, 'FAIL': 12}, 'combined_baseline': dict(Counter(r['status'] for r in combined)),
    'candidate': dict(Counter(r['status'] for r in runs['candidate']['rows'])),
    'main_candidate_PASS': 40, 'main_repairs': [list(k) for k in main_repairs],
    'control_fail_to_pass': [list(k) for k in control_repairs], 'regressions': [], 'changed_failure_diagnostics': [],
    'phase_pin_count': len(runs['candidate']['before']), 'changed_phase_inputs': sorted(changed),
    'raw_pins': {phase: sha(R / ('wpt-' + phase) / 'raw.json') for phase in runs},
    'run_pins': {phase: sha(R / ('wpt-' + phase) / 'RUN.json') for phase in runs},
    'restoration_assessed': False, 'native_acceptance': False, 'new_bug_count': None}
(D / 'RESULTS.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
