import copy
import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def expected_wpt(root, policy):
    kind = policy.get('phase_kind', 'feedback')
    expected = copy.deepcopy(read(root / policy['baseline_capsule']['directory'] / 'POLICY.json')['phases'][kind])
    assert set(expected['phase_revisions']) == {'original'}
    expected['phase_revisions']['candidate'] = policy['head']
    assert kind == 'feedback'
    expected['candidate_required_pass_pages'] = list(expected['expected_subtests'])
    return expected


def phase_policy(settings):
    result = dict(settings, tests=settings['test_types'], held_subtests={})
    result['regression_subtests'] = {page:[name for name in names if name not in settings['target_subtests'].get(page, [])] for page,names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result



def original_metadata(policy):
    base = policy['prepared_application_metadata']
    assert set(base) == {'browser_build_id','entry_identity','entry_type','identity','path','resolved','revision','sha256','symlink_target'}
    assert base['revision'] == policy['wpt']['phase_revisions']['original']
    return dict(base, build_revision=base['revision'], harness_revision=policy['head'], source_role='original')

def replay_original(root, policy, assessor, checks):
    kind = policy.get('phase_kind', 'feedback')
    directory = root / policy['baseline_binding']['directory']
    phase = directory / (kind + '-wpt')
    source = read(root / policy['baseline_capsule']['directory'] / 'POLICY.json')
    assert policy['wpt'] == expected_wpt(root, policy)
    assert source['head'] == policy['head'] and source['controls'] == policy['controls']
    assert source['prepared_application_metadata'] == original_metadata(policy)
    saved_policy = read(phase / 'ASSESSMENT-POLICY.json')
    assert saved_policy == phase_policy(source['phases'][kind])
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    metadata = read(phase / 'APPLICATION-METADATA.json')
    result = read(phase / 'RESULT.json')
    observed = assessor.assess(events, result['exit'], saved_policy, checks, run_binding=metadata)
    assert json.loads(json.dumps(observed)) == read(phase / 'ASSESSMENT.json')
    assert observed['complete'] and not observed['errors'] and result['success'] and result['preservation_verified'] and result['execution_error'] is None
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == read(directory / 'PRE.json') == read(directory / 'POST.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == source['prepared_application_metadata']
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    outer = read(directory / 'RESULT.json')
    assert outer['preservation_verified'] and outer['source_or_canonical_mutation'] is False
    assert outer['phases'][kind] == {'assessment_sha256':sha(phase / 'ASSESSMENT.json'),'raw_sha256':sha(phase / 'raw.jsonl'),'result_sha256':sha(phase / 'RESULT.json')}
    roster = read(directory / (kind.upper() + '-ROSTER.json'))
    assert roster['phase'] == outer['phases'][kind] and roster['owner_sha256'] == policy['baseline_capsule']['sha256']
    assert roster['observed_subtest_count'] == observed['observed_subtest_count'] == 2
    assert roster['expected_subtests'] == {page:[row['subtest'] for row in observed['rows'] if row['test']==page] for page in source['phases'][kind]['expected_subtests']}
    assert roster['endings'] == observed['ends']
    return observed


def replay_all(root, policy):
    here = root / policy['candidate_assessor']
    assessor = load('fresh_feedback_assessor', here)
    checks = load('fresh_feedback_checks', root / policy['wpt']['checks_helper'])
    observed = replay_original(root, policy, assessor, checks)
    assert all(row['status']=='PASS' for row in observed['rows'])
    phases = load('fresh_feedback_records', here.parent / 'phases.py')
    directory = root / policy['baseline_binding']['directory']
    assert read(directory / 'FEEDBACK-RECORDS.json') == phases.feedback_records(root,directory,policy)


def original_directory(root, policy):
    assert policy['phase_kind'] == 'feedback'
    return root / policy['baseline_binding']['directory'] / 'feedback-wpt'
