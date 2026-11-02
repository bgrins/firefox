import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
EXPECTED_HEAD = '70d9abdf9784cf84732aed747cbec87fe0589d95'
EXPECTED_CHECKPOINT = '526b97af7108c7d4d1d014b2ec48299d8e7f6a6f7fb4cc7fec8411aa274a46a9'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location('metric_check_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_driver(body, enabled):
    assert type(enabled) is bool
    line = 'EXECUTION_ENABLED = ' + str(enabled)
    assert body.splitlines().count(line) == 1 and body.count('EXECUTION_ENABLED = ') == 1
    return body.replace(line, 'EXECUTION_ENABLED = False')


def validate_policy(policy):
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-font-metric-dynamic-native-typecheck-runtime-1'
    assert policy['head'] == EXPECTED_HEAD
    assert policy['ownership_commit'] == '8870962db02b006791085b73f9e270942e145365'
    admission = load('admission')
    prior = admission.authenticate(ROOT, policy['predecessor_binding'])
    template = admission.authenticate(ROOT, policy['typecheck_binding'])
    assert prior == ROOT / 'artifacts/css-hyphenation-ownership-native-pair-v2'
    assert template == ROOT / 'artifacts/css-font-metric-synthesis-native-typecheck-v2'
    old = read(prior / 'POLICY.json')
    for name in ('image_commit', 'nowrap_commit', 'language_commit', 'ownership_helper', 'phase_helper', 'process_helper', 'state_helper', 'bundle_helper', 'bundle_path', 'extra_backup_paths', 'rebuilt_binaries', 'source_context_pins', 'restored_application_revision', 'timeout_seconds', 'metadata_current_pins', 'preserved_absent_metadata', 'preserved_absent_resources', 'wpt'):
        assert policy[name] == old[name], name
    assert policy['wpt_lanes'] == {} and policy['lane_order'] == policy['diagnostic_lane_order'] == []
    admission.authenticate(ROOT, policy['source_binding'])
    assert policy['source_binding']['directory'] == 'artifacts/css-font-metric-dynamic-prerequisite-producer-v1'
    typecheck = read(HERE / 'TYPECHECK.json')
    prepared = read(template / 'TYPECHECK.json')
    for name in ('command', 'required_input_hashes', 'fresh_input_revalidation_required'):
        assert typecheck[name] == prepared[name], name
    assert typecheck['current_binding'] == policy['current_binding']
    assert typecheck['baseline_and_policy_materialization_required'] is False
    assert policy['required_typecheck_inputs'] == typecheck['required_input_hashes']
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert roles == typecheck['source_roles'] and len(roles) == 2
    assert set(roles) == set(prepared['source_roles'])
    for name, row in roles.items():
        for key in ('base_sha256', 'base_capture'):
            assert row[key] == prepared['source_roles'][name][key]
        assert row['candidate_capture'] == policy['source_binding']['directory'] + '/candidate/' + name
    assert policy['committed_source_preimages'] == {name: row['base_sha256'] for name, row in roles.items()}
    for row in roles.values():
        for kind in ('base', 'candidate'):
            assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
    assert policy['execution_enabled'] == policy['candidate_execution_enabled'] == typecheck['execution_enabled']
    assert normalized_driver((HERE / 'run.py').read_text(), policy['execution_enabled']) == (template / 'run.py').read_text()
    assert (HERE / 'assess.py').read_bytes() == (template / 'assess.py').read_bytes()
    for name in ('inputs.py', 'intermediate.py', 'review_scope.py'):
        assert (HERE / name).read_bytes() == (prior / name).read_bytes()
    for path, digest in policy['references'].items():
        assert sha(ROOT / path) == digest, path
    closure = load('closure').external_inputs(ROOT, policy, roles)
    assert closure == policy['intermediate_consumed_inputs']
    for path, digest in closure.items():
        if path.startswith('artifacts/'):
            assert digest is not None and sha(ROOT / path) == digest, path
    if policy['current_binding'] is None:
        assert EXPECTED_HEAD is EXPECTED_CHECKPOINT is None and policy['head'] is None
        assert policy['controls'] is None and policy['accepted_current_payloads'] == {}
        assert policy['activation_pending'] and not policy['execution_enabled']
        return len(closure)
    capture = admission.validate_current(ROOT, policy, roles)
    assert capture['checkpoint_receipt']['sha256'] == EXPECTED_CHECKPOINT
    adapter = read(ROOT / policy['capture_owner']['directory'] / 'BINDINGS.json')
    assert adapter['typecheck_required_inputs'] == typecheck['required_input_hashes']
    assert policy['resource_policy']['start_after_backups_bytes'] == 27 * 1024**3
    assert policy['resource_policy']['running_stop_bytes'] == 15 * 1024**3
    return len(closure)


if __name__ == '__main__':
    policy = read(HERE / 'POLICY.json')
    count = validate_policy(policy)
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    assert not read(HERE / 'TYPECHECK.json')['execution_enabled']
    runpy.run_path(str(HERE / 'check_assessor.py'), run_name='__main__')
    driver = (HERE / 'run.py').read_text()
    active = driver.replace('EXECUTION_ENABLED = False', 'EXECUTION_ENABLED = True')
    assert normalized_driver(active, True) == driver
    assert normalized_driver(active + '\nraise RuntimeError(\'unrelated change\')\n', True) != driver
    if policy['current_binding'] is None:
        try:
            load('baseline').require_ready(policy)
        except AssertionError:
            pass
        else:
            raise AssertionError('Pending admission accepted')
        print(json.dumps({'consumed_inputs': count, 'pending_admission_rejected': True, 'no_live_operations': True}))
        raise SystemExit(0)
    negatives = 0
    for key, value in [('head', '0' * 40), ('ownership_commit', '0' * 40), ('current_binding', None), ('controls', {}), ('accepted_current_payloads', {}), ('committed_source_preimages', {}), ('required_typecheck_inputs', {})]:
        changed = copy.deepcopy(policy)
        changed[key] = value
        try:
            validate_policy(changed)
        except (AssertionError, KeyError, TypeError):
            negatives += 1
        else:
            raise AssertionError('Accepted mutation: ' + key)
    print(json.dumps({'consumed_inputs': count, 'binding_negatives': negatives, 'exact_typecheck_driver_and_assessor': True, 'unchanged_intermediate_helpers': 3, 'active_literal_identity_positive': True, 'unrelated_driver_change_rejected': True, 'no_live_operations': True}))
