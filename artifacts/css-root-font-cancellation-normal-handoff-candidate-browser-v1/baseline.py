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


def require_ready(policy, ownership, manifest):
    assert policy['execution_enabled'] and policy['candidate_execution_enabled']
    assert policy['activation_pending'] == []
    assert policy['current_binding'] is not None
    assert sha(HERE / 'FILES.json') == manifest
    ownership.authenticate(HERE, manifest)
    assert read(HERE / 'POLICY.json') == policy
    closure = load('ready_consumed_closure', str((HERE / 'closure.py').relative_to(ROOT)))
    external = closure.external_inputs(ROOT, policy, read(HERE / 'SOURCE-ROLES.json'))
    assert external == policy['intermediate_consumed_inputs']
    for name, pin in external.items():
        path = ROOT / name
        if pin is None:
            assert not path.exists() and not path.is_symlink()
        else:
            assert sha(path) == pin


def metadata_guard(policy):
    for name, pin in policy['metadata_current_pins'].items():
        assert sha(ROOT / name) == pin


def require_role(policy, role, epoch):
    adapter = load('language_capture_role', policy['capture_owner']['directory'] + '/baseline.py')
    assert adapter.binding['ownership_commit'] == policy['ownership_commit']
    assert adapter.binding['capacity_commit'] == policy['capacity_commit']
    adapter.require_role(policy, role, epoch)


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
    adapter = load('native_capture_authority', policy['capture_owner']['directory'] + '/baseline.py')
    native_receipt = checkpoint
    admission = load('live_direct_admission', str((HERE / 'admission.py').relative_to(ROOT)))
    evidence = admission.direct_evidence(ROOT, policy, native_receipt)
    native_head = native_receipt['commit']
    expected_epoch_sha256 = evidence['current_epoch_sha256']
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    epoch, role = json.loads(controls['CURRENT-EPOCH.json']), json.loads(controls['ROLE.json'])
    assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == expected_epoch_sha256
    assert epoch['semantic_index']['head'] == native_head
    assert epoch['staged_working'] == {} and epoch['modified_native_paths'] == []
    require_role(policy, role, epoch)
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['image_commit'], native_head)
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['nowrap_commit'], native_head)
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['language_commit'], native_head)
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['nowrap_commit'])
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['language_commit'])
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['ownership_commit'], native_head)
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['ownership_commit'])
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['capacity_commit'], native_head)
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['capacity_commit'])
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', adapter.binding['native_parent'])
    assert state.h.git(ROOT, env, 'rev-parse', native_head + '^').decode().strip() == adapter.binding['native_parent']
    assert state.h.git(ROOT, env, 'diff-tree', '--no-commit-id', '--name-only', '-r', native_head).decode().splitlines() == native_receipt['files']
    metadata_guard(policy)
    for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    sources = {}
    additional = current_capture(policy)['additional_sources']
    assert set(additional) == set(policy['additional_source_paths'])
    for name, record in roles.items():
        if name in additional:
            assert name not in epoch['installed_identities']
            assert name not in epoch['pins'] or epoch['pins'][name] == record['base_sha256']
            claim = additional[name]
            assert claim['path'] == name and claim['owned_sha256'] == record['base_sha256']
            sources[name] = ownership.claim(ROOT, name, record['base_sha256'], claim['identity'])
            assert sources[name] == claim
        else:
            assert record['base_sha256'] == epoch['pins'][name]
            sources[name] = ownership.claim(ROOT, name, record['base_sha256'], epoch['installed_identities'][name])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', native_head + ':' + name)).hexdigest() == record['base_sha256']
    for name, pin in policy['source_context_pins'].items():
        assert sha(ROOT / name) == pin
    ownership.quiescent(RUNTIME)
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists() and not (RUNTIME / 'SOURCE-TRANSITION.lock').is_symlink()
    flags = {name: state.h.git(path, env, 'ls-files', '-v', '-z') for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
    assert snapshot['index']['head'] == native_head
    assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
    return state, env, controls, epoch, role, sources, flags, snapshot


def guard(policy, ownership, roles, manifest):
    require_ready(policy, ownership, manifest)
    capture = current_capture(policy)
    state, env, controls, epoch, role, sources, flags, snapshot = observe(policy, ownership, roles, capture['checkpoint'])
    assert {name: hashlib.sha256(body).hexdigest() for name, body in controls.items()} == policy['controls'] == capture['controls']
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', policy['head'])
    assert snapshot == capture['snapshot'] and sources == {name: (capture['additional_sources'] | capture['payload_claims'])[name] for name in roles} and role == capture['role']
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
