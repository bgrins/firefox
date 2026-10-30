import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_wpt(policy):
    comparison = load('minmax_roster_binding', str((HERE / 'comparison.py').relative_to(ROOT)))
    return comparison.expected_wpt(ROOT, policy)


def restoration_binding(policy, ownership):
    binding = policy['current_restoration_binding']
    assert set(binding) == {'terminal', 'refresh'}
    for record in binding.values():
        assert policy['references'][record['path']] == record['sha256'] == sha(ROOT / record['path'])
    provenance = policy['restoration_provenance']
    directory = ROOT / provenance['directory']
    owner = ROOT / provenance['owner_directory']
    ownership.authenticate(directory, provenance['manifest_sha256'])
    ownership.authenticate(owner, provenance['owner_sha256'])
    previous = read(owner / 'POLICY.json')
    terminal = read(ROOT / binding['terminal']['path'])
    refresh = read(ROOT / binding['refresh']['path'])
    assert terminal == read(directory / 'ROOT-TERMINAL.json')
    assert terminal['owner_sha256'] == provenance['owner_sha256']
    assert terminal['exit'] == 0 and terminal['state_and_application_restoration_independently_verified']
    assert terminal['raw_replay_verified'] and terminal['build_success'] and not terminal['native_acceptance']
    assert terminal['result_sha256'] == provenance['result_sha256'] == sha(directory / 'CANDIDATE-RESULT.json')
    result = read(directory / 'CANDIDATE-RESULT.json')
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['empty_staging_preserved'] and result['error'] is None and result['publication_errors'] == []
    restored = read(directory / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    cleanup = read(directory / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert cleanup['owned_backup_bytes'] == terminal['backup_removed_bytes']
    assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
    assert refresh['runtime_manifest_sha256'] == provenance['manifest_sha256']
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    assert refresh['observation'] == terminal['raw_index_observation'] == read(directory / 'RAW-INDEX-OBSERVATION.json')
    assert refresh['observation']['semantic_index_unchanged'] and not refresh['observation']['canonical_updated']
    assert refresh['before_epoch'] == previous['controls']['CURRENT-EPOCH.json']
    assert policy['controls'] == dict(previous['controls'], **{'CURRENT-EPOCH.json': refresh['after_epoch']})
    assert policy['head'] == previous['head'] == policy['wpt']['harness_revision']
    assert policy['prepared_flag_hashes'] == previous['prepared_flag_hashes']
    metadata = dict(previous['prepared_application_metadata'])
    entry, target = terminal['restored_application_entry'], terminal['restored_application_target']
    assert entry['kind'] == 'symlink' and target['kind'] == 'file' and target['nlink'] == 1
    assert entry['target'] == metadata['symlink_target'] == metadata['resolved']
    assert target['sha256'] == metadata['sha256']
    metadata.update(entry_identity=entry['identity'], identity=target['identity'])
    assert policy['prepared_application_metadata'] == metadata
    expected_processes = previous['closed_process_receipts'] + [
        str((directory / name).relative_to(ROOT)) for name in read(directory / 'FILES.json') if name.endswith('PROCESS.json')]
    assert policy['closed_process_receipts'] == expected_processes


def prepare(manifest):
    assert sha(HERE / 'FILES.json') == manifest
    policy = read(HERE / 'POLICY.json')
    ownership = load('activation_ownership', policy['ownership_helper'])
    ownership.authenticate(HERE, manifest)
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    assert policy['source_context_pins']['dom/animation/EffectCompositor.cpp'] == '6ec3a0ca45789b3089e8d2abcfb3ff37b881b0ee9084e09d0d396d73491249ed'
    assert policy['source_context_pins']['dom/animation/EffectCompositor.h'] == '5ee054432f5105515def6f1eba9e2875226d6a59b6a0dc4d1e05b9617a12dc19'
    if not policy['execution_enabled']:
        assert policy['activation_pending'] and not policy['candidate_execution_enabled']
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths']) == {'servo/components/style/matching.rs'}
    for record in roles.values():
        for kind in ('base', 'candidate'):
            path = Path(record[kind + '_capture'])
            assert not path.is_absolute() and '..' not in path.parts and not (ROOT / path).is_symlink()
            assert policy['references'][str(path)] == sha(ROOT / path) == record[kind + '_sha256']
    ownership.authenticate(ROOT / policy['baseline_capsule']['directory'], policy['baseline_capsule']['sha256'])
    assert policy['wpt'] == expected_wpt(policy)
    wpt = policy['wpt']
    assert (wpt['expected_subtest_count'], wpt['expected_target_count'], wpt['expected_control_count'],
            wpt['expected_page_count'], wpt['expected_regression_signature_count']) == (2, 0, 2, 1, 3)
    binding = policy['baseline_binding']
    directory = ROOT / binding['directory']
    ownership.authenticate(directory, binding['manifest_sha256'])
    assert read(directory / binding['terminal_path']) == binding['terminal']
    assert binding['terminal']['exit'] == 0 and sha(directory / 'RESULT.json') == binding['result_sha256']
    assert sha(directory / 'OBSERVED-ROSTER.json') == binding['roster_sha256']
    assessor = load('minmax_assessor', str((HERE / 'assess.py').relative_to(ROOT)))
    checks = load('minmax_checks', wpt['checks_helper'])
    comparison = load('minmax_comparison', str((HERE / 'comparison.py').relative_to(ROOT)))
    comparison.replay_original(ROOT, policy, assessor, checks)
    restoration_binding(policy, ownership)
    return policy, ownership, roles


def guard(policy, ownership, roles):
    assert policy['activation_pending'] == []
    restoration_binding(policy, ownership)
    assert policy['head'] == policy['wpt']['harness_revision']
    assert policy['prepared_application_metadata'] and policy['prepared_flag_hashes'] and policy['closed_process_receipts']
    for name, pin in policy['deferred_nonartifact_references'].items():
        assert sha(ROOT / name) == pin, name
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'MOZ_ARTIFACT_BUILDS', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_PROFILE'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1', MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    state = load('activation_state', policy['state_helper'])
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    assert {name: hashlib.sha256(body).hexdigest() for name, body in controls.items()} == policy['controls']
    checkpoint = read(ROOT / policy['reference_checkpoint']['path'])
    assert sha(ROOT / policy['reference_checkpoint']['path']) == policy['reference_checkpoint']['sha256']
    assert checkpoint['head'] == policy['head'] and checkpoint['signature_chain_verified'] and checkpoint['runtime_epoch_synchronized']
    assert checkpoint['accepted_fix'] == 150 and checkpoint['accepted_fixes'] == 149 and checkpoint['tracked'] == 150
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
    assert epoch['modified_native_paths'] == ['servo/components/style/custom_properties.rs']
    assert epoch['accepted_round_context_quotient'] == policy['accepted_round_context_quotient']
    assert epoch['round_context_quotient_transition'] == policy['round_context_quotient_transition']
    assert epoch['accepted_round_special_knowledge'] == policy['accepted_round_special_knowledge']
    for name, record in policy['accepted_epoch_records'].items():
        assert epoch[name] == record
    for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    for name, record in policy['accepted_current_payloads'].items():
        ownership.claim(ROOT, name, record['sha256'], record['identity'])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', policy['head'] + ':' + name)).hexdigest() == record['sha256']
    build_epoch = read(ROOT / policy['original_build']['epoch'])
    build_result = read(ROOT / policy['original_build']['result'])
    inner = read(ROOT / policy['original_build']['inner_result'])
    assert build_result['command_success'] and build_result['preservation_verified'] and build_result['error'] is None
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == [] and inner['error'] is None and inner['stop_reason'] is None
    assert build_epoch['semantic_index']['head'] == policy['wpt']['phase_revisions']['original']
    assert policy['wpt']['phase_revisions']['candidate'] == policy['head']
    changed = set(state.h.git(ROOT, env, 'diff', '--no-renames', '--name-only', build_epoch['semantic_index']['head'], policy['head']).decode().splitlines())
    assert {name for name in changed if not name.startswith('artifacts/')} == set(policy['original_build']['later_committed_payloads']) | set(policy['original_build']['later_removed_payloads'])
    for name, pin in policy['original_build']['later_committed_payloads'].items():
        assert sha(ROOT / name) == epoch['pins'][name] == build_epoch['pins'][name] == pin
    owned = json.loads(controls['OWNED.json'])
    for name in policy['preserved_absent_metadata']:
        assert epoch['pins'][name] is None and build_epoch['pins'][name] is None
        assert name not in epoch['installed_identities'] and name not in owned
    pending = policy['original_build']['pending_at_build']
    accepted = epoch['accepted_pow_special_value']
    assert accepted == policy['accepted_epoch_records']['accepted_pow_special_value']
    assert accepted['native_commit'] == policy['original_build']['accepted_native_commit']
    assert set(pending) == set(accepted['files']) == set(policy['original_build']['later_committed_payloads'])
    assert len(pending) == 2 and epoch['pow_special_value_transition']['accepted']
    native_paths = set(state.h.git(ROOT, env, 'diff-tree', '--no-commit-id', '--name-only', '-r', accepted['native_commit']).decode().splitlines())
    assert native_paths == set(pending) | set(policy['original_build']['later_removed_payloads'])
    for name, record in pending.items():
        assert record['compiled_sha256'] == accepted['files'][name] == build_epoch['pins'][name] == epoch['pins'][name]
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', accepted['native_commit'] + ':' + name)).hexdigest() == record['compiled_sha256']
        if record['head_preimage_sha256'] is None:
            assert not state.h.git(ROOT, env, 'ls-tree', build_epoch['semantic_index']['head'], '--', name)
        else:
            assert hashlib.sha256(state.h.git(ROOT, env, 'show', build_epoch['semantic_index']['head'] + ':' + name)).hexdigest() == record['head_preimage_sha256']
    assert build_epoch['pow_special_value_transition']['compiled'] and not build_epoch['pow_special_value_transition']['accepted']
    assert build_epoch['pow_special_value_transition']['source_sha256'] == policy['accepted_calc_sha256']
    for name, preimage in policy['original_build']['later_removed_payloads'].items():
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', build_epoch['semantic_index']['head'] + ':' + name)).hexdigest() == preimage
        assert not state.h.git(ROOT, env, 'ls-tree', policy['head'], '--', name)
    recorded_metadata = read(ROOT / policy['original_build']['application_metadata'])
    assert sha(ROOT / policy['wpt']['application_ini']) == recorded_metadata['sha256']
    assert recorded_metadata['revision'] == policy['wpt']['phase_revisions']['original']
    metadata_helper = load('combined_metadata', policy['wpt']['metadata_helper'])
    assert metadata_helper.application_metadata(ROOT / policy['wpt']['application_ini'],
        policy['wpt']['phase_revisions']['original']) == policy['prepared_application_metadata']
    for name in policy['rebuilt_binaries']:
        assert sha(ROOT / name) == epoch['pins'][name] == build_epoch['pins'][name]
    for name, record in roles.items():
        assert sha(ROOT / name) == record['base_sha256']
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', policy['head'] + ':' + name)).hexdigest() == record['base_sha256']
        assert build_epoch['pins'][name] == epoch['pins'][name] == record['base_sha256']
    for name in ('servo/components/style/values/generics/calc.rs', 'servo/components/style/custom_properties.rs'):
        assert sha(ROOT / name) == epoch['pins'][name] == build_epoch['pins'][name]
    for name, pin in policy['source_context_pins'].items():
        assert sha(ROOT / name) == pin
        if name in build_epoch['pins']:
            assert epoch['pins'][name] == build_epoch['pins'][name] == pin
        else:
            assert name in policy['build_unpinned_sources'] and name not in build_epoch['modified_native_paths']
            for revision in (policy['head'], policy['wpt']['phase_revisions']['original']):
                assert hashlib.sha256(state.h.git(ROOT, env, 'show', revision + ':' + name)).hexdigest() == pin
    for name in policy['closed_process_receipts']:
        ownership.group_absent(read(ROOT / name)['pgid'])
    ownership.quiescent(RUNTIME)
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    flags = {name: state.h.git(path, env, 'ls-files', '-v', '-z') for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    assert {name: hashlib.sha256(body).hexdigest() for name, body in flags.items()} == policy['prepared_flag_hashes']
    def verify():
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
            assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
        current = state.a.verify_current(state.h, ROOT, env, epoch)
        for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
            assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
        return current
    return state, env, controls, epoch, flags, verify


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('--check', '--guard')
    policy, ownership, roles = prepare(sys.argv[2])
    if sys.argv[1] == '--guard':
        state, env, controls, epoch, flags, verify = guard(policy, ownership, roles)
        verify()
    print('Authenticated contextual-duration comparison inputs; no browser or build execution')


if __name__ == '__main__':
    main()
