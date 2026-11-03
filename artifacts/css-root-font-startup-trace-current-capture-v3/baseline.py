import copy
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
binding = json.loads((HERE/'BINDINGS.json').read_bytes())
for name, pin in binding['references'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == pin
spec = importlib.util.spec_from_file_location('executed_trace_baseline', ROOT/binding['executed_owner']['directory']/'baseline.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
spec = importlib.util.spec_from_file_location('strict_saved_equivalence', ROOT/binding['equivalence_helper']['directory']/'equivalence.py')
equivalence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(equivalence)


RUNTIME = core.RUNTIME
read = core.read
sha = core.sha
digest = core.digest
load = core.load
environment = core.environment
metadata_guard = core.metadata_guard
def require_role(policy, role, epoch):
    leaf = binding['role_validator']
    ownership = core.load('capture_role_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    ownership.authenticate(ROOT/leaf['directory'], leaf['manifest_sha256'])
    validator = core.load('capture_role_leaf', leaf['directory'] + '/baseline.py')
    assert validator.binding['capacity_commit'] == binding['capacity_commit']
    validator.require_role(policy, role, epoch)


def compare_saved(receipt, records):
    equal = equivalence.equal
    equal(receipt, records['native_receipt'], 'actual native receipt')
    assert receipt['signature_verified'] is True
    equal(receipt['epoch_sha256'], equivalence.INPUTS['original_epoch'][1], 'original native epoch')
    equal(receipt['commit'], binding['capacity_commit'], 'native HEAD')
    research = records['research_parent']
    assert research['committed'] is True and research['signature_verified'] is True
    equal(receipt['parent'], research['head'], 'signed research parent')
    equal(receipt['parent'], binding['native_parent'], 'native parent')
    original, current, previous = records['original_epoch'], records['current_epoch'], records['previous_epoch']
    original_capture, result = records['original_capture'], records['result']
    equal(original_capture['controls']['CURRENT-EPOCH.json'], receipt['epoch_sha256'], 'original capture epoch')
    equal(original_capture['prior_receipt_sha256'], equivalence.INPUTS['native_receipt'][1], 'original capture receipt')
    equal(records['original_terminal'], {'session':84891,'launch':'35cd73','terminal':'a35e44','exit':0,'capture_sha256':equivalence.INPUTS['original_capture'][1]}, 'original capture terminal')
    equal(result['signed_commit_receipt'], {'path':binding['native_receipt'],'sha256':equivalence.INPUTS['native_receipt'][1]}, 'refresh native receipt')
    equal(result['head'], receipt['commit'], 'refresh native HEAD')
    equal(result['epoch_sha256'], binding['current_epoch_sha256'], 'new epoch digest')
    equal(result['old_epoch_sha256'], binding['previous_epoch_sha256'], 'previous epoch digest')
    equal(result['updated_only'], 'raw_index_observation.current', 'refresh scope')
    for key in ('updated','preservation_verified','restoration_independently_verified','existing_head_signature_verified'):
        assert result[key] is True
    assert result['native_fix_acceptance'] is False
    equal(result['accepted_fix_increment'], 0, 'no acceptance increment')
    for key in ('before', 'after', 'frozen_pair_after'):
        assert type(result[key]) is str and len(result[key]) == 64 and set(result[key]) <= set('0123456789abcdef')
    equal(previous['raw_index_observation']['current'], result['before'], 'previous raw join')
    equal(current['raw_index_observation']['current'], result['after'], 'current raw join')
    equal(result['frozen_pair_after'], result['after'], 'audited raw join')
    for epoch, raw in ((original, original['raw_index_observation']['current']), (previous, result['before'])):
        equal(epoch['semantic_index']['head'], receipt['commit'], 'epoch native HEAD')
        normalized = copy.deepcopy(current)
        normalized['raw_index_observation']['current'] = raw
        equal(normalized, epoch, 'whole epoch equality')
    pre, post = records['pre'], records['post']
    equal(pre, post, 'refresh whole PRE POST equality')
    equal(post['index']['raw_index'], result['after'], 'snapshot raw join')
    equal({k:v for k,v in post['index'].items() if k != 'raw_index'}, current['semantic_index'], 'snapshot semantic index')
    equal({k:v for k,v in post['nested_index'].items() if k != 'raw_index'}, current['nested_semantic_index'], 'snapshot nested index')
    normalized = copy.deepcopy(post)
    normalized['index']['raw_index'] = original_capture['audit']['index']['raw_index']
    equal(original_capture['audit']['index']['raw_index'], original['raw_index_observation']['current'], 'original snapshot raw join')
    equal(normalized, original_capture['audit'], 'whole original snapshot equality')
    terminal = records['terminal']['refresh']
    equal({k:terminal[k] for k in ('launch','session','terminal','exit')}, {'launch':'761647','session':25987,'terminal':'e149b6','exit':0}, 'actual refresh terminal')
    equal(sorted(terminal), sorted(['launch','session','terminal','exit','active_manifest']), 'actual refresh terminal fields')
    equal(terminal['active_manifest'], '8c5273502b3b5ebaa872e900a35bcacfb73020b2dad7e3188bca2298076c4d86', 'executed refresh manifest')
    verification = records['verification']
    assert verification['raw_only_epoch_change'] is True
    assert verification['source_app_flags_controls_verified'] is True
    equal(verification['snapshot'], post, 'verified whole POST')
    equal(verification['result_sha256'], binding['refresh_binding']['result_sha256'], 'verified result')
    equal(sorted(records['terminal']), ['refresh','verification'], 'actual combined terminal fields')
    equal(records['verification_terminal'], records['terminal'], 'same actual combined receipt')
    equal(records['verification_terminal']['verification'], {'launch':'a7bdbc','session':4423,'terminal':'8ccc6d','exit':0,'verifier_sha256':verification['script_sha256']}, 'actual independent verification terminal')
    return post


def saved_native_state(receipt):
    ownership = core.load('capture_owned_inputs', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    ownership.authenticate(ROOT/binding['refresh_binding']['directory'], binding['refresh_manifest_sha256'])
    ownership.authenticate(ROOT/binding['equivalence_helper']['directory'], binding['equivalence_helper']['manifest_sha256'])
    records = {}
    for name, path in binding['saved_inputs'].items():
        body = (ROOT/path).read_bytes()
        assert hashlib.sha256(body).hexdigest() == binding['references'][path]
        records[name] = equivalence.decode(body)
    for key in ('native_receipt','original_epoch','original_capture','original_terminal'):
        assert binding['saved_inputs'][key] == equivalence.INPUTS[key][0]
        assert binding['references'][binding['saved_inputs'][key]] == equivalence.INPUTS[key][1]
    assert binding['references'][binding['saved_inputs']['current_epoch']] == binding['current_epoch_sha256']
    assert binding['references'][binding['saved_inputs']['previous_epoch']] == binding['previous_epoch_sha256']
    assert binding['references'][binding['saved_inputs']['result']] == binding['refresh_binding']['result_sha256']
    return compare_saved(receipt, records)


def prepare(manifest):
    policy, ownership, _ = core.prepare(binding['executed_owner']['manifest_sha256'])
    ownership.authenticate(HERE, manifest)
    prior = binding['prior_capture']
    assert core.sha(ROOT/prior['path']) == prior['sha256']
    capture = core.read(ROOT/prior['path'])
    roles = {name:{'base_sha256':claim['owned_sha256'],'candidate_sha256':claim['owned_sha256']} for name,claim in capture['sources'].items()}
    assert set(roles) == set(core.read(ROOT/policy['capture_source_owner']['directory']/'SOURCE-ROLES.json'))
    return policy, ownership, roles


def claim_additional_sources(ownership, state, env, epoch, head):
    assert set(binding['additional_sources']) == {'servo/components/style/data.rs', 'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs', 'layout/style/ServoStyleSet.cpp'}
    result = {}
    for name, record in binding['additional_sources'].items():
        assert name not in epoch['installed_identities']
        assert name not in epoch['pins'] or epoch['pins'][name] == record['base_sha256']
        assert core.sha(ROOT / record['base_capture']) == record['base_sha256']
        result[name] = ownership.claim(ROOT, name, record['base_sha256'])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', head + ':' + name)).hexdigest() == record['base_sha256']
    return result


def observe(policy, ownership, roles, checkpoint):
    env = environment()
    state = load('published_state', policy['state_helper'])
    native_receipt = checkpoint
    expected_snapshot = saved_native_state(native_receipt)
    native_head = native_receipt['commit']
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    epoch, role = json.loads(controls['CURRENT-EPOCH.json']), json.loads(controls['ROLE.json'])
    assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == binding['current_epoch_sha256']
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
    state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', binding['native_parent'])
    assert state.h.git(ROOT, env, 'rev-parse', native_head + '^').decode().strip() == binding['native_parent']
    assert state.h.git(ROOT, env, 'diff-tree', '--no-commit-id', '--name-only', '-r', native_head).decode().splitlines() == native_receipt['files']
    metadata_guard(policy)
    for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    sources = {}
    for name, record in roles.items():
        assert record['base_sha256'] == record['candidate_sha256'] == epoch['pins'][name]
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
    equivalence.equal(snapshot, expected_snapshot, 'fresh whole state equals saved direct target')
    for name, pin in binding['source_preimages'].items():
        assert epoch['pins'][name] == pin
        ownership.claim(ROOT, name, pin, epoch['installed_identities'][name])
        assert hashlib.sha256(state.h.git(ROOT, env, 'show', native_head + ':' + name)).hexdigest() == pin
    for name, pin in binding['typecheck_required_inputs'].items():
        assert core.sha(ROOT / name) == pin
    return state, env, controls, epoch, role, sources, flags, snapshot


def __getattr__(name):
    return getattr(core, name)
