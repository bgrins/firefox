import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    owner = load('clean_candidate_ownership', ROOT / policy['ownership_helper'])
    prior = ROOT / policy['predecessor']['directory']
    owner.authenticate(prior, policy['predecessor']['manifest_sha256'])
    old = read(prior / 'POLICY.json')
    mutable = {'owner_directory', 'runtime_output', 'execution_enabled', 'candidate_execution_enabled', 'activation_pending',
               'baseline_binding', 'baseline_capsule', 'original_admission_policy_sha256', 'head', 'controls',
               'prepared_application_metadata', 'prepared_flag_hashes', 'prepared_flag_capture',
               'restored_application_revision', 'execution_handoff', 'suite_binding', 'predecessor',
               'semantic_original_sources', 'source_roster', 'wpt', 'preserved_absent_resources', 'references'}
    assert {k: v for k, v in policy.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-animation-taint-clean-candidate-runtime-1'
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled'] and policy['activation_pending']
    assert all(policy[k] is None for k in ('baseline_binding', 'baseline_capsule', 'original_admission_policy_sha256', 'head', 'controls', 'prepared_application_metadata', 'prepared_flag_hashes', 'prepared_flag_capture', 'execution_handoff'))
    assert policy['restored_application_revision'] == old['wpt']['phase_revisions']['original']
    for path, digest in policy['references'].items():
        assert sha(ROOT / path) == digest, path
    assert all(policy['references'][path] == digest for path, digest in old['references'].items())
    proposal = ROOT / policy['proposal']['directory']
    owner.authenticate(proposal, policy['proposal']['manifest_sha256'])
    clean = read(proposal / 'CLEAN-PROVIDER.json')
    roles = read(HERE / 'SOURCE-ROLES.json')
    expected = read(proposal / 'SOURCE-ROLES.json')
    name = 'servo/components/style/custom_properties.rs'
    expected[name].update(candidate_capture=clean['candidate_capture'], candidate_sha256=clean['candidate_sha256'])
    assert roles == expected and set(roles) == set(policy['source_paths'])
    for row in roles.values():
        for kind in ('base', 'candidate'):
            assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
    assert policy['semantic_original_sources'] == policy['committed_source_preimages']
    assert policy['semantic_original_sources'][name] == clean['base_sha256'] != roles[name]['base_sha256']
    assert policy['references'][str((proposal / 'native-clean-provider.patch').relative_to(ROOT))] == sha(proposal / 'native-clean-provider.patch')
    load('prior_source_lineage', prior / 'check.py').validate_lineage(old, read(prior / 'SOURCE-ROLES.json'))
    suite = ROOT / policy['suite_binding']['directory']
    owner.authenticate(suite, policy['suite_binding']['manifest_sha256'])
    load('clean_suite', suite / 'check.py').main()
    union = read(suite / 'INPUTS.json')
    assert policy['source_roster'] == str((suite / 'ROSTER.json').relative_to(ROOT))
    assert policy['preserved_absent_resources'] == old['preserved_absent_resources'] + [read(ROOT / union['previous_suite']['directory'] / 'INPUTS.json')['new_metadata_absence'], union['new_metadata_absence']]
    comparison = load('clean_candidate_comparison', HERE / 'comparison.py')
    assert policy['wpt'] == comparison.expected_wpt(ROOT, policy)
    pages = policy['wpt']['fixture_target_pages']
    assert len(pages) == len(set(pages)) == 18 and set(pages) == set(policy['wpt']['expected_subtests'])
    assert all((HERE / n).read_bytes() == (prior / n).read_bytes() for n in ('phases.py', 'wpt.py', 'assess.py'))


def validate_actual_bindings(policy):
    load('clean_candidate_admission', HERE / 'admission.py').validate(ROOT, policy)


def check():
    policy = read(HERE / 'POLICY.json')
    validate_policy(policy)
    for change in (
        lambda p: p.update(baseline_binding={'invented': True}),
        lambda p: p.update(execution_handoff={'invented': True}),
        lambda p: p.update(execution_enabled=True, candidate_execution_enabled=True, activation_pending=[]),
        lambda p: p.update(head='0' * 40),
        lambda p: p['wpt']['fixture_target_pages'].pop(),
    ):
        bad = copy.deepcopy(policy)
        change(bad)
        try:
            validate_policy(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('pending admission was bypassed')
    assessor = load('clean_observation_assessor', HERE / 'assess.py')
    checks = load('clean_stream_checks', ROOT / policy['wpt']['checks_helper'])
    comparison = load('clean_projection', HERE / 'comparison.py')
    settings = copy.deepcopy(policy['wpt'])
    settings.update(harness_revision='a' * 40, phase_revisions={'original': 'b' * 40, 'candidate': 'a' * 40})
    app = {'browser_build_id': 'synthetic', 'revision': 'b' * 40, 'build_revision': 'b' * 40, 'harness_revision': 'a' * 40, 'source_role': 'original', 'sha256': 'c' * 64, 'path': 'synthetic/application.ini', 'resolved': 'synthetic/application.ini'}
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False, 'browser_build_id': 'synthetic', 'revision': 'a' * 40}}]
    for page, names in settings['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': page})
        events.extend({'action': 'test_status', 'test': page, 'subtest': name, 'status': 'PASS'} for name in names)
        events.append({'action': 'test_end', 'test': page, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    original = assessor.assess(events, 0, comparison.phase_policy(settings), checks, run_binding=app)
    assert original['complete']
    failed = copy.deepcopy(events)
    for row in failed:
        if row.get('action') == 'test_status':
            row.update(status='FAIL', expected='PASS', message='synthetic ordinary assertion')
    candidate_app = dict(app, revision='a' * 40, build_revision='a' * 40, source_role='candidate')
    observed = assessor.assess(failed, 1, comparison.phase_policy(settings), checks, original=original, run_binding=candidate_app)
    assert observed['complete'] and len(observed['rows']) == 125 and not observed['comparison_gate_passed']
    assert all(row['status'] == 'FAIL' for row in observed['rows'])
    prior = ROOT / policy['predecessor']['directory']
    load('executed_phase_test', prior / 'check.py').phases_check(policy, original, observed)
    print(json.dumps({'references': len(policy['references']), 'pending_negatives': 5, 'all125FAIL_retained': True, 'actual_clean_original': None, 'live_operations': False}))


if __name__ == '__main__':
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
