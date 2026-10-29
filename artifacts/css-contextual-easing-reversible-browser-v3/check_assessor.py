import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assessor = load('check_assessor', HERE / 'assess.py')
policy = json.loads((HERE / 'POLICY.json').read_bytes())['wpt']
checks = load('existing_checks', ROOT / policy['checks_helper'])
policy = dict(policy, tests={test: 'testharness' for test in policy['expected_subtests']}, held_subtests={}, regression_subtests={}, cardinality_description='Synthetic exact roster controls')
targets = {(test, name) for test, names in policy['target_subtests'].items() for name in names}


def fixture(role):
    binding = {'sha256': 'a' * 64, 'path': '/synthetic/application.ini', 'resolved': '/synthetic/application.ini', 'browser_build_id': role, 'revision': policy['phase_revisions'][role], 'build_revision': policy['phase_revisions'][role], 'harness_revision': policy['harness_revision'], 'source_role': role}
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False, 'browser_build_id': role, 'revision': policy['harness_revision']}}]
    for test, names in policy['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': test})
        for name in names:
            status = 'FAIL' if role == 'original' and (test, name) in targets else 'PASS'
            row = {'action': 'test_status', 'test': test, 'subtest': name, 'status': status}
            if status == 'FAIL':
                row['expected'] = 'PASS'
            events.append(row)
        events.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, binding


old_events, old_binding = fixture('original')
original = assessor.assess(old_events, 1, policy, checks, run_binding=old_binding)
assert original['complete']
events, binding = fixture('candidate')
result = assessor.assess(events, 0, policy, checks, original, binding)
assert result['comparison_gate_passed']
failures = {}
for kind in ('missing', 'duplicate', 'target_failure', 'shared_page_control_change', 'wrong_original_revision', 'wrong_candidate_revision', 'crash', 'wrong_exit', 'fixture_typeerror', 'wrong_harness_revision'):
    altered, origin, meta, code = copy.deepcopy(events), copy.deepcopy(original), copy.deepcopy(binding), 0
    rows = [row for row in altered if row['action'] == 'test_status']
    if kind == 'missing': altered.remove(rows[0])
    elif kind == 'duplicate': altered.insert(altered.index(rows[0]), copy.deepcopy(rows[0]))
    elif kind == 'target_failure':
        row = next(row for row in rows if (row['test'], row['subtest']) in targets)
        row.update(status='FAIL', expected='PASS'); code = 1
    elif kind == 'shared_page_control_change':
        row = next(row for row in rows if row['test'] in policy['target_subtests'] and (row['test'], row['subtest']) not in targets)
        row['message'] = 'changed independent control signature'
    elif kind == 'wrong_original_revision':
        origin['run_binding']['revision'] = origin['run_info']['revision'] = '0' * 40
    elif kind == 'wrong_candidate_revision':
        meta['revision'] = altered[0]['run_info']['revision'] = '0' * 40
    elif kind == 'crash': altered.insert(-1, {'action': 'crash'})
    elif kind == 'wrong_exit': code = 1
    elif kind == 'fixture_typeerror':
        row = next(row for row in rows if row['test'] in policy['fixture_target_pages'])
        row.update(status='FAIL', expected='PASS', message='promise_test: Unhandled rejection with value: TypeError: document.body is null'); code = 1
    elif kind == 'wrong_harness_revision':
        meta['harness_revision'] = altered[0]['run_info']['revision'] = '0' * 40
    assessed = assessor.assess(altered, code, policy, checks, origin, meta)
    assert not assessed['comparison_gate_passed'], kind
    failures[kind] = True
print(json.dumps({'synthetic_positive': 2, 'synthetic_negative': failures, 'actual_browser_execution': False}, sort_keys=True))
old_runtime = ROOT / 'artifacts/css-contextual-easing-reversible-browser-runtime-1/original-wpt'
actual_events = [json.loads(line) for line in (old_runtime / 'raw.jsonl').read_text().splitlines()]
actual_meta = json.loads((old_runtime / 'APPLICATION-METADATA.json').read_bytes())
actual_meta.update(build_revision=actual_meta['revision'], harness_revision=policy['harness_revision'], source_role='original')
actual = assessor.assess(actual_events, 1, policy, checks, run_binding=actual_meta)
assert not actual['complete'] and len(actual['fixture_setup_errors']) == 16
assert actual['errors'] == ['new target fixture has an uncaught setup/runtime exception']
print(json.dumps({'historical_invalid_fixture_replay': 'REJECTED', 'setup_errors': 16, 'harness_app_revision_gate': 'PASS', 'native_baseline_claim': False}, sort_keys=True))
