import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-svg-absolute-factor-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
c = read(RUNTIME / 'CONFIG.json')
s = read(RUNTIME / 'STATE.json')
spec = importlib.util.spec_from_file_location('reviewed_tests', RUNTIME / 'tests.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
manifest = read(RUNTIME / 'DRAFT-FILES.json')
assert sha(RUNTIME / 'DRAFT-FILES.json') == '9c1a9ef56e3f9fa25fb4cb8b462f62edf360e9010a9b3559db593208ef2fc81b'
for name, digest in manifest.items():
    assert sha(RUNTIME / name) == digest, name
resources = read(RUNTIME / 'RESOURCES.json')
expected_keys = {(name, label) for name, labels in c['expected_subtests'].items() for label in labels}
assert len(expected_keys) == 34
phase_rows = {}
report = {'restoration_review_pending': True, 'phases': {}}
for phase in ('baseline', 'candidate'):
    directory = RUNTIME / ('wpt-' + phase)
    run = read(directory / 'RUN.json')
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    rows = [event for event in events if event.get('action') == 'test_status']
    starts = [event for event in events if event.get('action') == 'test_start']
    ends = [event for event in events if event.get('action') == 'test_end']
    assert rows == run['rows'] and starts == run['starts'] and ends == run['ends']
    keys = [(row['test'], row['subtest']) for row in rows]
    assert len(keys) == len(set(keys)) == 34 and set(keys) == expected_keys
    assert len(starts) == len(ends) == 5
    assert {event['test'] for event in starts} == set(c['expected_subtests'])
    assert {event['test'] for event in ends} == set(c['expected_subtests'])
    assert all(event['status'] == 'OK' for event in ends)
    assert sum(event.get('action') == 'suite_start' for event in events) == 1
    assert sum(event.get('action') == 'suite_end' for event in events) == 1
    assert not tests.infrastructure_faults(events) and not run['infrastructure_faults']
    assert run['complete'] and run['before'] == run['after']
    assert run['exit'] == (1 if phase == 'baseline' else 0)
    assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    state = s['phases'][phase]
    assert state['build_exit'] == read(RUNTIME / (phase + '-build.json'))['exit'] == 0
    before = state['source_before_build']
    assert before == state['source_after_build']
    source_map = {**c['head_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    assert before['sources'] == source_map and len(source_map) == 53
    assert before['head'] == c['head']
    original = read(RUNTIME / 'BEFORE.json')
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        assert before[key] == original[key]
    if phase == 'baseline':
        assert before['native_diff_sha256'] == hashlib.sha256(b'').hexdigest()
    pins = {**resources, **source_map,
            **{name: sha(RUNTIME / fixture) for name, fixture in c['install'].items()},
            **state['binary_pins']}
    assert run['before'] == pins
    counts = dict(collections.Counter(row['status'] for row in rows))
    assert counts == ({'PASS': 26, 'FAIL': 8} if phase == 'baseline' else {'PASS': 34})
    phase_rows[phase] = dict(zip(keys, rows))
    report['phases'][phase] = {'counts': counts, 'harness_ok': 5, 'role_pins': len(pins),
        'raw_sha256': sha(directory / 'raw.json'), 'run_sha256': sha(directory / 'RUN.json'),
        'binary_pins': state['binary_pins'], 'build_exit': 0,
        'source_native_diff_sha256': before['native_diff_sha256']}
repairs = []
for key, old in phase_rows['baseline'].items():
    new = phase_rows['candidate'][key]
    assert new['status'] == 'PASS'
    if old['status'] == 'FAIL':
        assert key[0] in c['main_tests'] and key[1] in c['baseline_allowed_failure_messages']
        assert c['baseline_allowed_failure_messages'][key[1]] in old['message']
        repairs.append({'test': key[0], 'subtest': key[1], 'baseline_message': old['message']})
assert len(repairs) == 8
comparison = read(RUNTIME / 'COMPARISON.json')
assert not comparison['regressions'] and not comparison['changed_failures']
assert {tuple(key) for key in comparison['repaired']} == {(r['test'], r['subtest']) for r in repairs}
assert set(c['candidate_pins']) == {'dom/svg/SVGLength.cpp'}
assert s['lint_exit'] == 0
report.update(repairs=repairs, controls_preserved=18, pending_overlay_independence=True,
              pristine_upstream_runtime=False, no_native_acceptance=True)
(HERE / 'PHASES.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'phases': {k: v['counts'] for k, v in report['phases'].items()},
                  'repairs': len(repairs), 'controls': 18, 'restoration_pending': True}))
