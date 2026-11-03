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
    assert role['role'] == 'published-native' and role['variant'] == 'capacity'
    assert role['built'] is False and role['paired_head'] == binding['capacity_commit']
    assert role['pending_gtest_overlay_installed'] is False
    assert 'last_build' not in role and 'last_install' not in role
    directory = 'artifacts/css-prioritary-declaration-capacity-publication-capacity-runtime-1'
    assert role['last_transition'] == directory
    receipt = core.read(ROOT / directory / 'COMMIT-RESULT.json')
    install = core.read(ROOT / directory / 'INSTALL-RESULT.json')
    assert receipt['commit'] == binding['capacity_commit'] and receipt['signature_verified']
    assert receipt['accepted_fix_increment'] == 0 and not receipt['app_rebuilt']
    assert install['installed'] and not install['app_rebuilt']
    marker = epoch['prioritary_declaration_capacity_publication']['capacity']
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
    assert not binding['pending_pair_refresh'], 'Completed pair raw-refresh admission is pending'
    policy, ownership, roles = core.prepare(binding['executed_original_manifest'])
    ownership.authenticate(HERE, manifest)
    source = binding['source']
    assert roles[source]['base_sha256'] == roles[source]['candidate_sha256'] == policy['source_context_pins'][source]
    assert core.sha(ROOT / binding['source_capture']) == binding['source_sha256']
    roles[source] = {
        'base_capture': binding['source_capture'], 'candidate_capture': binding['source_capture'],
        'base_sha256': binding['source_sha256'], 'candidate_sha256': binding['source_sha256'],
    }
    policy['source_context_pins'][source] = binding['source_sha256']
    return policy, ownership, roles


def native_head_view(receipt):
    assert not binding['pending_pair_refresh'], 'Completed pair raw-refresh admission is pending'
    assert set(receipt) == {'stage', 'commit', 'parent', 'signature_verified', 'files', 'epoch_sha256', 'accepted', 'accepted_fix_increment', 'app_rebuilt'}
    assert receipt == core.read(ROOT / binding['native_receipt'])
    assert receipt['stage'] == 'capacity' and receipt['signature_verified'] is True
    assert receipt['commit'] == binding['capacity_commit']
    assert receipt['accepted'] is False and receipt['accepted_fix_increment'] == 0
    assert receipt['app_rebuilt'] is False
    assert receipt['files'] == ['servo/components/style/properties/cascade.rs', 'testing/web-platform/tests/css/css-cascade/prioritary-after-many-unrelated-declarations.html']
    research = core.read(ROOT / binding['research_parent_receipt'])
    assert research['committed'] and research['signature_verified']
    assert receipt['parent'] == research['head'] == binding['native_parent']
    expected = validate_refresh(receipt)
    return {'head': receipt['commit'], 'epoch_sha256': binding['current_epoch_sha256'],
            'committed': True, 'signature_verified': True,
            'authority_kind': 'internal-observed-head-from-native-receipt-and-raw-refresh'}


def validate_refresh(receipt):
    assert not binding['pending_pair_refresh'], 'Completed pair raw-refresh admission is pending'
    record = binding['refresh_validator']
    parent_dir = ROOT / record['directory']
    assert core.sha(parent_dir / 'baseline.py') == record['driver_sha256']
    assert core.sha(parent_dir / 'BINDINGS.json') == record['bindings_sha256']
    parent = core.load('previous_native_capture_bridge', str((parent_dir / 'baseline.py').relative_to(ROOT)))
    assert parent.binding['native_receipt'] == binding['native_receipt']
    previous = parent.validate_refresh(receipt)
    refresh = binding['refresh_binding']
    assert refresh is not None
    directory = ROOT / refresh['directory']
    ownership = core.load('capture_refresh_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    ownership.authenticate(directory, binding['refresh_manifest_sha256'])
    assert core.sha(directory / 'RESULT.json') == refresh['result_sha256']
    result = core.read(directory / 'RESULT.json')
    owner_record = binding['refresh_owner']
    owner_dir = ROOT / owner_record['directory']
    ownership.authenticate(owner_dir, owner_record['manifest_sha256'])
    driver = core.load('completed_integrated_raw_refresh', str((owner_dir / 'run.py').relative_to(ROOT)))
    policy = core.read(owner_dir / 'POLICY.json')
    assert policy['output'] == refresh['directory']
    assert policy['signed_receipt'] == {'path': binding['native_receipt'], 'sha256': core.sha(ROOT / binding['native_receipt'])}
    assert policy['refresh_parent'] == parent.binding['refresh_binding']
    _, _, frozen_pre, frozen_post, raw = driver.saved(policy)
    assert result['updated'] and result['updated_only'] == 'raw_index_observation.current'
    assert result['preservation_verified'] and result['restoration_independently_verified']
    assert result['existing_head_signature_verified'] and result['accepted_fix_increment'] == 0
    assert not result['native_fix_acceptance']
    assert result['head'] == receipt['commit'] == binding['capacity_commit']
    assert result['signed_commit_receipt'] == policy['signed_receipt']
    old_body, new_body = (directory / 'PRE-CURRENT-EPOCH.json').read_bytes(), (directory / 'EPOCH.json').read_bytes()
    assert hashlib.sha256(old_body).hexdigest() == result['old_epoch_sha256'] == parent.binding['current_epoch_sha256']
    assert hashlib.sha256(new_body).hexdigest() == result['epoch_sha256'] == binding['current_epoch_sha256']
    old, new = json.loads(old_body), json.loads(new_body)
    assert old['raw_index_observation']['current'] == result['before'] == raw['before']
    expected = json.loads(old_body)
    expected['raw_index_observation']['current'] = result['after']
    assert expected == new and new['semantic_index']['head'] == receipt['commit']
    assert result['frozen_pair_after'] == raw['after']
    pre, post = core.read(directory / 'PRE.json'), core.read(directory / 'POST.json')
    assert pre == post and post['index']['raw_index'] == result['after']
    assert {k:v for k,v in post['index'].items() if k != 'raw_index'} == new['semantic_index']
    for snapshot in (previous, frozen_pre['snapshot'], frozen_post):
        projected = json.loads(json.dumps(snapshot))
        projected['index']['raw_index'] = result['after']
        assert projected == post
    return post


def claim_additional_sources(ownership, state, env, epoch, head):
    assert set(binding['additional_sources']) == {'servo/components/style/traversal.rs', 'servo/components/style/data.rs'}
    result = {}
    for name, record in binding['additional_sources'].items():
        assert name not in epoch['installed_identities']
        assert name not in epoch['pins'] or epoch['pins'][name] == record['base_sha256']
        assert core.sha(ROOT / record['base_capture']) == record['base_sha256']
        result[name] = ownership.claim(ROOT, name, record['base_sha256'])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', head + ':' + name)).hexdigest() == record['base_sha256']
    return result



def observe(policy, ownership, roles, checkpoint):
    native_receipt = checkpoint
    checkpoint = native_head_view(native_receipt)
    result = core.observe(policy, ownership, roles, checkpoint)
    state, env, controls, epoch, role, sources, flags, snapshot = result
    assert snapshot == validate_refresh(native_receipt)
    assert state.h.git(ROOT, env, 'rev-parse', checkpoint['head'] + '^').decode().strip() == binding['native_parent']
    assert state.h.git(ROOT, env, 'diff-tree', '--no-commit-id', '--name-only', '-r', checkpoint['head']).decode().splitlines() == native_receipt['files']
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', binding['native_parent'])
    for commit in (binding['nowrap_commit'], binding['language_commit'], binding['ownership_commit'], binding['capacity_commit']):
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
