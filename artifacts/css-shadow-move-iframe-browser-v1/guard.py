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
    for name, record in policy['accepted_current_payloads'].items():
        ownership.claim(ROOT, name, record['sha256'], record['identity'])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', policy['head'] + ':' + name)).hexdigest() == record['sha256']
    build_epoch = read(ROOT / policy['original_build']['epoch'])
    build_result = read(ROOT / policy['original_build']['result'])
    inner = read(ROOT / policy['original_build']['inner_result'])
    assert build_result['command_success'] and build_result['preservation_verified'] and build_result['error'] is None and build_result['publication_errors'] == [] and build_result['owned_processes'] == {}
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == [] and inner['error'] is None and inner['stop_reason'] is None
    assert build_epoch['semantic_index']['head'] == policy['wpt']['phase_revisions']['original']
    assert policy['wpt']['phase_revisions']['candidate'] == policy['head']
    changed = set(state.h.git(ROOT, env, 'diff', '--no-renames', '--name-only', build_epoch['semantic_index']['head'], policy['head']).decode().splitlines())
    assert {name for name in changed if not name.startswith('artifacts/')} == set(policy['original_build']['later_committed_payloads'])
    for name, pin in policy['original_build']['later_committed_payloads'].items():
        assert epoch['pins'][name] == build_epoch['pins'][name] == pin
        if pin is None:
            assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
            assert name not in epoch['installed_identities']
        else:
            assert sha(ROOT / name) == pin
    recorded_metadata = read(ROOT / policy['original_build']['application_metadata'])
    assert sha(ROOT / policy['wpt']['application_ini']) == recorded_metadata['sha256']
    assert recorded_metadata['revision'] == policy['wpt']['phase_revisions']['original']
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
    for marker, expected in policy['preserved_markers'].items():
        assert epoch[marker] == expected
    metadata = load('shadow_metadata', policy['wpt']['metadata_helper'])
    restored_metadata = policy['application_metadata']
    assert {k:v for k,v in recorded_metadata.items() if k not in ('identity', 'entry_identity')} == {k:v for k,v in restored_metadata.items() if k not in ('identity', 'entry_identity')}
    assert metadata.application_metadata(ROOT / policy['wpt']['application_ini'], recorded_metadata['revision']) == restored_metadata
    deletion = policy['deleted_metadata']
    assert epoch['pins'][deletion] is None and deletion not in epoch['installed_identities']
    owned_data = json.loads(controls['OWNED.json'])
    assert deletion not in owned_data
    flags = {name: state.h.git(path, env, 'ls-files', '-v', '-z') for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    def verify():
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        assert not (ROOT / deletion).exists() and not (ROOT / deletion).is_symlink()
        assert metadata.application_metadata(ROOT / policy['wpt']['application_ini'], recorded_metadata['revision']) == restored_metadata
        for name, record in policy['accepted_current_payloads'].items():
            ownership.claim(ROOT, name, record['sha256'], record['identity'])
        current = state.a.verify_current(state.h, ROOT, env, epoch)
        for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
            assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
        return current
    return state, env, controls, epoch, flags, verify

