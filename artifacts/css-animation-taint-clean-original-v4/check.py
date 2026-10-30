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
    owner = load('clean_ownership', ROOT / policy['ownership_helper'])
    prior = ROOT / policy['predecessor']['directory']
    owner.authenticate(prior, policy['predecessor']['manifest_sha256'])
    old = read(prior / 'POLICY.json')
    mutable = {'owner_directory', 'runtime_output', 'execution_enabled', 'candidate_execution_enabled',
               'activation_pending', 'baseline_binding', 'baseline_capsule', 'source_paths',
               'restored_application_revision', 'provider_source_role', 'predecessor',
               'restoration_binding', 'prepared_application_metadata', 'controls', 'wpt',
               'closed_process_receipts', 'references', 'suite_binding',
               'preparation_predecessor', 'source_roster', 'preserved_absent_resources', 'correction_predecessor', 'execution_handoff'}
    assert {k: v for k, v in policy.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    correction = policy['correction_predecessor']
    assert correction == {'directory': 'artifacts/css-animation-taint-clean-original-v3', 'manifest_sha256': '5c9994a2569080197ae0cf9dd6f530b1b5965625815c21eed62a872425a1bab3'}
    owner.authenticate(ROOT / correction['directory'], correction['manifest_sha256'])
    assert policy['runtime_output'] == 'artifacts/css-animation-taint-clean-original-runtime-1'
    assert policy['baseline_binding'] is None and policy['baseline_capsule'] is None
    assert policy['provider_source_role'] == 'clean-original'
    validate_handoff(policy)
    assert policy['execution_enabled'] == policy['candidate_execution_enabled']
    if policy['execution_enabled']:
        assert policy['activation_pending'] == []
    else:
        assert policy['activation_pending']
    prep = policy['preparation_predecessor']
    owner.authenticate(ROOT / prep['directory'], prep['manifest_sha256'])
    assert prep['directory'] == 'artifacts/css-animation-taint-clean-original-v1'
    assert prep['manifest_sha256'] == 'a31d80d75df9e231735271fe69b0dc460ac3c54cc7a1bea48e70f3fe834f5bc0'
    suite = policy['suite_binding']
    assert suite is not None and suite['directory'] == 'artifacts/css-animation-taint-clean-suite-v2'
    owner.authenticate(ROOT / suite['directory'], suite['manifest_sha256'])
    load('clean_union_check', ROOT / suite['directory'] / 'check.py').main()
    union = read(ROOT / suite['directory'] / 'INPUTS.json')
    assert policy['source_roster'] == suite['directory'] + '/ROSTER.json'
    assert policy['preserved_absent_resources'] == old['preserved_absent_resources'] + [read(ROOT / union['previous_suite']['directory'] / 'INPUTS.json')['new_metadata_absence'], union['new_metadata_absence']]
    assert policy['restored_application_revision'] == old['wpt']['phase_revisions']['original']
    settings = copy.deepcopy(old['wpt'])
    settings['phase_revisions']['original'] = old['head']
    settings.update(resources=union['resources'], metadata=union['metadata'],
                    manifest={'path': suite['directory'] + '/MANIFEST.json', 'sha256': sha(ROOT / suite['directory'] / 'MANIFEST.json')},
                    expected_subtests=union['roster'], expected_subtest_count=125,
                    expected_control_count=125, expected_page_count=18, expected_regression_signature_count=143)
    settings['fixture_target_pages'] = old['wpt']['fixture_target_pages'] + ['/css/css-variables/animation-taint-registered-same-token.tentative.html', '/css/css-variables/animation-taint-registered-invalid-fallback.tentative.html']
    assert policy['wpt'] == settings
    pages = policy['wpt']['fixture_target_pages']
    assert len(pages) == len(set(pages)) == 18
    assert set(pages) == set(policy['wpt']['expected_subtests'])
    assert settings['expected_subtest_count'] == 125 and settings['expected_page_count'] == 18
    assert settings['target_subtests'] == {} and settings['expected_regression_signature_count'] == 143
    assert len(policy['accepted_current_payloads']) == 29
    for path, digest in policy['references'].items():
        assert sha(ROOT / path) == digest, path
    assert all(policy['references'][path] == digest for path, digest in old['references'].items())
    proposal = ROOT / policy['proposal']['directory']
    owner.authenticate(proposal, policy['proposal']['manifest_sha256'])
    clean = read(proposal / 'CLEAN-PROVIDER.json')
    roles = read(HERE / 'SOURCE-ROLES.json')
    name = 'servo/components/style/custom_properties.rs'
    assert set(roles) == set(policy['source_paths']) == {name}
    expected = dict(read(prior / 'SOURCE-ROLES.json')[name], candidate_capture=clean['base_capture'], candidate_sha256=clean['base_sha256'])
    assert roles[name] == expected
    for kind in ('base', 'candidate'):
        assert sha(ROOT / expected[kind + '_capture']) == expected[kind + '_sha256']
    assert expected['candidate_sha256'] == policy['committed_source_preimages'][name]
    load('prior_lineage', prior / 'check.py').validate_lineage(old, read(prior / 'SOURCE-ROLES.json'))
    binding = policy['restoration_binding']
    directory = ROOT / binding['directory']
    assert binding['directory'] == 'artifacts/css-animation-active-value-taint-candidate-runtime-3'
    assert binding['manifest_sha256'] == '28ad738e114cafedb9950c911a69a95c45f25514716d4b6cf047d06921b1b00f'
    owner.authenticate(directory, binding['manifest_sha256'])
    terminal = read(directory / 'ROOT-TERMINAL.json')
    review = read(directory / 'ROOT-REVIEW.json')
    refresh = read(directory / 'ROOT-EPOCH-REFRESH.json')
    result = read(directory / 'CANDIDATE-RESULT.json')
    assert (terminal['owner_session'], terminal['owner_terminal'], terminal['owner_exit']) == (13008, 'a00618', 0)
    assert (terminal['review_session'], terminal['review_terminal'], terminal['review_exit']) == (95388, 'a854aa', 0)
    assert terminal['review_sha256'] == sha(directory / 'ROOT-REVIEW.json') == refresh['independent_review_sha256']
    assert review['owner_manifest_sha256'] == policy['predecessor']['manifest_sha256']
    assert review['actual_terminal'] == {'exit': 0, 'session': 13008, 'terminal_chunk': 'a00618', 'result_sha256': sha(directory / 'CANDIDATE-RESULT.json')}
    assert result == review['owner_result'] and result['success'] and result['restoration_verified']
    assert not result['native_fix_acceptance'] and not review['native_acceptance']
    assert review['restoration_independently_verified'] and review['backup'] == read(directory / 'BACKUP-CLEANUP.json')
    assert review['backup']['removed'] and review['backup']['verified_original_restoration'] and not review['backup']['retained_after_failure']
    assert review['snapshot'] == read(directory / 'POST.json')
    before = read(directory / 'CANDIDATE-PRE.json')['snapshot']
    projected = copy.deepcopy(before)
    projected['index']['raw_index'] = refresh['raw_index_after']
    assert projected == review['snapshot']
    assert refresh['previous_epoch_sha256'] == old['controls']['CURRENT-EPOCH.json']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['semantic_index_unchanged']
    assert refresh['raw_index_before'] == before['index']['raw_index']
    assert refresh['raw_index_after'] == review['snapshot']['index']['raw_index']
    assert policy['controls'] == dict(old['controls'], **{'CURRENT-EPOCH.json': refresh['new_epoch_sha256']})
    assert refresh['other_controls_unchanged'] == {k: v for k, v in old['controls'].items() if k != 'CURRENT-EPOCH.json'}
    assert policy['prepared_application_metadata'] == review['restored_application_metadata']
    strip = lambda m: {k: v for k, v in m.items() if k not in ('entry_identity', 'identity')}
    assert strip(policy['prepared_application_metadata']) == strip(old['prepared_application_metadata'])
    for path, row in read(prior / 'SOURCE-ROLES.json').items():
        assert review['source_identities'][path] == {'sha256': row['base_sha256'], 'identity': read(ROOT / policy['source_equivalence']['path'])['sources'][path]['identity']}
    outcomes = read(directory / 'OUTCOMES.json')
    assert outcomes == review['observation']['outcomes']
    assert (outcomes['callbacks_passed'], outcomes['callbacks_failed']) == (119, 1)
    assert not outcomes['all_callbacks_passed'] and not outcomes['comparison_gate_passed']
    assert review['observation']['observation_complete'] and review['observation']['browser_exit'] == 1
    assert policy['closed_process_receipts'] == old['closed_process_receipts'] + [str(directory.relative_to(ROOT) / p) for p in ('candidate-build/build-PROCESS.json', 'candidate-build/WAKE-PROCESS.json', 'candidate-wpt/PROCESS.json')]
    assert read(ROOT / policy['prepared_flag_capture']['path']) == policy['prepared_flag_hashes']



def validate_handoff(policy, outcome=None, current=None):
    binding = policy['execution_handoff']
    assert isinstance(binding, dict) and set(binding) == {'root_outcome', 'current', 'signer_result', 'signing_log'}
    for row in binding.values():
        assert set(row) == {'path', 'sha256'}
        assert policy['references'][row['path']] == sha(ROOT / row['path']) == row['sha256']
    assert binding['root_outcome']['sha256'] == '288832ce6205405e5fd558c93684a53978ebabbc475602c266bbd933c749f529'
    assert binding['current']['sha256'] == '18ad29e77ff7481e2e8847475524b6d1de19ac43c933b27d6858b191277ed4be'
    observed = read(ROOT / binding['root_outcome']['path']) if outcome is None else outcome
    state = read(ROOT / binding['current']['path']) if current is None else current
    result = read(ROOT / binding['signer_result']['path'])
    assert (observed['session_id'], observed['terminal_chunk'], observed['owner_exit'], observed['git_exit']) == (75764, '8969a1', 1, 128)
    assert observed['committed'] is False and observed['head'] == policy['head']
    assert observed['result_sha256'] == binding['signer_result']['sha256']
    assert observed['signing_log_sha256'] == binding['signing_log']['sha256']
    assert observed['signature_error'] == '1Password: failed to fill whole buffer'
    assert observed['signature_error'] in (ROOT / binding['signing_log']['path']).read_text()
    assert result == {'committed': False, 'exit': 128, 'real_index_and_canonical_state_unchanged': True}
    assert all(observed[k] is True for k in ('head_unchanged', 'raw_index_unchanged', 'controls_unchanged', 'staging_empty', 'full_porcelain_status_unchanged', 'source_transition_lock_absent', 'owned_temporary_index_removed', 'owner_full_current_state_verification_completed'))
    assert (observed['project_bodies_preserved'], observed['unrelated_metadata_preserved']) == (68, 495)
    review = read(ROOT / policy['restoration_binding']['directory'] / 'ROOT-REVIEW.json')
    assert state['audit'] == review['snapshot']
    assert state['controls'] == policy['controls']
    assert state['source_transition_lock_absent'] is True and state['full_current_state_verified'] is True
    assert state['audit']['index']['head'] == observed['head']
    assert state['observed_at'] < observed['observed_at']


def check():
    policy = read(HERE / 'POLICY.json')
    validate_policy(policy)
    for change in (
        lambda p: p['wpt']['phase_revisions'].update(original=p['restored_application_revision']),
        lambda p: p['controls'].update({'CURRENT-EPOCH.json': '0' * 64}),
        lambda p: p['prepared_application_metadata'].update(sha256='0' * 64),
        lambda p: p['prepared_application_metadata'].update(identity=[1, 2]),
        lambda p: p.update(provider_source_role='held-original'),
        lambda p: p.update(source_paths=[]),
        lambda p: p.update(preserved_absent_resources=[]),
        lambda p: p['wpt'].update(expected_subtest_count=120),
        lambda p: p['wpt']['fixture_target_pages'].remove('/css/css-variables/animation-taint-registered-same-token.tentative.html'),
        lambda p: p['wpt']['fixture_target_pages'].append(p['wpt']['fixture_target_pages'][0]),
        lambda p: p['wpt']['fixture_target_pages'].remove('/css/css-variables/animation-taint-registered-invalid-fallback.tentative.html'),
        lambda p: p.update(execution_handoff={'unverified': True}),
        lambda p: p.update(execution_enabled=True, candidate_execution_enabled=False, activation_pending=[]),
    ):
        bad = copy.deepcopy(policy)
        change(bad)
        try:
            validate_policy(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('invalid clean-original binding admitted')
    handoff = policy['execution_handoff']
    actual = read(ROOT / handoff['root_outcome']['path'])
    for key, value in [('committed', True), ('owner_exit', 0), ('head', '0' * 40), ('controls_unchanged', False)]:
        bad = copy.deepcopy(actual)
        bad[key] = value
        try:
            validate_handoff(policy, outcome=bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('incorrect signing handoff admitted')
    bad_state = read(ROOT / handoff['current']['path'])
    bad_state['audit']['index']['raw_index'] = '0' * 64
    try:
        validate_handoff(policy, current=bad_state)
    except AssertionError:
        pass
    else:
        raise AssertionError('incorrect current snapshot admitted')
    assessor = load('clean_assessor', HERE / 'assess.py')
    checks = load('clean_stream_checks', ROOT / policy['wpt']['checks_helper'])
    projection = load('phase_projection', ROOT / policy['predecessor']['directory'] / 'comparison.py')
    settings = copy.deepcopy(policy['wpt'])
    app = dict(policy['prepared_application_metadata'], revision=policy['head'], build_revision=policy['head'], harness_revision=policy['head'], source_role='original')
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False, 'browser_build_id': app['browser_build_id'], 'revision': policy['head']}}]
    for page, names in settings['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': page})
        events.extend({'action': 'test_status', 'test': page, 'subtest': name, 'status': 'FAIL', 'expected': 'PASS', 'message': 'synthetic ordinary assertion'} for name in names)
        events.append({'action': 'test_end', 'test': page, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    observed = assessor.assess(events, 1, projection.phase_policy(settings), checks, run_binding=app)
    assert observed['complete'] and len(observed['rows']) == 125 and all(r['status'] == 'FAIL' for r in observed['rows'])
    assert len(observed['ends']) == 18
    setup = copy.deepcopy(events)
    new_page = '/css/css-variables/animation-taint-registered-invalid-fallback.tentative.html'
    bad_row = next(row for row in setup if row.get('action') == 'test_status' and row.get('test') == new_page)
    bad_row['message'] = 'ReferenceError: syntheticMissingFunction is not defined'
    rejected = assessor.assess(setup, 1, projection.phase_policy(settings), checks, run_binding=app)
    assert not rejected['complete'] and len(rejected['fixture_setup_errors']) == 1
    assert rejected['fixture_setup_errors'] == [assessor.signature(bad_row)]
    assert 'new target fixture has an uncaught setup/runtime exception' in rejected['errors']
    old_gap = copy.deepcopy(settings)
    old_gap['fixture_target_pages'].remove(new_page)
    missed = assessor.assess(setup, 1, projection.phase_policy(old_gap), checks, run_binding=app)
    assert missed['complete'] and missed['fixture_setup_errors'] == []
    import tempfile
    phases = load('clean_phase_check', HERE / 'phases.py')
    with tempfile.TemporaryDirectory(prefix='css-clean-original-phase-', dir='/private/tmp') as temp:
        scratch = Path(temp)
        phase = scratch / 'original-wpt'
        phase.mkdir()
        (scratch / 'original-build').mkdir()
        save = lambda p, value: p.write_text(json.dumps(value))
        snapshot = {'synthetic': True}
        for name in ('PRE.json', 'POST.json'):
            save(phase / name, snapshot)
        for name in ('APPLICATION-METADATA.json', 'APPLICATION-METADATA-POST.json'):
            save(phase / name, app)
        save(phase / 'ASSESSMENT.json', observed)
        save(phase / 'BINARY-PINS.json', {'synthetic': 'binary'})
        save(scratch / 'SOURCE-ROLES.json', read(HERE / 'SOURCE-ROLES.json'))
        save(scratch / 'original-build/RESULT.json', {'binaries': {'synthetic': 'binary'}, 'native_sources': {k: v['candidate_sha256'] for k, v in read(HERE / 'SOURCE-ROLES.json').items()}})
        (scratch / 'wpt.py').write_text('import json\ndef save(p, v): p.write_text(json.dumps(v))\ndef run(*args): return {"synthetic": "complete observation"}\n')
        assert phases.run(ROOT, scratch, scratch, policy, {}, lambda: snapshot, {}, lambda: False) == {'synthetic': 'complete observation'}
        result = read(scratch / 'OUTCOMES.json')
        assert result['callbacks_failed'] == 125 and result['callbacks_passed'] == 0
        assert not result['native_acceptance'] and len(result['endings']) == 18
    assert not scratch.exists()
    print(json.dumps({'references': len(policy['references']), 'binding_negatives': 13, 'signing_handoff_negatives': 5, 'new_page_ReferenceError_rejected': True, 'old_gap_reproduced_synthetically': True, 'all_125_FAIL_retained': True, 'phase_failure_retention': True, 'scratch_removed': True, 'live_operations': False}))


if __name__ == '__main__':
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
