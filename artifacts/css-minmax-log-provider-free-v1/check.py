import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = read(HERE / 'POLICY.json')
baseline_policy = read(ROOT / policy['baseline_capsule']['directory'] / 'POLICY.json')
comparison = load('static_comparison', HERE / 'comparison.py')
assert comparison.expected_wpt(ROOT, policy) == policy['wpt']
assessor = load('static_assessor', HERE / 'assess.py')
checks = load('static_stream_checks', ROOT / policy['wpt']['checks_helper'])
settings = comparison.phase_policy(policy['wpt'])
old_settings = comparison.phase_policy(baseline_policy['wpt'])
app = baseline_policy['prepared_application_metadata']
targets = {(page, name) for page,names in settings['target_subtests'].items() for name in names}
assert len(targets) == 33
events = [{'action':'suite_start', 'run_info':{'os':'mac', 'debug':False, 'browser_build_id':app['browser_build_id'], 'revision':settings['harness_revision']}}]
for page,names in settings['expected_subtests'].items():
    events.append({'action':'test_start', 'test':page})
    for name in names:
        event = {'action':'test_status', 'test':page, 'subtest':name, 'status':'PASS'}
        if (page,name) in targets:
            event.update(status='FAIL', expected='PASS', message='synthetic old target')
        events.append(event)
    events.append({'action':'test_end', 'test':page, 'status':'OK'})
events.append({'action':'suite_end'})
original = assessor.assess(events, 1, old_settings, checks, run_binding=app)
assert original['complete']
candidate_app = dict(app, browser_build_id='synthetic-new-build', revision=policy['head'], build_revision=policy['head'], source_role='candidate')
events = copy.deepcopy(events)
events[0]['run_info']['browser_build_id'] = candidate_app['browser_build_id']
for event in events:
    if (event.get('test'), event.get('subtest')) in targets:
        event.update(status='PASS')
        event.pop('expected')
        event.pop('message')


def evaluate(stream, code=0):
    return assessor.assess(stream, code, settings, checks, original=original, run_binding=candidate_app)


positive = evaluate(events)
assert positive['complete'] and positive['comparison_gate_passed']
assert len(positive['rows']) == 578 and len(positive['regression_signature']) == 561
assert positive['regression_signature'] == original['regression_signature']
negative = []


def row(stream, predicate=lambda e: True):
    return next(e for e in stream if e.get('action') == 'test_status' and predicate(e))


def reject(name, mutation, code=0):
    stream = copy.deepcopy(events)
    mutation(stream)
    assert not evaluate(stream, code)['comparison_gate_passed'], name
    negative.append(name)


reject('target still FAIL', lambda s: row(s, lambda e:(e['test'],e['subtest']) in targets).update(status='FAIL', expected='PASS'), 1)
reject('control FAIL', lambda s: row(s, lambda e:(e['test'],e['subtest']) not in targets).update(status='FAIL', expected='PASS'), 1)
reject('control message changed', lambda s: row(s, lambda e:(e['test'],e['subtest']) not in targets).update(message='changed'))
reject('control expected presence changed', lambda s: row(s, lambda e:(e['test'],e['subtest']) not in targets).update(expected='PASS'))
reject('control intermittent changed', lambda s: row(s, lambda e:(e['test'],e['subtest']) not in targets).update(known_intermittent=['FAIL']))
reject('missing callback', lambda s:s.remove(row(s)))
reject('duplicate callback', lambda s:s.insert(2, copy.deepcopy(row(s))))
reject('renamed callback', lambda s:row(s).update(subtest='unknown'))
reject('missing ending', lambda s:s.remove(next(e for e in s if e.get('action')=='test_end')))
reject('ending changed', lambda s:next(e for e in s if e.get('action')=='test_end').update(message='changed'))
reject('missing suite end', lambda s:s.pop())
reject('crash', lambda s:s.append({'action':'crash'}))
reject('wrong BuildID', lambda s:s[0]['run_info'].update(browser_build_id='wrong'))
reject('wrong harness revision', lambda s:s[0]['run_info'].update(revision='wrong'))
reject('wrong exit', lambda s:None, 1)
legacy_rows = read(ROOT / 'artifacts/css-minmax-log-integration-plan-v1/PLAN.json')['historical_legacy_failure_rows']
legacy_names = {(event['test'], event['subtest']) for event in legacy_rows}
assert len(legacy_names) == 2 and not legacy_names & targets
legacy_candidate = copy.deepcopy(events)
for event in legacy_candidate:
    if (event.get('test'), event.get('subtest')) in legacy_names:
        event.update(status='FAIL', message='synthetic preserved legacy failure', known_intermittent=[])
legacy_events = copy.deepcopy(legacy_candidate)
legacy_events[0]['run_info']['browser_build_id'] = app['browser_build_id']
for event in legacy_events:
    if (event.get('test'), event.get('subtest')) in targets:
        event.update(status='FAIL', expected='PASS', message='synthetic old target')
legacy_original = assessor.assess(legacy_events, 1, old_settings, checks, run_binding=app)
assert legacy_original['complete']
legacy_positive = assessor.assess(legacy_candidate, 0, settings, checks, original=legacy_original, run_binding=candidate_app)
assert legacy_positive['comparison_gate_passed'] and len(legacy_positive['regression_signature']) == 561
for label, change in [('legacy FAIL became PASS', {'status':'PASS'}),
                      ('legacy message changed', {'message':'changed'}),
                      ('legacy expected field added', {'expected':'FAIL'}),
                      ('legacy intermittent changed', {'known_intermittent':['PASS']})]:
    stream = copy.deepcopy(legacy_candidate)
    row(stream, lambda e:(e['test'],e['subtest']) in legacy_names).update(change)
    assert not assessor.assess(stream, 0, settings, checks, original=legacy_original, run_binding=candidate_app)['comparison_gate_passed'], label
    negative.append(label)
print(json.dumps({'synthetic_candidate_PASS':578, 'targets':33, 'strict_signatures':561,
                  'synthetic_legacy_failure_preservation':True,
                  'negative_checks':negative, 'actual_baseline_replayed':False,
                  'owner_browser_or_build_executed':False}, indent=2))

reference = comparison.replay_combined(ROOT, policy, assessor, checks)
comparison.require_equal_results(reference, copy.deepcopy(reference), assessor)
provider_negative = []
for label, field, mutation in [
    ('target message', 'rows', lambda rows: rows[0].update(message='altered')),
    ('expected presence', 'rows', lambda rows: rows[0].update(expected=rows[0]['status'])),
    ('intermittent content', 'rows', lambda rows: rows[0].update(known_intermittent=['PASS'])),
    ('intermittent presence', 'rows', lambda rows: rows[0].pop('known_intermittent', None)),
    ('target status', 'rows', lambda rows: rows[0].update(status='FAIL')),
    ('missing row', 'rows', lambda rows: rows.pop()),
    ('duplicated row', 'rows', lambda rows: rows.__setitem__(1, copy.deepcopy(rows[0]))),
    ('ending message', 'ends', lambda rows: rows[0].update(message='altered')),
    ('ending expected presence', 'ends', lambda rows: rows[0].update(expected='OK')),
    ('ending missing', 'ends', lambda rows: rows.pop()),
]:
    changed = copy.deepcopy(reference)
    mutation(changed[field])
    try:
        comparison.require_equal_results(reference, changed, assessor)
    except AssertionError:
        provider_negative.append(label)
    else:
        raise AssertionError(label)
changed = copy.deepcopy(reference)
changed['run_binding']['browser_build_id'] = 'different-build-identity'
comparison.require_equal_results(reference, changed, assessor)
print(json.dumps({'actual_original_and_combined_replay': True, 'provider_free_browser_executed': False,
                  'strict_row_end_signatures':594, 'provider_comparison_negative_checks':provider_negative}, indent=2))
