import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'artifacts/css-contextual-duration-restyle-tristate-browser-v1'
PAIR = ROOT / 'artifacts/css-contextual-duration-restyle-tristate-browser-runtime-1'
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


policy = read(HERE / 'POLICY.json')
owner = load('root_trace_owner', policy['ownership_helper'])
owner.authenticate(HERE, 'dad1eba06c18933608ac4e937ab3a6a71d191e23ef2fd1033118d4e05f134be1')
state = load('root_trace_state', policy['state_helper'])
bundle = load('root_trace_bundle', policy['bundle_helper'])
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert {name: sha(RUNTIME / name) for name in policy['controls']} == policy['controls']
assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
result = read(PAIR / 'CANDIDATE-RESULT.json')
assert result['success'] and result['restoration_verified'] and result['error'] is None
assert result['runtime_controls_unchanged'] and result['empty_staging_preserved']
assert result['publication_errors'] == [] and not result['native_fix_acceptance']
assert read(PAIR / 'RESTORATION.json')['errors'] == []
assert read(PAIR / 'RESTORATION.json')['owned_processes'] == {}
backup = read(PAIR / 'BACKUP-CLEANUP.json')
assert backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
assert not (PAIR / 'backups').exists()
build = read(PAIR / 'candidate-build/build-RESULT.json')
assert build['exit'] == 0 and build['owned_group_absent'] and build['cleanup_errors'] == []
assert build['error'] is None and build['stop_reason'] is None
phase = PAIR / 'feedback-wpt'
for receipt in (PAIR / 'candidate-build/build-PROCESS.json', phase / 'PROCESS.json'):
    owner.group_absent(read(receipt)['pgid'])
outcome = read(phase / 'RESULT.json')
assert outcome['success'] and outcome['exit'] == 0 and outcome['preservation_verified']
cleanup = read(phase / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
assessor = load('root_trace_assessor', str((HERE / 'assess.py').relative_to(ROOT)))
checks = load('root_trace_checks', policy['wpt']['checks_helper'])
events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
owner.authenticate(ROOT / policy['baseline_capsule']['directory'], policy['baseline_capsule']['sha256'])
owner.authenticate(ROOT / policy['baseline_binding']['directory'], policy['baseline_binding']['manifest_sha256'])
comparison = load('root_tristate_comparison', str((HERE / 'comparison.py').relative_to(ROOT)))
comparison.replay_all(ROOT, policy)
original_assessment = comparison.replay_original(ROOT, policy, assessor, checks)
assessment = assessor.assess(events, outcome['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, original=original_assessment, run_binding=read(phase / 'APPLICATION-METADATA.json'))
assert assessment == read(phase / 'ASSESSMENT.json')
assert assessment['complete'] and assessment['errors'] == []
assert assessment['comparison_gate_passed'] and assessment['comparison_errors'] == []
assert len(assessment['rows']) == 2 and all(r['status'] == 'PASS' for r in assessment['rows'])
assert len(assessment['ends']) == 1 and assessment['ends'][0]['status'] == 'OK'
assert read(phase / 'PRE.json') == read(phase / 'POST.json') == read(PAIR / 'PHASES-PRE.json') == read(PAIR / 'PHASES-POST.json')
assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
metadata = read(phase / 'APPLICATION-METADATA.json')
assert metadata['revision'] == metadata['build_revision'] == policy['head']
assert metadata['source_role'] == 'candidate'
compiled = read(PAIR / 'candidate-build/RESULT.json')
assert compiled['command_success'] and compiled['preservation_verified'] and compiled['error'] is None
assert compiled['native_sources'] == {name: record['candidate_sha256'] for name, record in read(HERE / 'SOURCE-ROLES.json').items()}
assert compiled['binaries'] == read(phase / 'BINARY-PINS.json')
assert compiled['snapshot'] == read(phase / 'PRE.json')
phases = load('root_trace_phases', str((HERE / 'phases.py').relative_to(ROOT)))
records = phases.feedback_records(ROOT, PAIR, policy)
assert records == read(PAIR / 'FEEDBACK-RECORDS.json') and records['calibrated_acquisition']
roles = read(HERE / 'SOURCE-ROLES.json')
for name, role in roles.items():
    record = read(PAIR / 'RESTORATION.json')['sources'][name]
    owner.claim(ROOT, name, role['base_sha256'], record['identity'])
for name, record in policy['accepted_current_payloads'].items():
    owner.claim(ROOT, name, record['sha256'], record['identity'])
for name, pin in policy['source_context_pins'].items():
    assert sha(ROOT / name) == pin
assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(PAIR / 'APP-PRE.json'))
assert bundle.semantic({name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}) == bundle.semantic(read(PAIR / 'EXTRA-PRE.json'))
for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest() == policy['prepared_flag_hashes'][name]
old_bytes = (RUNTIME / 'CURRENT-EPOCH.json').read_bytes()
old = json.loads(old_bytes)
observation = read(PAIR / 'RAW-INDEX-OBSERVATION.json')
assert observation['semantic_index_unchanged'] and not observation['canonical_updated']
assert observation['before'] == old['raw_index_observation']['current']
updated = copy.deepcopy(old)
updated['raw_index_observation']['current'] = observation['after']
snapshot = state.a.verify_current(state.h, ROOT, env, updated)
assert snapshot == read(PAIR / 'POST.json')
expected = copy.deepcopy(read(ROOT / policy['baseline_binding']['directory'] / 'POST.json'))
expected['index']['raw_index'] = observation['after']
assert snapshot == expected
app_entry = ROOT / policy['wpt']['application_ini']
terminal = {
    'session_id': 7257, 'terminal_chunk': '7a7e91', 'exit': 0,
    'owner_sha256': sha(HERE / 'FILES.json'), 'result_sha256': sha(PAIR / 'CANDIDATE-RESULT.json'),
    'build_success': True, 'callbacks_passed': 2, 'ending': 'OK', 'records': 2,
    'calibrated_acquisition': True, 'raw_replay_verified': True,
    'state_and_application_restoration_independently_verified': True,
    'raw_index_observation': observation, 'restored_application_entry': bundle.entry(app_entry),
    'restored_application_target': bundle.entry(app_entry.resolve()),
    'backup_removed_bytes': backup['owned_backup_bytes'], 'native_acceptance': False,
    'self_feedback_numeric_or_convergence_oracle': False,
}
save(PAIR / 'ROOT-TERMINAL.json', terminal)
symlinks = {str(p.relative_to(PAIR)): os.readlink(p) for p in PAIR.rglob('*') if p.is_symlink()}
save(PAIR / 'SYMLINKS.json', symlinks)
manifest = {str(p.relative_to(PAIR)): sha(p) for p in PAIR.rglob('*') if p.is_file() and not p.is_symlink()}
assert 'FILES.json' not in manifest
save(PAIR / 'FILES.json', manifest)
if observation['before'] != observation['after']:
    unchanged = copy.deepcopy(updated)
    unchanged['raw_index_observation']['current'] = observation['before']
    assert unchanged == old
    claim = owner.claim(ROOT, str((RUNTIME / 'CURRENT-EPOCH.json').relative_to(ROOT)), policy['controls']['CURRENT-EPOCH.json'])
    try:
        owner.write_owned(ROOT, claim, owner.encoded(updated))
        assert state.a.verify_current(state.h, ROOT, env, updated) == snapshot
        assert all(sha(RUNTIME / name) == policy['controls'][name] for name in ('OWNED.json', 'ROLE.json'))
    except BaseException:
        owner.write_owned(ROOT, claim, old_bytes)
        raise
refresh = {'before_epoch': policy['controls']['CURRENT-EPOCH.json'], 'after_epoch': sha(RUNTIME / 'CURRENT-EPOCH.json'), 'only_changed_field': 'raw_index_observation.current', 'observation': observation, 'runtime_manifest_sha256': sha(PAIR / 'FILES.json'), 'full_restored_state_verified': True, 'accepted_fix_increment': 0}
save(ROOT / 'artifacts/css-contextual-duration-restyle-tristate-root-refresh.json', refresh)
print(json.dumps({'terminal': terminal, 'refresh': refresh}, indent=2), flush=True)
