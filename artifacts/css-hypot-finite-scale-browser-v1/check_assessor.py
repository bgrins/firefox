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


assessor = load('combined_assessor', HERE / 'assess.py')
policy = json.loads((HERE / 'POLICY.json').read_bytes())['wpt']
checks = load('existing_checks', ROOT / policy['checks_helper'])
policy = dict(policy, tests={test: 'testharness' for test in policy['expected_subtests']},
              held_subtests={}, cardinality_description='Synthetic exact227/16/211/4 roster')
policy['regression_subtests'] = {
    test: [name for name in names if name not in policy['target_subtests'].get(test, [])]
    for test, names in policy['expected_subtests'].items()}
targets = {(test, name) for test, names in policy['target_subtests'].items() for name in names}
controls = {(test, name) for test, names in policy['regression_subtests'].items() for name in names}


def fixture(role, all_pass=False):
    binding = {'sha256': 'a' * 64, 'path': '/synthetic/application.ini', 'resolved': '/synthetic/application.ini',
               'browser_build_id': role, 'revision': policy['phase_revisions'][role],
               'build_revision': policy['phase_revisions'][role], 'harness_revision': policy['harness_revision'],
               'source_role': role}
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False,
               'browser_build_id': role, 'revision': policy['harness_revision']}}]
    for test, names in policy['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': test})
        for name in names:
            fails = role == 'original' and not all_pass and (test, name) in targets
            row = {'action': 'test_status', 'test': test, 'subtest': name, 'status': 'FAIL' if fails else 'PASS'}
            if fails:
                row['expected'] = 'PASS'
            events.append(row)
        events.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, binding


def exit_code(events):
    for code in (0, 1):
        if checks.exit_matches_results(code, [row for row in events if row['action'] in ('test_status', 'test_end')]):
            return code
    raise AssertionError('No consistent exit')


def observe(events, binding, original=None, settings=policy, code=None):
    return assessor.assess(events, exit_code(events) if code is None else code, settings, checks, original, binding)


original_events, original_binding = fixture('original')
candidate_events, candidate_binding = fixture('candidate')
original = observe(original_events, original_binding)
candidate = observe(candidate_events, candidate_binding, original)
assert original['complete'] and candidate['comparison_gate_passed']
assert len(candidate['rows']) == 227 and len(candidate['regression_signature']) == 215
passing_events, passing_binding = fixture('original', all_pass=True)
passing_original = observe(passing_events, passing_binding)
assert passing_original['complete'] and observe(candidate_events, candidate_binding, passing_original)['comparison_gate_passed']

control_identity = sorted(identity for identity in controls if identity[0] not in policy['candidate_required_pass_pages'])[0]


def control_row(events):
    return next(row for row in events if (row.get('test'), row.get('subtest')) == control_identity)


failed_original_events = copy.deepcopy(original_events)
failed_candidate_events = copy.deepcopy(candidate_events)
for events in (failed_original_events, failed_candidate_events):
    control_row(events).update(status='FAIL', expected='PASS', message='Stable existing assertion failure')
failed_original = observe(failed_original_events, original_binding)
assert failed_original['complete']
assert observe(failed_candidate_events, candidate_binding, failed_original)['comparison_gate_passed']
expected_original_events = copy.deepcopy(failed_original_events)
expected_candidate_events = copy.deepcopy(failed_candidate_events)
for events in (expected_original_events, expected_candidate_events):
    control_row(events).update(expected='FAIL', known_intermittent=[])
expected_original = observe(expected_original_events, original_binding)
assert expected_original['complete']
assert observe(expected_candidate_events, candidate_binding, expected_original)['comparison_gate_passed']

negative = {}
kinds = [
    'missing_target', 'missing_control', 'duplicate_control', 'missing_page_end', 'missing_suite_end',
    'extra_callback', 'target_failure', 'target_timeout', 'control_pass_to_fail', 'control_fail_to_pass',
    'control_failure_message', 'control_expected_presence', 'control_intermittent_presence',
    'ending_status', 'ending_message', 'ending_expected_presence', 'ending_intermittent_presence',
    'original_passing_target_message', 'wrong_original_revision', 'wrong_candidate_revision',
    'wrong_harness_revision', 'platform_change', 'crash', 'wrong_exit', 'fixture_typeerror',
    'new_fixture_stable_failure', 'declared_target_partition_change', 'declared_control_partition_change', 'held_control_waiver',
]
for kind in kinds:
    events, binding, origin, settings = copy.deepcopy(candidate_events), copy.deepcopy(candidate_binding), copy.deepcopy(original), copy.deepcopy(policy)
    rows = [row for row in events if row['action'] == 'test_status']
    target = next(row for row in rows if (row['test'], row['subtest']) in targets)
    control = control_row(events)
    ending = next(row for row in events if row['action'] == 'test_end')
    code = None
    if kind == 'missing_target': events.remove(target)
    elif kind == 'missing_control': events.remove(control)
    elif kind == 'duplicate_control': events.insert(events.index(control), copy.deepcopy(control))
    elif kind == 'missing_page_end': events.remove(ending)
    elif kind == 'missing_suite_end': events.pop()
    elif kind == 'extra_callback':
        extra = copy.deepcopy(control); extra['subtest'] = 'Unlisted callback'
        events.insert(events.index(control), extra)
    elif kind == 'target_failure': target.update(status='FAIL', expected='PASS')
    elif kind == 'target_timeout': target.update(status='TIMEOUT', expected='PASS')
    elif kind == 'control_pass_to_fail': control.update(status='FAIL', expected='PASS')
    elif kind == 'control_fail_to_pass': origin = copy.deepcopy(failed_original)
    elif kind == 'control_failure_message':
        events, origin = copy.deepcopy(failed_candidate_events), copy.deepcopy(failed_original)
        control_row(events)['message'] = 'Different failure'
    elif kind == 'control_expected_presence': control['expected'] = 'PASS'
    elif kind == 'control_intermittent_presence': control['known_intermittent'] = []
    elif kind == 'ending_status': ending['status'] = 'TIMEOUT'
    elif kind == 'ending_message': ending['message'] = 'Changed'
    elif kind == 'ending_expected_presence': ending['expected'] = 'OK'
    elif kind == 'ending_intermittent_presence': ending['known_intermittent'] = []
    elif kind == 'original_passing_target_message':
        origin = copy.deepcopy(passing_original); target['message'] = 'Changed passing callback'
    elif kind == 'wrong_original_revision': origin['run_binding']['revision'] = '0' * 40
    elif kind == 'wrong_candidate_revision': binding['revision'] = '0' * 40
    elif kind == 'wrong_harness_revision': binding['harness_revision'] = '0' * 40
    elif kind == 'platform_change': events[0]['run_info']['os'] = 'different'
    elif kind == 'crash': events.insert(-1, {'action': 'crash'})
    elif kind == 'wrong_exit': code = 1
    elif kind == 'fixture_typeerror':
        row = next(row for row in rows if row['test'] in settings['fixture_target_pages'])
        row.update(status='FAIL', expected='PASS', message='Unhandled rejection: TypeError: document.body is null')
    elif kind == 'new_fixture_stable_failure':
        fixture_identity = next(identity for identity in controls if identity[0] in policy['candidate_required_pass_pages'])
        original_copy = copy.deepcopy(original_events)
        for stream in (original_copy, events):
            next(row for row in stream if (row.get('test'), row.get('subtest')) == fixture_identity).update(status='FAIL', expected='PASS', message='Stable new fixture failure')
        origin = observe(original_copy, original_binding)
    elif kind == 'declared_target_partition_change': settings['target_subtests'][target['test']].remove(target['subtest'])
    elif kind == 'declared_control_partition_change': settings['regression_subtests'][control['test']].remove(control['subtest'])
    elif kind == 'held_control_waiver': settings['held_subtests'][control['test']] = [control['subtest']]
    result = observe(events, binding, origin, settings, code)
    assert not result['comparison_gate_passed'], kind
    negative[kind] = {'errors': result['errors'], 'comparison_errors': result['comparison_errors']}
print(json.dumps({'positive_scenarios': ['targets_improve', 'all_pass_original', 'stable_unexpected_control_failure',
                                       'stable_expected_control_failure'], 'negative_scenarios': negative,
                  'callbacks': 227, 'target_count': 16, 'controls': 211, 'pages': 4,
                  'regression_signatures': 215, 'actual_browser_execution': False}, sort_keys=True))
