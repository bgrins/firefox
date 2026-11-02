import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
binding = json.loads((HERE / 'BINDINGS.json').read_bytes())
for name, pin in binding['references'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin
spec = importlib.util.spec_from_file_location('executed_published_capture_baseline', ROOT / 'artifacts/css-prioritary-published-original-v1/baseline.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def require_role(policy, role, epoch):
    assert role['role'] == 'published-native' and role['variant'] == 'ownership'
    assert role['built'] is False and role['paired_head'] == binding['ownership_commit']
    assert role['pending_gtest_overlay_installed'] is False
    assert 'last_build' not in role and 'last_install' not in role
    directory = 'artifacts/css-hyphenation-ownership-publication-ownership-runtime-2'
    assert role['last_transition'] == directory
    receipt = core.read(ROOT / directory / 'COMMIT-RESULT.json')
    install = core.read(ROOT / directory / 'INSTALL-RESULT.json')
    assert receipt['commit'] == binding['ownership_commit'] and receipt['signature_verified']
    assert receipt['accepted_fix_increment'] == 0 and not receipt['app_rebuilt']
    assert install['installed'] and not install['app_rebuilt']
    marker = epoch['hyphenation_ownership_publication']['ownership']
    assert marker['native_commit'] == receipt['commit']
    assert marker['installation_manifest'] == install['manifest_sha256']
    assert marker['files'][binding['source']] == binding['source_sha256']
    assert set(marker['files']) == set(receipt['files']) == set(install['files'])
    assert not marker['accepted'] and not marker['compiled'] and not marker['current_app_contains_candidate']
    retirement = epoch['prototype_overlay_state']
    assert retirement['installed'] is False and retirement['held_provider_parked'] is True
    assert retirement['old_restoration_recipes_require_rebase'] is True
    path = 'artifacts/css-registered-color-image-publication-union-runtime-1/PRE-ROLE.json'
    assert retirement['original_role_preserved_in'] == path
    claims = core.read(ROOT / 'artifacts/css-registered-color-image-publication-union-runtime-1/INITIAL-CLAIMS.json')
    assert claims['controls']['ROLE.json']['owned_sha256'] == core.sha(ROOT / path)


core.require_role = require_role


def prepare(manifest):
    policy, ownership, roles = core.prepare(binding['executed_original_manifest'])
    ownership.authenticate(HERE, manifest)
    return policy, ownership, roles


def observe_refreshed(policy, ownership, roles, checkpoint):
    env = core.environment()
    state = core.load('published_state', policy['state_helper'])
    assert checkpoint['committed'] and checkpoint['signature_verified']
    controls = {name: (core.RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    epoch, role = json.loads(controls['CURRENT-EPOCH.json']), json.loads(controls['ROLE.json'])
    refresh = core.load('diagnostic_verified_refresh', binding['refresh_owner'] + '/commit.py')
    assert checkpoint == core.read(ROOT / refresh.BINDINGS['prior_receipt'])
    assert core.sha(ROOT / refresh.BINDINGS['prior_receipt']) == refresh.BINDINGS['prior_receipt_sha256']
    refreshed = refresh.validate_refresh(checkpoint)
    assert {name:hashlib.sha256(value).hexdigest() for name,value in controls.items()} == refresh.BINDINGS['controls']
    assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == refresh.BINDINGS['epoch_sha256']
    assert epoch['semantic_index']['head'] == checkpoint['head']
    assert epoch['staged_working'] == {} and epoch['modified_native_paths'] == []
    require_role(policy, role, epoch)
    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['image_commit'], checkpoint['head'])
    core.metadata_guard(policy)
    for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    sources = {}
    for name, record in roles.items():
        assert record['base_sha256'] == record['candidate_sha256'] == epoch['pins'][name]
        sources[name] = ownership.claim(ROOT, name, record['base_sha256'], epoch['installed_identities'][name])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', checkpoint['head'] + ':' + name)).hexdigest() == record['base_sha256']
    for name, pin in policy['source_context_pins'].items():
        assert core.sha(ROOT / name) == pin
    ownership.quiescent(core.RUNTIME)
    assert not (core.RUNTIME / 'SOURCE-TRANSITION.lock').exists() and not (core.RUNTIME / 'SOURCE-TRANSITION.lock').is_symlink()
    flags = {name: state.h.git(path, env, 'ls-files', '-v', '-z') for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
    assert snapshot == refreshed and snapshot['index']['head'] == checkpoint['head']
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', checkpoint['head'])
    assert all((core.RUNTIME / name).read_bytes() == body for name, body in controls.items())
    return state, env, controls, epoch, role, sources, flags, snapshot


def observe(policy, ownership, roles, checkpoint):
    result = observe_refreshed(policy, ownership, roles, checkpoint)
    state, env, controls, epoch, role, sources, flags, snapshot = result
    for commit in (binding['nowrap_commit'], binding['language_commit'], binding['ownership_commit']):
        assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', commit, checkpoint['head'])
        state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', commit)
    for name, pin in binding['source_preimages'].items():
        assert epoch['pins'][name] == pin
        ownership.claim(ROOT, name, pin, epoch['installed_identities'][name])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', checkpoint['head'] + ':' + name)).hexdigest() == pin
    for name, pin in binding['typecheck_required_inputs'].items():
        assert core.sha(ROOT / name) == pin
    return result


def __getattr__(name):
    return getattr(core, name)
