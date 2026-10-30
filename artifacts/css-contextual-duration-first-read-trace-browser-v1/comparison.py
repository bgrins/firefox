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
    settings['candidate_required_pass_pages'] = list(settings['expected_subtests'])
    binding = policy['baseline_binding']
    if binding is not None:
        saved = read(root / binding['directory'] / 'original-wpt/ASSESSMENT.json')
        settings['target_subtests'] = {page: [row['subtest'] for row in saved['rows'] if row['test'] == page and row['status'] == 'FAIL'] for page in settings['expected_subtests']}
        count = sum(map(len, settings['target_subtests'].values()))
        settings['expected_target_count'] = count
        settings['expected_control_count'] = 9 - count
        settings['expected_regression_signature_count'] = 12 - count
    return settings


def admit_snapshot(historical, current):
    expected = copy.deepcopy(historical)
    expected['index']['raw_index'] = current['index']['raw_index']
    assert expected == current


def replay_original(root, policy, assessor, checks):
    source = source_policy(root, policy)
    binding = policy['baseline_binding']
    assert binding is not None and policy['wpt'] == expected_wpt(root, policy)
    directory = root / binding['directory']
    assert sha(directory / 'FILES.json') == binding['manifest_sha256']
    assert read(directory / binding['terminal_path']) == binding['terminal'] and binding['terminal']['exit'] == 0
    assert sha(directory / 'RESULT.json') == binding['result_sha256']
    assert binding['terminal']['owner_sha256'] == policy['baseline_capsule']['sha256']
    assert binding['terminal']['result_sha256'] == binding['result_sha256']
    assert (binding['terminal']['session_id'], binding['terminal']['terminal_chunk'], binding['terminal']['exit']) == (84260, 'c64017', 0)
    assert (binding['terminal']['callbacks_passed'], binding['terminal']['callbacks_failed'], binding['terminal']['page_endings_ok'], binding['terminal']['complete_records']) == (4, 5, 3, 9)
    assert all(binding['terminal'][name] for name in ('raw_replay_verified', 'pre_post_equality_verified', 'current_source_binary_control_pins_verified', 'private_records_independently_validated', 'owned_process_cleanup_verified'))
    result = read(directory / 'RESULT.json')
    assert result['preservation_verified'] and result['lifecycle_complete'] and not result['source_or_canonical_mutation']
    assert not result['native_fix_accepted']
    phase = directory / 'original-wpt'
    for name, key in [('ASSESSMENT.json', 'assessment_sha256'), ('raw.jsonl', 'raw_sha256'), ('RESULT.json', 'result_sha256')]:
        assert sha(phase / name) == result['phase'][key]
    assert read(directory / 'PRE.json') == read(directory / 'POST.json') == read(phase / 'PRE.json') == read(phase / 'POST.json')
    metadata = read(phase / 'APPLICATION-METADATA.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == source['prepared_application_metadata']
    if policy['prepared_application_metadata'] is not None:
        historical = {key: value for key, value in metadata.items() if key not in ('build_revision', 'harness_revision', 'source_role', 'identity', 'entry_identity')}
        assert historical == {key: value for key, value in policy['prepared_application_metadata'].items() if key not in ('identity', 'entry_identity')}
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
    assert replay == read(phase / 'ASSESSMENT.json') and replay['complete'] and len(replay['rows']) == 9
    assert all(row['status'] in ('PASS', 'FAIL') for row in replay['rows'])
    collection = load('progress_original_records', root / policy['baseline_capsule']['directory'] / 'records.py').collect(root, directory / 'progress-records', read(directory / 'PROGRESS-BINDING.json'), source, replay)
    assert collection == read(directory / 'PROGRESS-RECORDS.json') and not collection['errors']
    assert result['records_complete'] == result['observation_complete'] == collection['complete']
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


def replay_uninstrumented(root, policy):
    binding = policy['uninstrumented_reference']
    directory = root / binding['directory']
    assert sha(directory / 'FILES.json') == binding['manifest_sha256']
    assert sha(directory / binding['terminal_path']) == binding['terminal_sha256']
    terminal = read(directory / binding['terminal_path'])
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (8127, 'bef82f', 0)
    assert terminal['state_and_application_restoration_independently_verified'] and terminal['raw_replay_verified']
    assert (terminal['callbacks_passed'], terminal['callbacks_failed'], terminal['page_endings_ok']) == (9, 0, 3)
    old_dir = root / 'artifacts/css-contextual-duration-progress-candidate-v1'
    assert sha(old_dir / 'FILES.json') == terminal['owner_sha256']
    old_policy = read(old_dir / 'POLICY.json')
    old_comparison = load('uninstrumented_progress_comparison', old_dir / 'comparison.py')
    original = old_comparison.replay_all(root, old_policy)
    assessor = load('uninstrumented_progress_assessor', old_dir / 'assess.py')
    checks = load('uninstrumented_progress_streams', root / old_policy['wpt']['checks_helper'])
    phase = directory / 'candidate-wpt'
    result = read(directory / 'CANDIDATE-RESULT.json')
    assert sha(directory / 'CANDIDATE-RESULT.json') == terminal['result_sha256']
    assert result['success'] and result['restoration_verified'] and result['error'] is None
    for name, key in [('ASSESSMENT.json', 'assessment_sha256'), ('raw.jsonl', 'raw_sha256'), ('RESULT.json', 'result_sha256')]:
        assert sha(phase / name) == result['candidate_phase'][key]
    settings = read(phase / 'ASSESSMENT-POLICY.json')
    assert settings == phase_policy(old_policy['wpt'])
    assert old_policy['wpt']['resources'] == policy['wpt']['resources']
    assert old_policy['wpt']['expected_subtests'] == policy['wpt']['expected_subtests']
    metadata = read(phase / 'APPLICATION-METADATA.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    assert read(phase / 'PRE.json') == read(phase / 'POST.json')
    build = read(directory / 'candidate-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert read(phase / 'BINARY-PINS.json') == build['binaries']
    semantic = read(root / policy['landing_package']['directory'] / 'PAYLOADS.json')
    assert build['native_sources'] == {name: row['candidate_sha256'] for name, row in semantic.items() if name in old_policy['source_paths']}
    raw = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    replay = assessor.assess(raw, read(phase / 'RESULT.json')['exit'], settings, checks, original=original, run_binding=metadata)
    assert replay == read(phase / 'ASSESSMENT.json') and replay['comparison_gate_passed']
    collection = load('uninstrumented_progress_records', old_dir / 'records.py').collect(root, directory / 'progress-records', read(directory / 'PROGRESS-BINDING.json'), old_policy, replay)
    assert collection == read(directory / 'PROGRESS-RECORDS.json') and collection['complete'] and not collection['errors']
    return replay


def compare_uninstrumented(root, policy, current):
    previous = replay_uninstrumented(root, policy)
    assessor = load('first_read_signature', root / policy['owner_directory'] / 'assess.py')
    signatures = lambda value: sorted((assessor.signature(row) for row in value['rows'] + value['ends']), key=lambda row: (row['test'], row['kind'], row['subtest'] or ''))
    return {'full_callback_and_ending_signatures_equal': signatures(previous) == signatures(current), 'expected_callbacks': 9, 'expected_endings': 3, 'first_read_phase_alignment_established': False, 'numeric_first_samples_required_equal': False}
