import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def owner_terminal(directory, binding, capsule):
    terminal_path = directory / binding['terminal_path']
    assert sha(terminal_path) == binding['terminal_sha256']
    terminal = read(terminal_path)
    assert terminal == binding['terminal'] and terminal['exit'] == 0
    assert terminal['result_sha256'] == binding['result_sha256']
    assert sha(ROOT / capsule['directory'] / 'FILES.json') == capsule['sha256']
    return terminal


def current_capture(policy):
    binding = policy['current_binding']
    assert binding and sha(ROOT / binding['path']) == binding['sha256']
    return read(ROOT / binding['path'])


def prepare(manifest):
    assert sha(HERE / 'FILES.json') == manifest
    policy = read(HERE / 'POLICY.json')
    ownership = load('published_ownership', policy['ownership_helper'])
    ownership.authenticate(HERE, manifest)
    load('published_checks', str((HERE / 'check.py').relative_to(ROOT))).validate_policy(policy)
    return policy, ownership, read(HERE / 'SOURCE-ROLES.json')


def require_ready(policy):
    assert policy['execution_enabled'] and policy['candidate_execution_enabled']
    assert policy['activation_pending'] == []
    assert policy['current_binding'] is not None and policy['baseline_binding'] is not None and policy['execution_handoff'] is not None
    load('published_checks', str((HERE / 'check.py').relative_to(ROOT))).validate_policy(policy)


def metadata_guard(policy):
    for name, pin in policy['metadata_current_pins'].items():
        assert sha(ROOT / name) == pin


def require_role(policy, role, epoch):
    assert role['role'] == 'published-native' and role['variant'] == 'registered-image'
    assert role['built'] is False and role['paired_head'] == policy['image_commit']
    assert role['pending_gtest_overlay_installed'] is False
    assert 'last_build' not in role and 'last_install' not in role
    retirement = epoch['prototype_overlay_state']
    assert retirement['installed'] is False and retirement['held_provider_parked'] is True
    assert retirement['old_restoration_recipes_require_rebase'] is True
    path = 'artifacts/css-registered-color-image-publication-union-runtime-1/PRE-ROLE.json'
    assert retirement['original_role_preserved_in'] == path
    claims = read(ROOT / 'artifacts/css-registered-color-image-publication-union-runtime-1/INITIAL-CLAIMS.json')
    assert claims['controls']['ROLE.json']['owned_sha256'] == sha(ROOT / path)


def require_app_inventory(policy, app, extra):
    capture = current_capture(policy)
    assert digest(app) == capture['app_inventory_sha256']
    assert extra == capture['extras']


def environment():
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'MOZ_ARTIFACT_BUILDS', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_PROFILE', 'MOZ_DURATION_RESTYLE_TRACE'))
    return dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1', MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')


def observe(policy, ownership, roles, checkpoint):
    env = environment()
    state = load('published_state', policy['state_helper'])
    assert checkpoint['committed'] and checkpoint['signature_verified']
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    epoch, role = json.loads(controls['CURRENT-EPOCH.json']), json.loads(controls['ROLE.json'])
    assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == checkpoint['epoch_sha256']
    assert epoch['semantic_index']['head'] == checkpoint['head']
    assert epoch['staged_working'] == {} and epoch['modified_native_paths'] == []
    require_role(policy, role, epoch)
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['image_commit'], checkpoint['head'])
    metadata_guard(policy)
    for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    sources = {}
    for name, record in roles.items():
        assert record['base_sha256'] == epoch['pins'][name]
        sources[name] = ownership.claim(ROOT, name, record['base_sha256'], epoch['installed_identities'][name])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', checkpoint['head'] + ':' + name)).hexdigest() == record['base_sha256']
    for name, pin in policy['source_context_pins'].items():
        assert sha(ROOT / name) == pin
    ownership.quiescent(RUNTIME)
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists() and not (RUNTIME / 'SOURCE-TRANSITION.lock').is_symlink()
    flags = {name: state.h.git(path, env, 'ls-files', '-v', '-z') for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
    assert snapshot['index']['head'] == checkpoint['head']
    assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
    return state, env, controls, epoch, role, sources, flags, snapshot


def guard(policy, ownership, roles):
    require_ready(policy)
    capture = current_capture(policy)
    state, env, controls, epoch, role, sources, flags, snapshot = observe(policy, ownership, roles, capture['checkpoint'])
    assert {name: hashlib.sha256(body).hexdigest() for name, body in controls.items()} == policy['controls'] == capture['controls']
    assert state.h.git(ROOT, env, 'rev-parse', policy['head'] + '^').decode().strip() == policy['baseline_head']
    changed = state.h.git(ROOT, env, 'diff-tree', '--no-commit-id', '--name-only', '-r', policy['head']).decode().splitlines()
    assert sorted(changed) == policy['checkpoint_bridge']['committed_paths']
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['head'])
    assert snapshot == capture['snapshot'] and sources == capture['sources'] and role == capture['role']
    assert epoch['pins'] == capture['epoch_payload_pins']
    assert epoch['installed_identities'] == capture['installed_identities']
    for name, record in policy['accepted_current_payloads'].items():
        ownership.claim(ROOT, name, record['sha256'], record['identity'])
    assert {name: hashlib.sha256(body).hexdigest() for name, body in flags.items()} == capture['flag_hashes']
    metadata = load('published_metadata', policy['wpt']['metadata_helper'])
    assert metadata.application_metadata(ROOT / policy['wpt']['application_ini'], policy['restored_application_revision']) == capture['application_metadata']
    for name in policy['rebuilt_binaries']:
        assert sha(ROOT / name) == epoch['pins'][name] == capture['binaries'][name]
    def verify():
        metadata_guard(policy)
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
            assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
        value = state.a.verify_current(state.h, ROOT, env, epoch)
        for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
            assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
        return value
    return state, env, controls, epoch, flags, verify
