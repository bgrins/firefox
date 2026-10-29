import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


for source in HERE.glob('*.py'):
    ast.parse(source.read_text(), filename=str(source))
policy = json.loads((HERE / 'POLICY.json').read_bytes())
assert policy['install_enabled'] and policy['build_enabled']
bound = json.loads((HERE / 'ACTUAL-BINDING.json').read_bytes())
assert policy['head'] == bound['head']
assert policy['epoch_sha256'] == bound['controls']['CURRENT-EPOCH.json']
assert policy['role_sha256'] == bound['controls']['ROLE.json']
assert policy['owned_sha256'] == bound['controls']['OWNED.json']
owner = load('saved_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
evidence = load('saved_evidence', HERE / 'evidence.py')
saved = evidence.verify(ROOT, policy, None, owner, check_processes=False)
assessor = load('final_assessor', HERE / 'assess.py')
final = load('final_owner', HERE / 'final.py')
final.validate_settings(policy)
paired = ROOT / policy['paired_runtime'] / 'candidate-wpt'
phase_policy = json.loads((paired / 'ASSESSMENT-POLICY.json').read_bytes())
binding = json.loads((paired / 'APPLICATION-METADATA.json').read_bytes())
checks = load('saved_checks', ROOT / phase_policy['checks_helper'])
events = [json.loads(line) for line in (paired / 'raw.jsonl').read_text().splitlines()]
expected = set(policy['deleted_metadata']['expected_fail_subtests'])
changed = []
for event in events:
    if event.get('action') == 'test_status' and event.get('test') == '/dom/nodes/moveBefore/moveBefore-child-list-selector-invalidation.html' and event.get('subtest') in expected:
        assert event['status'] == 'PASS' and event.pop('expected') == 'FAIL'
        assert event.pop('known_intermittent') == []
        changed.append(event['subtest'])
assert set(changed) == expected and len(changed) == 7

def assess(items, code=0):
    return assessor.assess(items, code, phase_policy, checks, run_binding=binding)

positive = assess(events)
assert positive['comparison_gate_passed'] and positive['complete']
rejected = []
for variant in ('old_metadata', 'control_message', 'missing_row', 'failed_row', 'bad_ending', 'exit_one', 'wrong_expectation', 'extra_row'):
    items = copy.deepcopy(events)
    rows = [event for event in items if event.get('action') == 'test_status']
    code = 0
    if variant == 'old_metadata':
        items = [json.loads(line) for line in (paired / 'raw.jsonl').read_text().splitlines()]
        code = 1
    elif variant == 'control_message':
        next(row for row in rows if row['test'].endswith('animation-identity-restoration.html'))['message'] = 'changed'
    elif variant == 'missing_row':
        items.remove(rows[0])
    elif variant == 'failed_row':
        rows[0]['status'] = 'FAIL'
    elif variant == 'bad_ending':
        next(event for event in items if event.get('action') == 'test_end')['status'] = 'ERROR'
    elif variant == 'exit_one':
        code = 1
    elif variant == 'wrong_expectation':
        next(row for row in rows if row['subtest'] in expected)['expected'] = 'FAIL'
    else:
        extra = copy.deepcopy(rows[0])
        extra['subtest'] = 'not in roster'
        items.append(extra)
    assert not assess(items, code)['comparison_gate_passed'], variant
    rejected.append(variant)
print(json.dumps({'saved_pair_complete_replay': saved, 'final_projection_positive': 1,
                  'negative_controls_rejected': rejected, 'synthetic_final_only': True,
                  'live_guard_or_main_executed': False}))
