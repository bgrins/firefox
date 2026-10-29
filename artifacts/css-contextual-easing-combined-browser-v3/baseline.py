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


def prepare(manifest):
    assert sha(HERE / 'FILES.json') == manifest
    policy = read(HERE / 'POLICY.json')
    ownership = load('activation_ownership', policy['ownership_helper'])
    ownership.authenticate(HERE, manifest)
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    allowed = {}
    for package in [policy['candidate']] + policy['capture_packages']:
        directory = ROOT / package['directory']
        ownership.authenticate(directory, package['sha256'])
        for name, entry in read(directory / 'FILES.json').items():
            allowed[str(Path(package['directory']) / name)] = entry['sha256'] if isinstance(entry, dict) else entry
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert (HERE / 'SOURCE-ROLES.json').read_bytes() == (ROOT / policy['candidate']['directory'] / 'SOURCE-ROLES.json').read_bytes()
    for name, record in roles.items():
        assert name in policy['source_paths']
        for kind in ('base', 'candidate'):
            path = Path(record[kind + '_capture'])
            assert not path.is_absolute() and '..' not in path.parts and not (ROOT / path).is_symlink()
            assert allowed[str(path)] == sha(ROOT / path) == record[kind + '_sha256']
    assert set(roles) == set(policy['source_paths']) and len(roles) == 8
    assert set(roles) & set(policy['accepted_current_payloads']) == {'servo/components/style/values/specified/easing.rs'}
    assert 'servo/components/style/values/generics/calc.rs' not in roles and 'servo/components/style/custom_properties.rs' not in roles
    input_directory = ROOT / policy['input_plan']['directory']
    ownership.authenticate(input_directory, policy['input_plan']['sha256'])
    experiment = read(input_directory / 'EXPERIMENT.json')
    assert policy['wpt']['expected_subtests'] == experiment['expected_subtests']
    assert policy['wpt']['target_subtests'] == experiment['target_subtests']
    assert policy['wpt']['resources'] == read(input_directory / 'RESOURCES.json')
    assert policy['wpt']['metadata'] == read(input_directory / 'METADATA.json')
    assert roles == read(input_directory / 'SOURCE-ROLES.json')
    assert policy['wpt']['manifest']['path'] == str((input_directory / 'SUBSET-MANIFEST.json').relative_to(ROOT))
    assert policy['wpt']['expected_subtest_count'] == experiment['expected_subtest_count'] == 315
    assert policy['wpt']['expected_page_count'] == experiment['expected_page_count'] == 22
    assert policy['wpt']['expected_target_count'] == 41
    assert policy['wpt']['expected_control_count'] == 274
    assert policy['wpt']['expected_regression_signature_count'] == 296
    controls = {test: [name for name in names if name not in policy['wpt']['target_subtests'].get(test, [])]
                for test, names in policy['wpt']['expected_subtests'].items()}
    assert {test: names for test, names in controls.items() if names} == experiment['regression_subtests']
    return policy, ownership, roles


def guard(policy, ownership, roles):
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'MOZ_ARTIFACT_BUILDS', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_PROFILE'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1', MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    state = load('activation_state', policy['state_helper'])
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    assert {name: hashlib.sha256(body).hexdigest() for name, body in controls.items()} == policy['controls']
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
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', build_epoch['semantic_index']['head'] + ':' + name)).hexdigest() == record['base_sha256']
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
    assert len(sys.argv) == 3 and sys.argv[1] in ('--check', '--guard', '--run')
    policy, ownership, roles = prepare(sys.argv[2])
    assert policy['wpt'] is not None, 'Exact reviewed WPT roster remains pending'
    if sys.argv[1] == '--check':
        print('Authenticated activation captures and fixed baseline recipe; no live guard')
        return
    if sys.argv[1] == '--guard':
        state, env, controls, epoch, flags, verify = guard(policy, ownership, roles)
        verify()
        print('Live baseline bindings verified; no browser, build, or state mutation')
        return
    assert policy['execution_enabled']
    state, env, controls, epoch, flags, verify = guard(policy, ownership, roles)
    before = verify()
    output = ROOT / policy['runtime_output']
    assert output.parent == ROOT / 'artifacts' and not output.exists() and not output.is_symlink()
    output.mkdir()
    state.save(output / 'BASELINE-PRE.json', {'snapshot': before, 'controls': policy['controls'], 'source_roles': roles, 'browser_build_performed': False, 'original_build': policy['original_build']})
    stopped = [False]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    runner = load('activation_wpt', str((HERE / 'wpt.py').relative_to(ROOT)))
    owned = {}
    result = runner.run(ROOT, HERE, output / 'original-wpt', 'original', policy, env, verify, owned, lambda: stopped[0])
    assert not owned and verify() == before
    state.save(output / 'BASELINE-RESULT.json', {'success': True, 'preservation_verified': True, 'browser_build_performed': False, 'phase': result, 'canonical_updated': False})
    print('Current linked-app baseline complete; source/application preserved', flush=True)


if __name__ == '__main__':
    main()
