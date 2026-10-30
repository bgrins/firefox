import copy
import hashlib
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def expected_wpt(root, policy):
    expected = copy.deepcopy(read(root / policy['baseline_capsule']['directory'] / 'POLICY.json')['wpt'])
    assert set(expected['phase_revisions']) == {'original'}
    expected['phase_revisions']['candidate'] = policy['head']
    assert sum(map(len, expected['expected_subtests'].values())) == 578
    assert sum(map(len, expected['target_subtests'].values())) == 33
    assert sum(len(expected['expected_subtests'][page]) for page in expected['candidate_required_pass_pages']) == 60
    return expected


def phase_policy(settings):
    result = dict(settings, tests={page:'testharness' for page in settings['expected_subtests']}, held_subtests={})
    result['regression_subtests'] = {page:[name for name in names if name not in settings['target_subtests'].get(page, [])]
                                    for page,names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def replay_original(root, policy, assessor, checks):
    binding = policy['baseline_binding']
    assert binding is not None
    directory = root / binding['directory']
    phase = directory / 'original-wpt'
    capsule = root / policy['baseline_capsule']['directory']
    assert sha(capsule / 'assess.py') == sha(root / policy['candidate_assessor'])
    original_policy = read(capsule / 'POLICY.json')
    assert policy['wpt'] == expected_wpt(root, policy)
    saved_policy = read(phase / 'ASSESSMENT-POLICY.json')
    assert saved_policy == phase_policy(original_policy['wpt'])
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    metadata = read(phase / 'APPLICATION-METADATA.json')
    result = read(phase / 'RESULT.json')
    observed = assessor.assess(events, result['exit'], saved_policy, checks, run_binding=metadata)
    assert json.loads(json.dumps(observed)) == read(phase / 'ASSESSMENT.json')
    assert observed['complete'] and not observed['errors'] and result['success'] and result['preservation_verified']
    assert read(phase / 'PRE.json') == read(phase / 'POST.json')
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == original_policy['prepared_application_metadata']
    outer = read(directory / 'RESULT.json')
    assert outer['preservation_verified'] and outer['source_or_canonical_mutation'] is False
    assert outer['phase'] == {'assessment_sha256':sha(phase / 'ASSESSMENT.json'),
                              'raw_sha256':sha(phase / 'raw.jsonl'), 'result_sha256':sha(phase / 'RESULT.json')}
    roster = read(directory / 'OBSERVED-ROSTER.json')
    assert roster['phase'] == outer['phase'] and roster['owner_sha256'] == policy['baseline_capsule']['sha256']
    assert roster['source_roster_sha256'] == original_policy['references'][original_policy['source_roster']]
    assert roster['observed_subtest_count'] == 578 and observed['observed_subtest_count'] == 578
    for page,names in roster['expected_subtests'].items():
        assert names == [row['subtest'] for row in observed['rows'] if row['test'] == page]
        assert set(names) == set(policy['wpt']['expected_subtests'][page])
    assert set(roster['expected_subtests']) == set(policy['wpt']['expected_subtests'])
    return observed


def replay_combined(root, policy, assessor, checks):
    binding = policy['combined_binding']
    directory = root / binding['directory']
    terminal = read(directory / binding['terminal_path'])
    assert terminal == binding['terminal'] and terminal['exit'] == 0
    outer = read(directory / 'CANDIDATE-RESULT.json')
    assert sha(directory / 'CANDIDATE-RESULT.json') == binding['result_sha256'] == terminal['result_sha256']
    assert outer['success'] and outer['restoration_verified'] and outer['runtime_controls_unchanged']
    assert outer['error'] is None and not outer['publication_errors']
    owner = root / binding['owner']['directory']
    assert sha(owner / 'FILES.json') == binding['owner']['sha256']
    prior_policy = read(owner / 'POLICY.json')
    assert prior_policy['wpt'] == policy['wpt']
    roles = read(owner / 'SOURCE-ROLES.json')
    calc = 'servo/components/style/values/generics/calc.rs'
    assert roles[calc]['candidate_sha256'] == policy['combined_source_sha256']
    provider = 'servo/components/style/custom_properties.rs'
    build_epoch = read(root / prior_policy['original_build']['epoch'])
    assert build_epoch['pins'][provider] == policy['held_provider_sha256']
    build = read(directory / 'candidate-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert build['native_sources'] == {calc: policy['combined_source_sha256']}
    inner = read(directory / 'candidate-build/build-RESULT.json')
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assert inner['error'] is None and inner['stop_reason'] is None
    phase = directory / 'candidate-wpt'
    assert read(phase / 'BINARY-PINS.json') == build['binaries']
    assert outer['candidate_phase'] == {'assessment_sha256':sha(phase / 'ASSESSMENT.json'),
                                        'raw_sha256':sha(phase / 'raw.jsonl'), 'result_sha256':sha(phase / 'RESULT.json')}
    saved_policy = read(phase / 'ASSESSMENT-POLICY.json')
    assert saved_policy == phase_policy(policy['wpt'])
    metadata = read(phase / 'APPLICATION-METADATA.json')
    result = read(phase / 'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['comparison_gate_passed']
    assert read(phase / 'PRE.json') == read(phase / 'POST.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    original = replay_original(root, policy, assessor, checks)
    observed = assessor.assess(events, result['exit'], saved_policy, checks, original=original, run_binding=metadata)
    assert json.loads(json.dumps(observed)) == read(phase / 'ASSESSMENT.json')
    assert observed['complete'] and observed['comparison_gate_passed'] and not observed['errors']
    restored = read(directory / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    assert restored['sources'][calc]['sha256'] == roles[calc]['base_sha256']
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    return observed


def require_equal_results(reference, candidate, assessor):
    assert reference['complete'] and reference['comparison_gate_passed']
    assert candidate['complete'] and candidate['comparison_gate_passed']
    for kind, count in [('rows', 578), ('ends', 16)]:
        assert len(reference[kind]) == len(candidate[kind]) == count
        signatures = lambda result: sorted(json.dumps(assessor.signature(event), sort_keys=True) for event in result[kind])
        assert signatures(reference) == signatures(candidate), kind + ' differ from the with-provider result'
