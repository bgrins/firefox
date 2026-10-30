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
    settings['target_subtests'] = copy.deepcopy(settings['expected_subtests'])
    settings.update(expected_target_count=4, expected_control_count=0, expected_regression_signature_count=1)
    binding = policy['baseline_binding']
    if binding is not None:
        saved = read(root / binding['directory'] / 'original-wpt/ASSESSMENT.json')
        settings['target_subtests'] = {page: [row['subtest'] for row in saved['rows'] if row['test'] == page and row['status'] == 'FAIL'] for page in settings['expected_subtests']}
        count = sum(map(len, settings['target_subtests'].values()))
        settings['expected_target_count'] = count
        settings['expected_control_count'] = 4 - count
        settings['expected_regression_signature_count'] = 5 - count
    return settings


def admit_snapshot(historical, current):
    expected = copy.deepcopy(historical)
    expected['index']['raw_index'] = current['index']['raw_index']
    assert expected == current


def require_complete_collection(collection, terminal):
    assert collection['complete'] and not collection['errors'] and not collection['missing']
    assert len(collection['records']) == terminal['complete_records'] == 4


def expected_snapshot(depth, advanced):
    value = 32 if advanced else 16
    nodes = []
    def timing(duration):
        return {'duration': duration, 'progress': 1 if duration == 1000 else 0.75, 'time': 1500, 'state': 'paused'}
    for index in range(depth):
        duration = value * 1000 // 16
        output = 48 - value
        nodes.append({'font': value if index % 2 == 0 else output,
                      'lineHeight': output if index % 2 == 0 else value,
                      'duration': duration, 'timing': timing(duration)})
        value = output
    duration = value * 1000 // 16
    return {'rootFont': 32 if advanced else 16, 'opacity': 1 if value == 16 else 0,
            'leafDuration': duration, 'leaf': timing(duration), 'nodes': nodes}


def require_original_calibration(observations):
    literal = observations['literal']
    depth = literal['depth']
    assert depth in (1, 2, 4, 8)
    for mode, item in observations.items():
        assert item['mode'] == mode and item['depth'] == depth
        assert item['literalInitial'] == item['initial'] == expected_snapshot(depth, False)
    expected = expected_snapshot(depth, True)
    assert literal['beforeMembership'] == literal['afterMembership'] == expected
    assert all(sample['opacity'] == expected['opacity'] for sample in literal['samples'])
    assert all(member['animation'] and member['effect'] for member in literal['membership'])


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
    assert binding['terminal']['callbacks_passed'] + binding['terminal']['callbacks_failed'] == 4
    assert (binding['terminal']['page_endings_ok'], binding['terminal']['complete_records']) == (1, 4)
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
    assert {key: value for key, value in metadata.items() if key not in ('build_revision', 'harness_revision', 'source_role')} == policy['prepared_application_metadata']
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
    assert replay == read(phase / 'ASSESSMENT.json') and replay['complete'] and len(replay['rows']) == 4
    assert all(row['status'] in ('PASS', 'FAIL') for row in replay['rows'])
    collection = load('progress_original_records', root / policy['baseline_capsule']['directory'] / 'records.py').collect(root, directory / 'progress-records', read(directory / 'PROGRESS-BINDING.json'), source, replay)
    assert collection == read(directory / 'PROGRESS-RECORDS.json') and not collection['errors']
    require_complete_collection(collection, binding['terminal'])
    for filename in policy['record_kinds']:
        require_original_calibration(read(directory / 'progress-records' / filename)['observations'])
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
