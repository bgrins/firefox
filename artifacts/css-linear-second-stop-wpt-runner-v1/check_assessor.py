import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


a = load('assessor_check', HERE / 'assess.py')
policy = json.loads((HERE / 'POLICY.json').read_text())
checks = load('real_lifecycle_checks', ROOT / policy['helpers']['checks'])
binding = {'sha256': 'a' * 64, 'path': 'application.ini', 'resolved': '/tmp/application.ini',
           'browser_build_id': '20261028000000', 'revision': policy['frozen_head']}
run_info = dict(os='mac', debug=False, browser_build_id=binding['browser_build_id'], revision=binding['revision'])
names = dict(policy['regression_subtests'], **policy['calibration_subtests'], **policy['target_subtests'])
target = next(iter(policy['target_subtests']))


def make(phase):
    p = dict(policy, phase=phase, tests=policy['phase_tests'][phase])
    events = [{'action': 'suite_start', 'run_info': run_info}]
    for test in p['tests']:
        events.append({'action': 'test_start', 'test': test})
        for name in names[test][:3] if phase == 'original-crash-1' else names[test]:
            events.append({'action': 'test_status', 'test': test, 'subtest': name, 'status': 'PASS'})
        if phase == 'original-crash-1':
            events.append({'action': 'crash', 'test': test, 'process': '123', 'minidump_path': '/tmp/owned/minidumps/test.dmp', 'signature': 'RustMozCrash'})
            events.append({'action': 'test_end', 'test': test, 'status': 'CRASH', 'expected': 'OK', 'extra': {'browser_pid': 123}})
        else:
            events.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, p


baseline_events, baseline_policy = make('original-baseline-1')
crash_events, crash_policy = make('original-crash-1')
candidate_events, candidate_policy = make('candidate-1')
assess = lambda events, code, p, original=None: a.assess(events, code, p, checks, original=original, run_binding=binding)
baseline = assess(baseline_events, 0, baseline_policy)
crash = assess(crash_events, 1, crash_policy)
original = {'baseline': baseline, 'crash': crash}
candidate = assess(candidate_events, 0, candidate_policy, original)
assert baseline['complete'] and baseline['phase_gate_passed'] and baseline['observed_subtest_count'] == 42
assert crash['phase_gate_passed'] and not crash['complete']
assert candidate['complete'] and candidate['comparison_gate_passed'] and candidate['observed_subtest_count'] == 48
empty_prefix = [e for e in crash_events if e['action'] != 'test_status']
assert assess(empty_prefix, 1, crash_policy)['phase_gate_passed']
rejected = []


def reject(name, events, code, p, original=None):
    result = assess(events, code, p, original)
    assert not result['phase_gate_passed'], name
    rejected.append({'name': name, 'errors': result['errors'] + result['comparison_errors']})


e = copy.deepcopy(crash_events)
next(x for x in e if x['action'] == 'crash')['test'] = '/unrelated.html'
reject('unrelated crash', e, 1, crash_policy)
reject('no crash evidence', [x for x in crash_events if x['action'] != 'crash'], 1, crash_policy)
e = copy.deepcopy(crash_events)
next(x for x in e if x['action'] == 'test_end')['status'] = 'TIMEOUT'
reject('timeout instead of crash', e, 1, crash_policy)
e = copy.deepcopy(crash_events)
c = next(x for x in e if x['action'] == 'crash')
e.remove(c)
e.insert(0, c)
reject('crash outside target interval', e, 1, crash_policy)
e = copy.deepcopy(crash_events)
next(x for x in e if x['action'] == 'crash')['process'] = '456'
reject('unrelated browser process', e, 1, crash_policy)
e = copy.deepcopy(crash_events)
next(x for x in e if x['action'] == 'test_status')['status'] = 'FAIL'
reject('pre-trigger calibration failure', e, 1, crash_policy)
reject('false zero crash exit', crash_events, 0, crash_policy)
reject('additional infrastructure failure', crash_events + [{'action': 'log', 'level': 'ERROR', 'message': 'server failed'}], 1, crash_policy)
e = copy.deepcopy(candidate_events)
next(x for x in e if x['action'] == 'test_status' and x['test'] == target)['status'] = 'FAIL'
reject('candidate target failure', e, 1, candidate_policy, original)
e = copy.deepcopy(candidate_events)
next(x for x in e if x['action'] == 'test_status' and x['test'] in policy['calibration_subtests'])['status'] = 'FAIL'
reject('unsupported feature calibration', e, 1, candidate_policy, original)
e = copy.deepcopy(candidate_events)
next(x for x in e if x['action'] == 'test_status' and x['test'] in policy['regression_subtests'])['message'] = 'changed'
reject('regression message drift', e, 0, candidate_policy, original)
reject('missing baseline', candidate_events, 0, candidate_policy, {'crash': crash})
e = copy.deepcopy(candidate_events)
row = next(x for x in e if x['action'] == 'test_status')
e.insert(e.index(row), dict(row))
reject('duplicated subtest', e, 0, candidate_policy, original)
e = copy.deepcopy(candidate_events)
e[0]['run_info']['browser_build_id'] = 'wrong'
reject('unbound BuildID', e, 0, candidate_policy, original)
e = copy.deepcopy(candidate_events)
e.remove(next(x for x in e if x['action'] == 'test_status'))
reject('missing row', e, 0, candidate_policy, original)
print(json.dumps({'synthetic_controls_only': True, 'positive_controls': 4, 'rejected': rejected}, indent=2))
