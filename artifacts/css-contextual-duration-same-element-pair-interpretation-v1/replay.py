import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / 'artifacts/css-contextual-duration-same-element-candidate-v2'
CANDIDATE = ROOT / 'artifacts/css-contextual-duration-same-element-candidate-runtime-1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha(OWNER / 'FILES.json') == '09b4e7abcf358c687cc2872c3c9b5cd273e9d48498f0ba44f22ced9fe05ea9a7'
for name, pin in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == pin
policy = read(OWNER / 'POLICY.json')
assert sha(CANDIDATE / 'FILES.json') == '0e2168c3cf3a34e51c6a2437133d31c9bd5c2e3fc7b4971b09b5cfbf1895b7b2'
for name, pin in read(CANDIDATE / 'FILES.json').items():
    assert sha(CANDIDATE / name) == pin
terminal = read(CANDIDATE / 'ROOT-TERMINAL.json')
assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (45913, 'd24784', 0)
assert terminal['owner_sha256'] == sha(OWNER / 'FILES.json')
assert terminal['result_sha256'] == sha(CANDIDATE / 'CANDIDATE-RESULT.json')
assert terminal['state_and_application_restoration_independently_verified']
assert terminal['backup_removed_bytes'] == 1008605176 and not terminal['native_acceptance']
refresh_path = ROOT / 'artifacts/css-contextual-duration-same-element-root-refresh.json'
assert sha(refresh_path) == '5db08d8dfbee2a1de7d0f73bb459c7f51c0b5e0be69a41b353da42f34337b813'
refresh = read(refresh_path)
assert refresh['runtime_manifest_sha256'] == sha(CANDIDATE / 'FILES.json')
assert refresh['observation'] == terminal['raw_index_observation']
assert refresh['only_changed_field'] == 'raw_index_observation.current'
assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
comparison = load('pair_comparison', OWNER / 'comparison.py')
original = comparison.replay_all(ROOT, policy)
assessor = load('pair_assessor', OWNER / 'assess.py')
checks = load('pair_checks', ROOT / policy['wpt']['checks_helper'])
phase = CANDIDATE / 'candidate-wpt'
result = read(CANDIDATE / 'CANDIDATE-RESULT.json')
assert result['success'] and result['error'] is None and result['publication_errors'] == []
assert not result['native_fix_acceptance']
for name, field in [('ASSESSMENT.json', 'assessment_sha256'), ('raw.jsonl', 'raw_sha256'), ('RESULT.json', 'result_sha256')]:
    assert sha(phase / name) == result['candidate_phase'][field]
settings = comparison.phase_policy(policy['wpt'])
assert settings == read(phase / 'ASSESSMENT-POLICY.json')
metadata = read(phase / 'APPLICATION-METADATA.json')
assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
inner = read(phase / 'RESULT.json')
events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
candidate = assessor.assess(events, inner['exit'], settings, checks, original=original, run_binding=metadata)
assert candidate == read(phase / 'ASSESSMENT.json') and candidate['comparison_gate_passed']
assert [row['status'] for row in original['rows']] == ['FAIL', 'PASS']
assert [row['status'] for row in candidate['rows']] == ['PASS', 'PASS']
assert [row['status'] for row in candidate['ends']] == ['OK']
build = read(CANDIDATE / 'candidate-build/RESULT.json')
roles = read(OWNER / 'SOURCE-ROLES.json')
assert build['command_success'] and build['preservation_verified'] and build['error'] is None
assert build['native_sources'] == {name: role['candidate_sha256'] for name, role in roles.items()}
assert build['binaries'] == read(phase / 'BINARY-PINS.json')
collection = load('pair_records', OWNER / 'records.py').collect(ROOT, CANDIDATE / 'progress-records', read(CANDIDATE / 'PROGRESS-BINDING.json'), policy, candidate)
assert collection == read(CANDIDATE / 'PROGRESS-RECORDS.json')
assert collection['complete'] and not collection['errors'] and not collection['missing']
baseline = ROOT / policy['baseline_binding']['directory']
pairs = {}
for filename in policy['record_kinds']:
    pairs[filename] = {role: read(directory / 'progress-records' / filename)['observations'] for role, directory in [('original', baseline), ('candidate', CANDIDATE)]}
acyclic = pairs['same-element-acyclic.json']
feedback = pairs['same-element-feedback.json']
assert [row['value'] for row in acyclic['original']['contextual']['samples']] == [0.75] * 4
assert [row['value'] for row in acyclic['candidate']['contextual']['samples']] == [0.545455] * 4
assert [row['value'] for row in feedback['original']['contextual']['samples']] == [32] * 4
assert [row['value'] for row in feedback['candidate']['contextual']['samples']] == [16] * 4
for role in ('original', 'candidate'):
    assert acyclic[role]['literal']['samples'] == acyclic['candidate']['literal']['samples']
    for name in ('literal500', 'literal1000'):
        assert feedback[role][name] == feedback['candidate'][name]
print(json.dumps({'actual_candidate': {'session': 45913, 'launch': '54b831', 'terminal': 'd24784', 'exit': 0},
                  'saved_raw_replay_exact': True, 'saved_build_and_record_joins_exact': True,
                  'original_statuses': ['FAIL', 'PASS'], 'candidate_statuses': ['PASS', 'PASS'],
                  'page_endings': ['OK'], 'pairs': pairs,
                  'native_acceptance': False, 'fresh_state_verification_performed': False}, indent=2))
