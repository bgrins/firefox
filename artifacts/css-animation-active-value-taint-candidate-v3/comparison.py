import copy
import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_policy(root, policy):
    directory = root / policy['baseline_capsule']['directory']
    assert sha(directory / 'FILES.json') == policy['baseline_capsule']['sha256']
    assert sha(directory / 'POLICY.json') == policy['original_admission_policy_sha256']
    return read(directory / 'POLICY.json')


def phase_policy(settings):
    result = dict(settings, tests={page: 'testharness' for page in settings['expected_subtests']}, held_subtests={})
    result['regression_subtests'] = {page: [name for name in names if name not in settings['target_subtests'].get(page, [])] for page, names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def expected_wpt(root, policy):
    settings = copy.deepcopy(source_policy(root, policy)['wpt'])
    settings['phase_revisions']['candidate'] = policy['head']
    settings['candidate_required_pass_pages'] = []
    return settings


def admit_snapshot(historical, current):
    expected = copy.deepcopy(historical)
    expected['index']['raw_index'] = current['index']['raw_index']
    assert expected == current


def replay_original(root, policy, assessor, checks):
    source = source_policy(root, policy)
    load('taint_failed_restore', root / policy['owner_directory'] / 'handoff.py').validate(root, policy, source)
    binding = policy['baseline_binding']
    assert binding is not None and policy['wpt'] == expected_wpt(root, policy)
    directory = root / binding['directory']
    assert sha(directory / 'FILES.json') == binding['manifest_sha256']
    assert read(directory / binding['terminal_path']) == binding['terminal'] and binding['terminal']['exit'] == 0
    assert sha(directory / 'RESULT.json') == binding['result_sha256']
    assert binding['terminal']['owner_sha256'] == policy['baseline_capsule']['sha256']
    assert binding['terminal']['result_sha256'] == binding['result_sha256']
    assert binding['terminal']['callbacks_passed'] + binding['terminal']['callbacks_failed'] == policy['wpt']['expected_subtest_count']
    assert binding['terminal']['page_endings_ok'] == policy['wpt']['expected_page_count']
    assert all(binding['terminal'][name] for name in ('raw_replay_verified', 'pre_post_equality_verified', 'current_source_binary_control_pins_verified', 'owned_process_cleanup_verified'))
    result = read(directory / 'RESULT.json')
    assert result['preservation_verified'] and result['lifecycle_complete'] and not result['source_or_canonical_mutation']
    assert not result['native_fix_accepted']
    phase = directory / 'original-wpt'
    for name, key in [('ASSESSMENT.json', 'assessment_sha256'), ('raw.jsonl', 'raw_sha256'), ('RESULT.json', 'result_sha256')]:
        assert sha(phase / name) == result['phase'][key]
    assert read(directory / 'PRE.json') == read(directory / 'POST.json') == read(phase / 'PRE.json') == read(phase / 'POST.json')
    metadata = read(phase / 'APPLICATION-METADATA.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == source['prepared_application_metadata']
    assert {key: value for key, value in metadata.items() if key not in ('build_revision', 'harness_revision', 'source_role', 'entry_identity', 'identity')} == {key: value for key, value in policy['prepared_application_metadata'].items() if key not in ('entry_identity', 'identity')}
    original_settings = read(phase / 'ASSESSMENT-POLICY.json')
    assert original_settings == phase_policy(source['wpt'])
    phase_result = read(phase / 'RESULT.json')
    assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
    build = read(root / policy['original_build']['epoch'])
    assert read(phase / 'BINARY-PINS.json') == {name: build['pins'][name] for name in policy['rebuilt_binaries']}
    assert read(phase / 'CLEANUP.json')['owned_group_absent'] and read(phase / 'CLEANUP.json')['temporary_root_removed']
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    original_assessor = load('progress_original_assessor', root / policy['baseline_capsule']['directory'] / 'assess.py')
    replay = original_assessor.assess(events, phase_result['exit'], original_settings, checks, run_binding=metadata)
    assert replay == read(phase / 'ASSESSMENT.json') and replay['complete'] and len(replay['rows']) == policy['wpt']['expected_subtest_count']
    assert all(row['status'] in ('PASS', 'FAIL') for row in replay['rows'])
    assert result['observation_complete'] and result['all_callbacks_passed'] == all(row['status'] == 'PASS' for row in replay['rows'])
    assert phase_result['exit'] == binding['terminal']['browser_exit']
    assert result['callbacks_passed'] == binding['terminal']['callbacks_passed']
    assert result['callbacks_failed'] == binding['terminal']['callbacks_failed']
    assert result['callbacks_passed'] == sum(row['status'] == 'PASS' for row in replay['rows'])
    assert result['callbacks_failed'] == sum(row['status'] == 'FAIL' for row in replay['rows'])
    projected = assessor.assess(events, phase_result['exit'], phase_policy(policy['wpt']), checks, run_binding=metadata)
    assert projected['complete'] and projected['rows'] == replay['rows'] and projected['ends'] == replay['ends']
    assert projected['run_info'] == replay['run_info'] and projected['run_binding'] == replay['run_binding']
    return projected


def replay_all(root, policy):
    assert policy['wpt'] == expected_wpt(root, policy)
    if policy['baseline_binding'] is not None:
        here = root / policy['owner_directory']
        assessor = load('progress_candidate_assessor', here / 'assess.py')
        checks = load('progress_stream_checks', root / policy['wpt']['checks_helper'])
        return replay_original(root, policy, assessor, checks)
