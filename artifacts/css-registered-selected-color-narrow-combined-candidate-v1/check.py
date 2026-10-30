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
    ownership = load('selected_color_ownership', ROOT / policy['ownership_helper'])
    previous = ROOT / policy['predecessor']['directory']
    ownership.authenticate(previous, policy['predecessor']['manifest_sha256'])
    old = read(previous / 'POLICY.json')
    mutable = {'owner_directory','runtime_output','predecessor','proposal','references','source_paths','execution_enabled','candidate_execution_enabled','activation_pending','head','controls','prepared_application_metadata','prepared_flag_hashes','prepared_flag_capture','execution_handoff','baseline_binding','baseline_capsule','original_admission_policy_sha256','restoration_binding','preparation_predecessor','correction_predecessor','suite_binding','wpt','source_roster','preserved_absent_resources','proposal_independent_review','restoration_handoff','signing_failure'}
    assert {k:v for k,v in policy.items() if k not in mutable} == {k:v for k,v in old.items() if k not in mutable}
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-registered-selected-color-narrow-combined-candidate-runtime-1'
    assert type(policy['execution_enabled']) is bool and policy['execution_enabled'] == policy['candidate_execution_enabled']
    assert bool(policy['activation_pending']) != policy['execution_enabled']
    assert all(policy[k] is not None for k in ('head','controls','prepared_application_metadata','prepared_flag_hashes','prepared_flag_capture','execution_handoff','baseline_binding','baseline_capsule','original_admission_policy_sha256'))
    assert len(policy['accepted_current_payloads']) == 29
    corrected = ROOT / policy['correction_predecessor']['directory']
    ownership.authenticate(corrected, policy['correction_predecessor']['manifest_sha256'])
    assert all((HERE / name).read_bytes() == (corrected / name).read_bytes() for name in ('baseline.py','comparison.py','phases.py','wpt.py','assess.py'))
    assert isinstance(policy['suite_binding'], dict)
    suite = ROOT / policy['suite_binding']['directory']
    ownership.authenticate(suite, policy['suite_binding']['manifest_sha256'])
    inputs = read(suite / 'INPUTS.json')
    original_owner = ROOT / 'artifacts/css-registered-selected-color-original-v2'
    ownership.authenticate(original_owner, policy['references'][str(original_owner.relative_to(ROOT) / 'FILES.json')])
    original_policy = read(original_owner / 'POLICY.json')
    for key in ('suite_binding', 'wpt', 'source_roster', 'preserved_absent_resources'):
        assert policy[key] == original_policy[key], key
    wpt = policy['wpt']
    assert wpt['expected_subtests'] == inputs['roster'] and wpt['resources'] == inputs['resources']
    assert wpt['metadata'] == inputs['metadata']
    assert len(wpt['fixture_target_pages']) == len(set(wpt['fixture_target_pages'])) == 4
    assert set(wpt['fixture_target_pages']) == set(inputs['roster'])
    assert (wpt['expected_subtest_count'], wpt['expected_page_count'], wpt['expected_regression_signature_count']) == (45, 4, 49)
    assert sum(map(len, inputs['roster'].values())) == 45
    assert all(name in policy['preserved_absent_resources'] for name in inputs['new_metadata_absences'])
    for name,pin in policy['references'].items(): assert sha(ROOT / name) == pin, name
    proposal = ROOT / policy['proposal']['directory']
    ownership.authenticate(proposal, policy['proposal']['manifest_sha256'])
    packaging = read(proposal / 'SOURCE-DEPENDENCIES.json')
    proposed = {name: {'base_sha256': role['base_sha256'], 'candidate_sha256': packaging['narrow_postimages'][name]} for name, role in packaging['roles']['A'].items()}
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths'])
    original = 'provider_source_role' in policy
    assert set(roles) == ({'servo/components/style/custom_properties.rs'} if original else set(proposed))
    for name,role in roles.items():
        for kind in ('base','candidate'): assert sha(ROOT / role[kind+'_capture']) == role[kind+'_sha256']
        assert role['base_sha256'] == policy['source_context_pins'][name]
        assert role['candidate_sha256'] == proposed[name]['base_sha256' if original else 'candidate_sha256']
        assert proposed[name]['base_sha256'] == policy['committed_source_preimages'][name]
    assert all((HERE/n).read_bytes()==(previous/n).read_bytes() for n in ('phases.py','wpt.py','assess.py'))
    comparison = load('selected_color_comparison', HERE / 'comparison.py')
    assert policy['wpt'] == comparison.expected_wpt(ROOT, policy)
    validate_actual_bindings(policy)
    return comparison.replay_all(ROOT, policy)


def validate_actual_bindings(policy):
    load('selected_color_pending_admission', HERE / 'admission.py').validate(ROOT,policy)


def check():
    policy = read(HERE / 'POLICY.json')
    actual = validate_policy(policy)
    baseline = load('corrected_terminal_prepare', HERE / 'baseline.py')
    directory = ROOT / policy['baseline_binding']['directory']
    assert baseline.owner_terminal(directory, policy['baseline_binding'], policy['baseline_capsule']) == policy['baseline_binding']['terminal']
    for mode in ('owner', 'terminal', 'exit'):
        binding, capsule = copy.deepcopy(policy['baseline_binding']), copy.deepcopy(policy['baseline_capsule'])
        if mode == 'owner': capsule['sha256'] = '0' * 64
        elif mode == 'terminal': binding['terminal']['terminal_chunk'] = 'invented'
        else: binding['terminal']['exit'] = 1
        try: baseline.owner_terminal(directory, binding, capsule)
        except AssertionError: pass
        else: raise AssertionError('Incorrect terminal schema join accepted')
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    mutations = (
        lambda p: p.update(baseline_binding=None),
        lambda p: p.update(execution_handoff=None),
        lambda p: p.update(head='0' * 40),
        lambda p: p['wpt']['fixture_target_pages'].pop(),
        lambda p: p['baseline_binding'].update(result_sha256='0' * 64),
        lambda p: p['baseline_binding']['terminal'].update(exit=1),
        lambda p: p['execution_handoff'].update(review_sha256='0' * 64),
        lambda p: p['execution_handoff'].update(epoch_refresh_sha256='0' * 64),
        lambda p: p['controls'].update(**{'CURRENT-EPOCH.json': '0' * 64}),
        lambda p: p['prepared_application_metadata'].update(identity=[1,2]),
        lambda p: p['prepared_application_metadata'].update(sha256='0' * 64),
        lambda p: p['prepared_flag_hashes'].update(root='0' * 64),
        lambda p: p['restoration_handoff'].update(manifest_sha256='0' * 64),
        lambda p: p['restoration_handoff'].update(review_sha256='0' * 64),
        lambda p: p.update(restoration_handoff=None),
    )
    for change in mutations:
        bad = copy.deepcopy(policy)
        change(bad)
        try:
            validate_policy(bad)
        except (AssertionError, TypeError, KeyError):
            pass
        else:
            raise AssertionError('invalid actual admission accepted')
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
    assert observed['complete'] and len(observed['rows']) == 45 and not observed['comparison_gate_passed']
    assert all(row['status'] == 'FAIL' for row in observed['rows'])
    prior = ROOT / policy['predecessor']['directory']
    phase_predecessor = ROOT / read(prior / 'POLICY.json')['predecessor']['directory']
    assert (HERE / 'phases.py').read_bytes() == (phase_predecessor / 'phases.py').read_bytes()
    load('executed_phase_test', phase_predecessor / 'check.py').phases_check(policy, original, observed)
    print(json.dumps({'references': len(policy['references']), 'actual_binding_negatives': len(mutations), 'terminal_schema_negatives': 3, 'all45FAIL_retained': True, 'actual_clean_original': {'passed': sum(row['status'] == 'PASS' for row in actual['rows']), 'failed': sum(row['status'] == 'FAIL' for row in actual['rows']), 'endings': len(actual['ends'])}, 'live_operations': False}))


if __name__ == '__main__':
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
