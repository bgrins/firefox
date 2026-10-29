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


policy = json.loads((HERE / 'POLICY.json').read_bytes())
settings = policy['wpt']
assessor = load('shadow_assessor_check', HERE / 'assess.py')
checks = load('shadow_checks', ROOT / settings['checks_helper'])
phase = dict(settings, tests={p: 'testharness' for p in settings['expected_subtests']},
             held_subtests={}, cardinality_description='Synthetic exact98 control')
targets = {(test, name) for test, names in settings['target_subtests'].items() for name in names}
known = ('/dom/nodes/moveBefore/custom-element-move-reactions.html',
         'connectedMove runs when custom element is nested within a shadow root')


def sample(role):
    binding = dict(policy['application_metadata'], source_role=role,
                   revision=settings['phase_revisions'][role],
                   build_revision=settings['phase_revisions'][role],
                   harness_revision=settings['harness_revision'])
    if role == 'candidate':
        binding['browser_build_id'] = 'synthetic-new-build'
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False,
               'revision': settings['harness_revision'], 'browser_build_id': binding['browser_build_id']}}]
    for test, names in settings['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': test})
        for name in names:
            status = 'FAIL' if role == 'original' and (test, name) in targets else 'PASS'
            expected = 'FAIL' if (test, name) == known else 'PASS'
            row = {'action': 'test_status', 'test': test, 'subtest': name,
                   'status': status, 'known_intermittent': []}
            if expected != status:
                row['expected'] = expected
            events.append(row)
        events.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, binding


old_events, old_binding = sample('original')
old = assessor.assess(old_events, 1, phase, checks, run_binding=old_binding)
assert old['complete'] and len(old['regression_signature']) == 106
events, binding = sample('candidate')


def evaluate(rows, code=1, current_binding=binding):
    return assessor.assess(rows, code, phase, checks, original=old, run_binding=current_binding)


result = evaluate(events)
assert result['comparison_gate_passed'] and len(result['unexpected']) == 1
assert result['observed_subtest_count'] == 98
assert 'Shadow move-context' in result['oracle_caveat']
rejected = 0
for identity in targets:
    bad = copy.deepcopy(events)
    row = next(e for e in bad if (e.get('test'), e.get('subtest')) == identity)
    row['status'] = 'FAIL'
    assert not evaluate(bad)['comparison_gate_passed']
    rejected += 1
for field, value in [('message', 'changed'), ('expected', 'FAIL'), ('known_intermittent', ['FAIL'])]:
    bad = copy.deepcopy(events)
    row = next(e for e in bad if e.get('action') == 'test_status' and (e['test'], e['subtest']) not in targets)
    row[field] = value
    assert not evaluate(bad)['comparison_gate_passed']
    rejected += 1
bad = copy.deepcopy(events)
row = next(e for e in bad if e.get('action') == 'test_status' and (e['test'], e['subtest']) not in targets)
del row['known_intermittent']
assert not evaluate(bad)['comparison_gate_passed']
rejected += 1
for action in ['test_status', 'test_end']:
    bad = copy.deepcopy(events)
    del bad[next(i for i, e in enumerate(bad) if e.get('action') == action)]
    assert not evaluate(bad)['comparison_gate_passed']
    rejected += 1
assert not evaluate(events, code=0)['comparison_gate_passed']
assert not evaluate(events, current_binding=dict(binding, revision=old_binding['revision'], build_revision=old_binding['revision']))['comparison_gate_passed']
rejected += 2
print(json.dumps({'synthetic_accepts': 1, 'rejected_mutations': rejected,
                  'candidate_expected_fail_to_pass_exit1_supported': True,
                  'known_intermittent_empty_presence_preserved': True,
                  'observed_browser_results': False}))
