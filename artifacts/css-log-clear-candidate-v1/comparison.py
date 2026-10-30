import copy
import hashlib
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def expected_wpt(root, policy):
    expected = copy.deepcopy(read(root / policy['baseline_capsule']['directory'] / 'POLICY.json')['wpt'])
    assert set(expected['phase_revisions']) == {'original'}
    expected['phase_revisions']['candidate'] = policy['head']
    assert sum(map(len, expected['expected_subtests'].values())) == 102
    assert sum(map(len, expected['target_subtests'].values())) == 15
    assert sum(len(expected['expected_subtests'][page]) for page in expected['candidate_required_pass_pages']) == 24
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
    assert roster['observed_subtest_count'] == 102 and observed['observed_subtest_count'] == 102
    for page,names in roster['expected_subtests'].items():
        assert names == [row['subtest'] for row in observed['rows'] if row['test'] == page]
        assert set(names) == set(policy['wpt']['expected_subtests'][page])
    assert set(roster['expected_subtests']) == set(policy['wpt']['expected_subtests'])
    return observed
