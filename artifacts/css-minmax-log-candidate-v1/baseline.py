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


def prepare(manifest):
    assert sha(HERE / 'FILES.json') == manifest
    policy = read(HERE / 'POLICY.json')
    ownership = load('activation_ownership', policy['ownership_helper'])
    ownership.authenticate(HERE, manifest)
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths']) == {'servo/components/style/values/generics/calc.rs'}
    for record in roles.values():
        for kind in ('base', 'candidate'):
            path = Path(record[kind + '_capture'])
            assert not path.is_absolute() and '..' not in path.parts and not (ROOT / path).is_symlink()
            assert policy['references'][str(path)] == sha(ROOT / path) == record[kind + '_sha256']
    ownership.authenticate(ROOT / policy['baseline_capsule']['directory'], policy['baseline_capsule']['sha256'])
    assert policy['wpt'] == expected_wpt(policy)
    wpt = policy['wpt']
    assert (wpt['expected_subtest_count'], wpt['expected_target_count'], wpt['expected_control_count'],
            wpt['expected_page_count'], wpt['expected_regression_signature_count']) == (578, 33, 545, 16, 561)
    binding = policy['baseline_binding']
    directory = ROOT / binding['directory']
    ownership.authenticate(directory, binding['manifest_sha256'])
    assert read(directory / binding['terminal_path']) == binding['terminal']
    assert binding['terminal']['exit'] == 0 and sha(directory / 'RESULT.json') == binding['result_sha256'] == binding['terminal']['result_sha256']
    assert sha(directory / 'OBSERVED-ROSTER.json') == binding['roster_sha256']
    assessor = load('minmax_assessor', str((HERE / 'assess.py').relative_to(ROOT)))
    checks = load('minmax_checks', wpt['checks_helper'])
    comparison = load('minmax_comparison', str((HERE / 'comparison.py').relative_to(ROOT)))
    comparison.replay_original(ROOT, policy, assessor, checks)
    return policy, ownership, roles


def guard(policy, ownership, roles):
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
    assert build_epoch['pow_special_value_transition']['source_sha256'] == roles['servo/components/style/values/generics/calc.rs']['base_sha256']
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
        assert build_epoch['pins'][name] == pending[name]['compiled_sha256'] == record['base_sha256']
    for name in ('servo/components/style/values/generics/calc.rs', 'servo/components/style/custom_properties.rs'):
        assert sha(ROOT / name) == epoch['pins'][name] == build_epoch['pins'][name]
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
    print('Authenticated min/max comparison inputs; no browser or build execution')


if __name__ == '__main__':
    main()
