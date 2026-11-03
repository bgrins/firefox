import copy
import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parent = ROOT / 'artifacts/css-root-font-cancellation-archive-current-capture-v1'
binding = read(HERE / 'BINDINGS.json')
role_path = ROOT / 'artifacts/css-root-font-cancellation-trace-instrumentation-v2/SOURCE-ROLES.json'
roles = read(role_path)
for name in ('baseline.py', 'capture_current.py'):
    assert (HERE / name).read_bytes() == (parent / name).read_bytes()
for name, pin in binding['references'].items():
    assert sha(ROOT / name) == pin, name


def check_bridge(b):
    assert not b['pending_pair_refresh']
    validator = b['refresh_validator']
    assert validator['directory'] == str(parent.relative_to(ROOT))
    assert sha(parent / 'baseline.py') == validator['driver_sha256']
    assert sha(parent / 'BINDINGS.json') == validator['bindings_sha256']
    previous = read(parent / 'BINDINGS.json')
    assert b['additional_sources'] == previous['additional_sources']
    assert b['native_receipt'] == previous['native_receipt']
    receipt = read(ROOT / b['native_receipt'])
    assert receipt['signature_verified'] and receipt['commit'] == b['capacity_commit']
    research = read(ROOT / b['research_parent_receipt'])
    assert research['committed'] and research['signature_verified']
    assert receipt['parent'] == research['head'] == b['native_parent']
    directory = ROOT / b['refresh_binding']['directory']
    assert sha(directory / 'FILES.json') == b['refresh_manifest_sha256']
    assert sha(directory / 'RESULT.json') == b['refresh_binding']['result_sha256']
    result = read(directory / 'RESULT.json')
    owner = ROOT / b['refresh_owner']['directory']
    assert sha(owner / 'FILES.json') == b['refresh_owner']['manifest_sha256']
    policy = read(owner / 'POLICY.json')
    assert policy['output'] == b['refresh_binding']['directory']
    assert policy['refresh_parent'] == previous['refresh_binding']
    assert result['signed_commit_receipt'] == policy['signed_receipt'] == {
        'path': b['native_receipt'], 'sha256': sha(ROOT / b['native_receipt'])}
    assert result['head'] == receipt['commit']
    assert result['updated'] and result['updated_only'] == 'raw_index_observation.current'
    assert result['preservation_verified'] and result['restoration_independently_verified']
    assert result['existing_head_signature_verified'] and not result['native_fix_acceptance']
    assert result['accepted_fix_increment'] == 0
    old = read(directory / 'PRE-CURRENT-EPOCH.json')
    new = read(directory / 'EPOCH.json')
    assert sha(directory / 'PRE-CURRENT-EPOCH.json') == result['old_epoch_sha256'] == previous['current_epoch_sha256']
    assert sha(directory / 'EPOCH.json') == result['epoch_sha256'] == b['current_epoch_sha256']
    assert old['raw_index_observation']['current'] == result['before']
    changed = copy.deepcopy(old)
    changed['raw_index_observation']['current'] = result['after']
    assert changed == new
    post = read(directory / 'POST.json')
    assert post == read(directory / 'PRE.json')
    assert post['index']['raw_index'] == result['after'] == result['frozen_pair_after']
    assert {k: v for k, v in post['index'].items() if k != 'raw_index'} == new['semantic_index']
    frozen = ROOT / policy['runtime']
    raw = read(frozen / 'RAW-INDEX-OBSERVATION.json')
    assert raw['before'] == result['before'] and raw['after'] == result['after']
    for snapshot in (read(ROOT / previous['refresh_binding']['directory'] / 'POST.json'),
                     read(frozen / 'PAIR-PRE.json')['snapshot'], read(frozen / 'POST.json')):
        projected = copy.deepcopy(snapshot)
        projected['index']['raw_index'] = result['after']
        assert projected == post
    return new


def check_roles(epoch, additional, source_roles):
    assert set(source_roles) == {
        'dom/animation/EffectCompositor.cpp', 'layout/style/GeckoBindings.cpp',
        'servo/components/style/matching.rs', 'servo/components/style/data.rs',
        'servo/components/style/traversal.rs'}
    assert set(additional) == {'servo/components/style/data.rs', 'servo/components/style/traversal.rs'}
    for name, role in source_roles.items():
        assert role['base_commit'] == binding['capacity_commit']
        if name in additional:
            assert name not in epoch['installed_identities']
            assert additional[name]['base_sha256'] == role['base_sha256']
        else:
            assert epoch['pins'][name] == role['base_sha256']
            assert len(epoch['installed_identities'][name]) == 2
    assert epoch['pins']['servo/ports/geckolib/glue.rs'] == binding['source_preimages']['servo/ports/geckolib/glue.rs']


epoch = check_bridge(binding)
check_roles(epoch, binding['additional_sources'], roles)
rejected = []
for label, mutate in [
    ('pending refresh', lambda b: b.update(pending_pair_refresh=True)),
    ('parent driver', lambda b: b['refresh_validator'].update(driver_sha256='0' * 64)),
    ('parent bindings', lambda b: b['refresh_validator'].update(bindings_sha256='0' * 64)),
    ('latest result', lambda b: b['refresh_binding'].update(result_sha256='0' * 64)),
    ('latest epoch', lambda b: b.update(current_epoch_sha256='0' * 64)),
    ('latest owner', lambda b: b['refresh_owner'].update(manifest_sha256='0' * 64)),
]:
    changed = copy.deepcopy(binding)
    mutate(changed)
    try:
        check_bridge(changed)
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError(label)
for name in roles:
    changed = copy.deepcopy(roles)
    changed[name]['base_sha256'] = '0' * 64
    try:
        check_roles(epoch, binding['additional_sources'], changed)
    except AssertionError:
        rejected.append('changed source base: ' + name)
    else:
        raise AssertionError(name)
result = {
    'success': True, 'references': len(binding['references']), 'source_roles': len(roles),
    'canonical_roles': 3, 'additional_roles': 2, 'rejected': rejected,
    'production_helpers_byte_identical': True, 'actual_saved_bridge_projection': True,
    'recursive_saved_validator_rerun': False, 'live_capture_executed': False,
    'scope': 'Focused frozen binding joins; actual root capture retains complete recursive validation and live observation.',
    'tested_inputs': {name: sha(HERE / name) for name in ('baseline.py', 'capture_current.py', 'BINDINGS.json', 'check_bindings.py')},
}
with (HERE / 'CHECK-RESULT.json').open('x') as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps(result, sort_keys=True))
