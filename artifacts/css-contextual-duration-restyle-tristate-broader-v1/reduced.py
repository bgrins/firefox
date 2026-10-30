import copy
import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def joined_source_pins(policy,roles):
    pins = dict(policy['source_context_pins'])
    for name,record in roles.items():
        if name in pins:
            assert pins[name] == record['base_sha256']
        pins[name] = record['base_sha256']
    return pins


def expected_wpt(root,policy):
    source = read(root / policy['reduced_capsule']['directory'] / 'POLICY.json')
    expected = copy.deepcopy(source['wpt'])
    assert set(expected['phase_revisions']) == {'original'}
    expected['phase_revisions']['candidate'] = policy['head']
    expected['test_types'] = {page:'testharness' for page in expected['expected_subtests']}
    expected['phase_kind'] = 'reduced'
    assert expected['candidate_required_pass_pages'] == list(expected['expected_subtests'])
    return expected


def replay_original(root,policy,assessor,checks):
    binding = policy['reduced_binding']
    assert binding is not None and policy['wpt'] == expected_wpt(root,policy)
    owner = root / policy['reduced_capsule']['directory']
    source = read(owner / 'POLICY.json')
    directory = root / binding['directory']
    phase = directory / 'original-wpt'
    assert read(directory / binding['terminal_path']) == binding['terminal']
    terminal = binding['terminal']
    assert terminal['session_id'] == 68662 and terminal['terminal_chunk'] == '634d07' and terminal['exit'] == 0
    assert terminal['owner_sha256'] == policy['reduced_capsule']['sha256']
    assert terminal['result_sha256'] == binding['result_sha256']
    assert terminal['raw_replay_verified'] and terminal['state_and_application_preservation_independently_verified']
    assert terminal['callbacks_passed'] == 2 and terminal['ending'] == 'OK' and terminal['fixed_controls_passed']
    assert terminal['native_acceptance'] is False and terminal['matching_only_or_combined_reduced_validation_performed'] is False
    assert terminal['epoch_sha256'] == policy['controls']['CURRENT-EPOCH.json']
    assert terminal['raw_index'] == read(phase / 'PRE.json')['index']['raw_index']
    assert sha(directory / 'RESULT.json') == binding['result_sha256']
    settings = source['wpt']
    expected = dict(settings,tests={page:'testharness' for page in settings['expected_subtests']},held_subtests={})
    expected['regression_subtests'] = {page:[name for name in names if name not in settings['target_subtests'].get(page,[])] for page,names in settings['expected_subtests'].items()}
    expected['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    assert read(phase / 'ASSESSMENT-POLICY.json') == expected
    original_assessor = load('reduced_original_assessor',owner / 'assess.py')
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    result = read(phase / 'RESULT.json')
    metadata = read(phase / 'APPLICATION-METADATA.json')
    observed = original_assessor.assess(events,result['exit'],expected,checks,run_binding=metadata)
    assert json.loads(json.dumps(observed)) == read(phase / 'ASSESSMENT.json')
    assert observed['complete'] and not observed['errors'] and len(observed['rows']) == 2
    assert all(row['status'] == 'PASS' for row in observed['rows']) and result['exit'] == 0
    assert result['success'] and result['preservation_verified'] and result['execution_error'] is None
    assert read(phase / 'PRE.json') == read(phase / 'POST.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == source['prepared_application_metadata']
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    outer = read(directory / 'RESULT.json')
    assert outer['preservation_verified'] and outer['source_or_canonical_mutation'] is False and outer['native_fix_accepted'] is False
    assert outer['phase'] == {key:sha(phase / filename) for key,filename in [('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl'),('result_sha256','RESULT.json')]}
    roster = read(directory / 'OBSERVED-ROSTER.json')
    assert roster['phase'] == outer['phase'] and roster['owner_sha256'] == policy['reduced_capsule']['sha256']
    assert roster['expected_subtests'] == settings['expected_subtests'] and roster['observed_subtest_count'] == 2
    assert roster['source_roster_sha256'] == source['references'][source['source_roster']]
    assert source['head'] == settings['harness_revision'] == policy['head']
    assert source['controls'] == policy['controls']
    assert source['rebuilt_binaries'] == policy['rebuilt_binaries']
    assert source['build_epoch'] == policy['original_build']['epoch']
    roles = read((root / policy['candidate_assessor']).parent / 'SOURCE-ROLES.json')
    assert source['source_role_pins'] == joined_source_pins(policy,roles)
    annotations = {'build_revision','harness_revision','source_role'}
    assert {k:v for k,v in metadata.items() if k not in annotations} == policy['prepared_application_metadata']
    assert metadata['revision'] == metadata['build_revision'] == policy['wpt']['phase_revisions']['original']
    assert metadata['harness_revision'] == policy['head'] and metadata['source_role'] == 'original'
    return observed


def replay_all(root,policy):
    current = dict(policy,wpt=policy['phases']['reduced'],phase_kind='reduced')
    assessor = load('broader_assessor',root / policy['candidate_assessor'])
    checks = load('broader_checks',root / current['wpt']['checks_helper'])
    replay_original(root,current,assessor,checks)
    comparison = load('broader_snapshot_comparison',(root / policy['candidate_assessor']).parent / 'comparison.py')
    original = root / policy['baseline_binding']['directory']
    reduced = root / policy['reduced_binding']['directory'] / 'original-wpt'
    comparison.admit_snapshot(read(original / 'POST.json'),read(reduced / 'PRE.json'))
