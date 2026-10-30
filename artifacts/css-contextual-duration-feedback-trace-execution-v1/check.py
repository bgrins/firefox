import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def check():
    policy = read(HERE / 'RECIPE.json')
    assert policy['execution_enabled'] is False
    assert policy['native_acceptance'] is False
    assert policy['trace_is_numeric_or_convergence_oracle'] is False
    assert policy['logger'] is None
    assert policy['trace_original_terminal'] is None
    assert policy['trace_original_runtime_manifest'] is None
    assert policy['candidate_fresh_restored_state_binding'] is None
    assert len(policy['activation_pending']) == 5
    refs = read(HERE / 'REFERENCES.json')
    for name, pin in refs.items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        path = ROOT / relative
        assert path.is_file() and not path.is_symlink() and sha(path) == pin, name
    fixture = ROOT / policy['fixture']['directory']
    assert sha(fixture / 'FILES.json') == policy['fixture']['manifest_sha256']
    for name, pin in read(fixture / 'FILES.json').items():
        assert sha(fixture / name) == pin
    inputs = read(fixture / 'INPUTS.json')
    assert (inputs['expected_callbacks'], inputs['expected_endings']) == (2, 1)
    assert inputs['calibrated_acquisition_requires_all_pass']
    assert inputs['numeric_feedback_oracle'] is False
    assert sum(map(len, inputs['expected_subtests'].values())) == 2
    assert inputs['transport']['record_files'] == {'coupled': 'coupled.json', 'zero-start': 'zero-start.json'}
    roles = policy['roles']
    assert set(roles) == {'instrumented-original', 'instrumented-candidate'}
    original, candidate = roles['instrumented-original'], roles['instrumented-candidate']
    assert original['overlay_paths'] == ['dom/animation/EffectCompositor.cpp']
    assert candidate['overlay_paths'] == ['dom/animation/EffectCompositor.cpp', 'servo/components/style/matching.rs']
    assert original['required_counts'] == {'PASS': 2, 'FAIL': 0, 'OK': 1}
    assert original['require_calibrated_acquisition'] is True
    assert candidate['require_calibrated_acquisition'] is False
    assert candidate['known_failure_remains_owner_exit'] == 1
    assert candidate['historical_failure_counts'] == {'PASS': 0, 'FAIL': 2, 'OK': 1}
    assert original['built_revision'] == candidate['built_revision'] == policy['head']
    assert policy['restored_app']['revision'] != policy['head']
    for role in roles.values():
        assert sha(ROOT / role['matching_capture']) == role['matching_sha256']
    assert original['matching_sha256'] != candidate['matching_sha256']
    assert len(set(policy['runtime_outputs'].values())) == 2
    refresh = read(ROOT / 'artifacts/css-contextual-duration-index-refresh-v6/RESULT.json')
    assert policy['prepared_epoch_sha256'] == refresh['after_epoch']
    assert policy['prepared_raw_index'] == refresh['raw_index']['after']
    terminal = read(ROOT / policy['restored_app']['receipt'])
    assert terminal['state_and_application_restoration_independently_verified']
    assert terminal['exit'] == 1 and terminal['callbacks_failed'] == 2
    assert terminal['calibrated_acquisition'] is False
    return {'disabled': True, 'references_authenticated': len(refs), 'fixture_payloads_authenticated': len(read(fixture / 'FILES.json')), 'live_state_checked': False, 'owner_executed': False}


if __name__ == '__main__':
    assert sys.argv[1:] == ['--check']
    print(json.dumps(check(), sort_keys=True))
