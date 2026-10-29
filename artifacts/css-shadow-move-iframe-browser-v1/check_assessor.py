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


settings = copy.deepcopy(json.loads((HERE / 'POLICY.json').read_bytes())['wpt'])
settings['harness_revision'] = 'a' * 40
settings['phase_revisions'] = {'original': 'b' * 40, 'candidate': 'a' * 40}
settings.update(tests={t: 'testharness' for t in settings['expected_subtests']},
                held_subtests={}, cardinality_description='Synthetic exact8 control')
assessor = load('iframe_assessor_check', HERE / 'assess.py')
checks = load('iframe_checks', ROOT / settings['checks_helper'])
targets = {(t, n) for t, names in settings['target_subtests'].items() for n in names}


def sample(role):
    binding = {'path': 'synthetic', 'resolved': 'synthetic', 'sha256': 'c' * 64,
               'browser_build_id': role, 'revision': settings['phase_revisions'][role],
               'build_revision': settings['phase_revisions'][role],
               'harness_revision': settings['harness_revision'], 'source_role': role}
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False,
               'revision': settings['harness_revision'], 'browser_build_id': role}}]
    for test, names in settings['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': test})
        for name in names:
            row = {'action': 'test_status', 'test': test, 'subtest': name,
                   'status': 'FAIL' if role == 'original' and (test, name) in targets else 'PASS',
                   'known_intermittent': []}
            if row['status'] == 'FAIL':
                row['expected'] = 'PASS'
            events.append(row)
        events.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, binding


old_events, old_binding = sample('original')
old = assessor.assess(old_events, 1, settings, checks, run_binding=old_binding)
assert old['complete'] and len(old['regression_signature']) == 7
events, binding = sample('candidate')


def evaluate(rows, code=0, meta=binding):
    return assessor.assess(rows, code, settings, checks, original=old, run_binding=meta)


assert evaluate(events)['comparison_gate_passed']
rejected = 0
for i, row in enumerate(events):
    if row.get('action') == 'test_status':
        bad = copy.deepcopy(events)
        bad[i]['status'] = 'FAIL'
        assert not evaluate(bad)['comparison_gate_passed']
        rejected += 1
for action in ['test_status', 'test_end']:
    bad = copy.deepcopy(events)
    del bad[next(i for i, row in enumerate(bad) if row.get('action') == action)]
    assert not evaluate(bad)['comparison_gate_passed']
    rejected += 1
bad = copy.deepcopy(events)
control = next(row for row in bad if row.get('action') == 'test_status' and (row['test'], row['subtest']) not in targets)
del control['known_intermittent']
assert not evaluate(bad)['comparison_gate_passed']
assert not evaluate(events, 1)['comparison_gate_passed']
assert not evaluate(events, meta=dict(binding, browser_build_id='wrong'))['comparison_gate_passed']
rejected += 3
print(json.dumps({'synthetic_accepts': 1, 'rejected_mutations': rejected,
                  'callbacks': 8, 'targets': 2, 'controls': 6, 'endings': 1,
                  'actual_browser_execution': False}))
