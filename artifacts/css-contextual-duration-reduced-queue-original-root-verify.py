import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'artifacts/css-contextual-duration-reduced-queue-original-v1'
PAIR = ROOT / 'artifacts/css-contextual-duration-reduced-queue-original-runtime-1'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


owner = load('reduced_owner', 'artifacts/css-registered-number-source-transition-v4/transition.py')
owner.authenticate(HERE, 'c2a7774f9514d60e2c054683eb9261406ca5b68d8738a2d7b9beb8a9290f0b77')
policy = read(HERE / 'POLICY.json')
assert all(sha(ROOT / name) == pin for name, pin in policy['references'].items())
assert {name: sha(RUNTIME / name) for name in policy['controls']} == policy['controls']
assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
phase = PAIR / 'original-wpt'
outcome = read(phase / 'RESULT.json')
assert outcome['success'] and outcome['exit'] == 0 and outcome['execution_error'] is None
assert outcome['preservation_verified'] and not outcome['native_fix_acceptance']
cleanup = read(phase / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
owner.group_absent(read(phase / 'PROCESS.json')['pgid'])
checks = load('reduced_checks', policy['wpt']['checks_helper'])
assessor = load('reduced_assessor', str((HERE / 'assess.py').relative_to(ROOT)))
events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
metadata = read(phase / 'APPLICATION-METADATA.json')
assessment = assessor.assess(events, outcome['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, run_binding=metadata)
assert assessment == read(phase / 'ASSESSMENT.json')
assert assessment['complete'] and assessment['errors'] == []
assert len(assessment['rows']) == 2 and all(row['status'] == 'PASS' for row in assessment['rows'])
assert len(assessment['ends']) == 1 and assessment['ends'][0]['status'] == 'OK'
assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == policy['prepared_application_metadata']
assert read(phase / 'PRE.json') == read(phase / 'POST.json')
result = read(PAIR / 'RESULT.json')
assert result['preservation_verified'] and not result['source_or_canonical_mutation'] and not result['native_fix_accepted']
assert result['phase'] == {key: sha(phase / name) for key, name in [('assessment_sha256', 'ASSESSMENT.json'), ('raw_sha256', 'raw.jsonl'), ('result_sha256', 'RESULT.json')]}
roster = read(PAIR / 'OBSERVED-ROSTER.json')
assert roster['phase'] == result['phase'] and roster['owner_sha256'] == sha(HERE / 'FILES.json')
assert roster['observed_subtest_count'] == 2 and roster['expected_subtests'] == policy['wpt']['expected_subtests']
assert all(sha(ROOT / name) == pin for name, pin in policy['source_role_pins'].items())
state = load('reduced_state', policy['state_helper'])
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
assert not any(os.environ.get(key) for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
epoch = read(RUNTIME / 'CURRENT-EPOCH.json')
snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
assert snapshot == read(phase / 'POST.json')
for name, pin in read(phase / 'BINARY-PINS.json').items():
    assert sha(ROOT / name) == epoch['pins'][name] == pin
prior = ROOT / 'artifacts/css-contextual-duration-restyle-tristate-browser-runtime-1'
prior_policy = read(ROOT / 'artifacts/css-contextual-duration-restyle-tristate-browser-v1/POLICY.json')
bundle = load('reduced_bundle', prior_policy['bundle_helper'])
assert bundle.semantic(bundle.scan(ROOT / prior_policy['bundle_path'])) == bundle.semantic(read(prior / 'APP-PRE.json'))
assert bundle.semantic({name: bundle.entry(ROOT / name) for name in prior_policy['extra_backup_paths']}) == bundle.semantic(read(prior / 'EXTRA-PRE.json'))
for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest() == prior_policy['prepared_flag_hashes'][name]
terminal = {'session_id': 68662, 'terminal_chunk': '634d07', 'exit': 0,
            'owner_sha256': sha(HERE / 'FILES.json'), 'result_sha256': sha(PAIR / 'RESULT.json'),
            'callbacks_passed': 2, 'ending': 'OK', 'fixed_controls_passed': True,
            'raw_replay_verified': True, 'state_and_application_preservation_independently_verified': True,
            'epoch_sha256': sha(RUNTIME / 'CURRENT-EPOCH.json'),
            'raw_index': snapshot['index']['raw_index'], 'native_acceptance': False,
            'matching_only_or_combined_reduced_validation_performed': False}
save(PAIR / 'ROOT-TERMINAL.json', terminal)
save(PAIR / 'SYMLINKS.json', {str(path.relative_to(PAIR)): os.readlink(path) for path in PAIR.rglob('*') if path.is_symlink()})
manifest = {str(path.relative_to(PAIR)): sha(path) for path in PAIR.rglob('*') if path.is_file() and not path.is_symlink()}
assert 'FILES.json' not in manifest
save(PAIR / 'FILES.json', manifest)
print(json.dumps({'terminal': terminal, 'runtime_manifest_sha256': sha(PAIR / 'FILES.json')}, indent=2), flush=True)
