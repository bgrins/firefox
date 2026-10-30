import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location('published_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_capture(policy, capture, roles):
    assert capture['full_current_state_verified'] is True and capture['source_transition_lock_absent'] is True
    assert capture['published_image_ancestor_verified'] is True and capture['sources_match_head'] is True
    checkpoint = capture['checkpoint']
    receipt = capture['checkpoint_receipt']
    assert sha(ROOT / receipt['path']) == receipt['sha256']
    assert read(ROOT / receipt['path']) == checkpoint
    assert checkpoint['committed'] and checkpoint['signature_verified']
    assert checkpoint['head'] == policy['head'] == capture['snapshot']['index']['head']
    assert checkpoint['epoch_sha256'] == capture['controls']['CURRENT-EPOCH.json']
    assert capture['controls'] == policy['controls']
    assert set(capture['controls']) == {'CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json'}
    assert capture['capture_helper_sha256'] == sha(HERE / 'capture_current.py')
    baseline = load('baseline')
    baseline.require_role(policy, capture['role'], {'prototype_overlay_state': capture['prototype_overlay_state']})
    load('review_scope').require_full(capture['snapshot'])
    assert set(capture['sources']) == set(roles)
    for name, record in roles.items():
        claim = capture['sources'][name]
        assert claim['path'] == name and claim['owned_sha256'] == record['base_sha256'] == record['candidate_sha256']
        assert len(claim['identity']) == 2 and all(isinstance(x, int) and x > 0 for x in claim['identity'])
    assert set(capture['payload_claims']) == set(capture['installed_identities'])
    expected_claims = {}
    for name, claim in capture['payload_claims'].items():
        assert claim['path'] == name and claim['identity'] == capture['installed_identities'][name]
        assert claim['owned_sha256'] == capture['epoch_payload_pins'][name]
        expected_claims[name] = {'sha256': claim['owned_sha256'], 'identity': claim['identity']}
    assert policy['accepted_current_payloads'] == expected_claims
    assert all(capture['sources'][name] == capture['payload_claims'][name] for name in roles)
    assert set(capture['flag_hashes']) == {'root', 'nested'}
    assert set(capture['binaries']) == set(policy['rebuilt_binaries'])
    assert set(capture['extras']) == set(policy['extra_backup_paths'])
    assert all(record['kind'] == 'file' for record in capture['extras'].values())
    assert capture['application_metadata']['revision'] == policy['restored_application_revision']
    assert capture['application_metadata']['sha256'] == '936bd88f3e47b0106b04b608cda306cc2fdee3bfd502e041b561febdb9643d3a'
    assert capture['application_metadata']['browser_build_id'] == '20261029165244'
    assert len(capture['app_inventory_sha256']) == 64


def validate_policy(policy):
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert len(roles) == 3
    for name, row in roles.items():
        assert row['base_sha256'] == row['candidate_sha256']
        for kind in ('base', 'candidate'):
            assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
        assert policy['source_context_pins'][name] == row['base_sha256']
    old = ROOT / 'artifacts/css-prioritary-selection-original-v3'
    prior = read(old / 'POLICY.json')
    for name in ('phases.py', 'wpt.py', 'assess.py', 'inputs.py', 'review_scope.py'):
        assert (HERE / name).read_bytes() == (old / name).read_bytes()
    assert (HERE / 'intermediate.py').read_bytes() == (ROOT / policy['diagnostic_binding']['directory'] / 'intermediate.py').read_bytes()
    for key in ('suite_binding', 'capture_binding', 'lane_order', 'metadata_current_pins', 'preserved_absent_resources'):
        assert policy[key] == prior[key]
    assert policy['preserved_absent_metadata'] == prior['preserved_absent_metadata'] + ['testing/web-platform/meta/css/css-values/exp-log-compute.html.ini']
    assert policy['source_context_pins']['servo/components/style/values/generics/calc.rs'] == '0803cce1f4e8c7c1f589342f4ddc7a0be923a9b43c244e1d5baa9bf4243fe526'
    for key in ('wpt', 'wpt_lanes'):
        actual, expected = copy.deepcopy(policy[key]), copy.deepcopy(prior[key])
        groups = [(actual, expected)] if key == 'wpt' else [(actual[name], expected[name]) for name in policy['lane_order']]
        for a, b in groups:
            assert set(a['phase_revisions']) == set(b['phase_revisions'])
            assert all(value == policy['head'] for value in a['phase_revisions'].values())
            assert a['harness_revision'] == policy['head']
            a.pop('phase_revisions'); b.pop('phase_revisions')
            a.pop('harness_revision'); b.pop('harness_revision')
        assert actual == expected
    assert policy['wpt']['expected_subtest_count'] == 77 and policy['wpt']['expected_page_count'] == 12
    assert len(set(policy['wpt']['fixture_target_pages'])) == 12
    assert set(policy['wpt']['fixture_target_pages']) == set(policy['wpt']['expected_subtests'])
    closure = load('closure').external_inputs(ROOT, policy, roles)
    for path, pin in closure.items():
        if pin is not None:
            assert sha(ROOT / path) == pin, path
    if policy['current_binding'] is None:
        assert policy['head'] is None and policy['controls'] is None
        assert policy['accepted_current_payloads'] == {}
        assert policy['intermediate_consumed_inputs'] is None
        assert policy['activation_pending']
        assert policy['execution_enabled'] is False and policy['candidate_execution_enabled'] is False
    else:
        binding = policy['current_binding']
        assert sha(ROOT / binding['path']) == binding['sha256']
        validate_capture(policy, read(ROOT / binding['path']), roles)
        assert policy['intermediate_consumed_inputs'] == closure
    return len(closure)


def rejected(action):
    try:
        action()
    except (AssertionError, TypeError, KeyError):
        return
    raise AssertionError('invalid preparation admitted')


if __name__ == '__main__':
    policy = read(HERE / 'POLICY.json')
    count = validate_policy(policy)
    mutations = [('head', 'invented'), ('controls', {}), ('intermediate_consumed_inputs', {})]
    if policy['current_binding'] is None:
        mutations += [('execution_enabled', True), ('candidate_execution_enabled', True), ('activation_pending', [])]
    else:
        mutations += [('current_binding', None)]
    for key, value in mutations:
        changed = copy.deepcopy(policy); changed[key] = value
        rejected(lambda: validate_policy(changed))
    old = ROOT / 'artifacts/css-prioritary-selection-original-v3/run.py'
    assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff(old.read_text().splitlines(True), (HERE / 'run.py').read_text().splitlines(True), fromfile='a/run.py', tofile='b/run.py'))
    before, after = old.read_text(), (HERE / 'run.py').read_text()
    marker = '    assert not restoration_errors, restoration_errors\n'
    assert before[before.index(marker):] == after[after.index(marker):]
    print(json.dumps({'consumed_static_inputs': count, 'suite': '77/12/89', 'unchanged_execution_helpers': 5,
                      'binding_negatives': len(mutations), 'final_restoration_publication_tail_unchanged': True,
                      'live_guard_executed': False, 'native_build': False, 'browser_run': False}))
