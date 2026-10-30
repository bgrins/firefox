import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r = load('saved_review', HERE / 'review.py')
observation = load('saved_observation', HERE / 'observations.py')
config, owner = r.authenticate()
assert not config['execution_enabled'] and config['actual_terminal'] is None
policy = r.read(owner / 'POLICY.json')
pair = ROOT / config['runtime_directory']
result = r.read(pair / 'CANDIDATE-RESULT.json')
pre = r.read(pair / 'CANDIDATE-PRE.json')
build = r.read(pair / 'candidate-build/build-RESULT.json')
inputs = {}


def record(name):
    inputs[name] = r.sha(pair / name)
    return r.read(pair / name)


def replay(reader=record):
    return observation.review(
        ROOT, HERE, pair, policy, pre, result, build, reader, inputs,
        SimpleNamespace(group_absent=lambda pgid: None), r.validate_build_phase)


value = replay()
assert value['observation_complete']
assert value['raw_counts'] == {'PASS': 56, 'FAIL': 18}
assert len(value['raw_endings']) == 11
assert value['repair_observation_gate'] is False
assert sum(len(b['candidate_signatures']) for b in value['behaviors'].values()) == 85
assert sum(len(b['target_rows']) for b in value['behaviors'].values()) == 15
assert all(row['status'] == 'PASS' for b in value['behaviors'].values() for row in b['target_rows'])
assert all(b['differences'] for b in value['behaviors'].values())
mutations = []


def altered_record(name):
    value = record(name)
    if name == 'candidate-wpt-ordinary/BEHAVIOR-COMPARISON.json':
        value['differences'][0]['identity'][2] += ' changed'
        mutations.append(name)
    return value


altered = replay(altered_record)
assert mutations == ['candidate-wpt-ordinary/BEHAVIOR-COMPARISON.json']
assert not altered['observation_complete']
assert altered['raw_counts'] == {'PASS': 56, 'FAIL': 18}
assert altered['lanes']['ordinary']['errors']
assert altered['lanes']['forced_colors']['observation_complete']
assert altered['lanes']['mozilla_appearance']['observation_complete']
for name, digest in inputs.items():
    assert r.sha(pair / name) == digest
print(json.dumps({'real_lanes_with_nonempty_differences': 3,
                 'raw_counts': value['raw_counts'], 'signatures': 85,
                 'passing_targets': 15, 'repair_gate': False,
                 'altered_identity_rejected': True,
                 'evidence_unchanged': True,
                 'process_absence_mocked': True,
                 'live_restoration_verifier_run': False}))
