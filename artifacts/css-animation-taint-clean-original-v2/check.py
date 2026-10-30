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
               'preparation_predecessor', 'source_roster', 'preserved_absent_resources'}
    assert {k: v for k, v in policy.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-animation-taint-clean-original-runtime-1'
    assert policy['baseline_binding'] is None and policy['baseline_capsule'] is None
    assert policy['provider_source_role'] == 'clean-original'
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
    assert suite is not None and suite['directory'] == 'artifacts/css-animation-taint-clean-suite-v1'
    owner.authenticate(ROOT / suite['directory'], suite['manifest_sha256'])
    load('clean_union_check', ROOT / suite['directory'] / 'check.py').main()
    union = read(ROOT / suite['directory'] / 'INPUTS.json')
    assert policy['source_roster'] == suite['directory'] + '/ROSTER.json'
    assert policy['preserved_absent_resources'] == old['preserved_absent_resources'] + [union['new_metadata_absence']]
    assert policy['restored_application_revision'] == old['wpt']['phase_revisions']['original']
    settings = copy.deepcopy(old['wpt'])
    settings['phase_revisions']['original'] = old['head']
    settings.update(resources=union['resources'], metadata=union['metadata'],
                    manifest={'path': suite['directory'] + '/MANIFEST.json', 'sha256': sha(ROOT / suite['directory'] / 'MANIFEST.json')},
                    expected_subtests=union['roster'], expected_subtest_count=123,
                    expected_control_count=123, expected_page_count=17, expected_regression_signature_count=140)
    assert policy['wpt'] == settings
    assert settings['expected_subtest_count'] == 123 and settings['expected_page_count'] == 17
    assert settings['target_subtests'] == {} and settings['expected_regression_signature_count'] == 140
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
    ):
        bad = copy.deepcopy(policy)
        change(bad)
        try:
            validate_policy(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('invalid clean-original binding admitted')
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
    assert observed['complete'] and len(observed['rows']) == 123 and all(r['status'] == 'FAIL' for r in observed['rows'])
    assert len(observed['ends']) == 17
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
        assert result['callbacks_failed'] == 123 and result['callbacks_passed'] == 0
        assert not result['native_acceptance'] and len(result['endings']) == 17
    assert not scratch.exists()
    print(json.dumps({'references': len(policy['references']), 'binding_negatives': 8, 'all_123_FAIL_retained': True, 'phase_failure_retention': True, 'scratch_removed': True, 'live_operations': False}))


if __name__ == '__main__':
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
