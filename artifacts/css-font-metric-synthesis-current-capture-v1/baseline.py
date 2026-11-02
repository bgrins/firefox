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


def observe(policy, ownership, roles, checkpoint):
    result = core.observe(policy, ownership, roles, checkpoint)
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
