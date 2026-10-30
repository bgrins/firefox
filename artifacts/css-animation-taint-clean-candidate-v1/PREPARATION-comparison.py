import copy
import hashlib
import importlib.util
import json

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phase_policy(settings):
    result = dict(settings, tests={p: 'testharness' for p in settings['expected_subtests']}, held_subtests={})
    result['regression_subtests'] = {p: [n for n in names if n not in settings['target_subtests'].get(p, [])] for p, names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def expected_wpt(root, policy):
    old = read(root / policy['predecessor']['directory'] / 'POLICY.json')
    suite = root / policy['suite_binding']['directory']
    union = read(suite / 'INPUTS.json')
    settings = copy.deepcopy(old['wpt'])
    settings.update(resources=union['resources'], metadata=union['metadata'],
                    manifest={'path': str((suite / 'MANIFEST.json').relative_to(root)), 'sha256': sha(suite / 'MANIFEST.json')},
                    expected_subtests=union['roster'], expected_subtest_count=125,
                    expected_control_count=125, expected_page_count=18,
                    expected_regression_signature_count=143,
                    fixture_target_pages=list(union['roster']), harness_revision=policy['head'],
                    phase_revisions={'original': policy['head'], 'candidate': policy['head']})
    return settings


def admit_snapshot(historical, current):
    expected = copy.deepcopy(historical)
    expected['index']['raw_index'] = current['index']['raw_index']
    assert expected == current


def replay_original(root, policy, assessor, checks):
    load('clean_candidate_admission', root / policy['owner_directory'] / 'admission.py').validate(root, policy)
    binding = policy['baseline_binding']
    directory = root / binding['directory']
    source = read(root / policy['baseline_capsule']['directory'] / 'POLICY.json')
    result = read(directory / 'RESULT.json')
    assert sha(directory / 'RESULT.json') == binding['result_sha256']
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['provider_source_role'] == 'clean-original' and result['build_revision'] == source['head']
    assert not result['native_fix_acceptance']
    phase = directory / 'original-wpt'
    for name, key in [('ASSESSMENT.json', 'assessment_sha256'), ('raw.jsonl', 'raw_sha256'), ('RESULT.json', 'result_sha256')]:
        assert sha(phase / name) == result['phase'][key]
    build = read(directory / 'original-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert read(directory / 'original-build/build-RESULT.json')['exit'] == 0
    assert build['native_sources'] == {'servo/components/style/custom_properties.rs': policy['semantic_original_sources']['servo/components/style/custom_properties.rs']}
    assert read(phase / 'BINARY-PINS.json') == build['binaries']
    assert set(build['binaries']) == set(policy['rebuilt_binaries'])
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == read(directory / 'PHASES-PRE.json') == read(directory / 'PHASES-POST.json')
    metadata = read(phase / 'APPLICATION-METADATA.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    assert metadata['revision'] == metadata['build_revision'] == source['head']
    assert metadata['harness_revision'] == source['head'] and metadata['source_role'] == 'original'
    assert read(phase / 'ASSESSMENT-POLICY.json') == phase_policy(source['wpt'])
    phase_result = read(phase / 'RESULT.json')
    assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
    assert read(phase / 'CLEANUP.json')['owned_group_absent'] and read(phase / 'CLEANUP.json')['temporary_root_removed']
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    original_assessor = load('clean_original_assessor', root / policy['baseline_capsule']['directory'] / 'assess.py')
    replay = original_assessor.assess(events, phase_result['exit'], phase_policy(source['wpt']), checks, run_binding=metadata)
    assert replay == read(phase / 'ASSESSMENT.json') and replay['complete']
    outcomes = read(directory / 'OUTCOMES.json')
    assert outcomes['rows'] == replay['rows'] and outcomes['endings'] == replay['ends']
    assert outcomes['callbacks_passed'] == sum(r['status'] == 'PASS' for r in replay['rows'])
    assert outcomes['callbacks_failed'] == sum(r['status'] == 'FAIL' for r in replay['rows'])
    assert len(replay['rows']) == 125 and len(replay['ends']) == 18
    projected = assessor.assess(events, phase_result['exit'], phase_policy(policy['wpt']), checks, run_binding=metadata)
    assert projected['complete'] and projected['rows'] == replay['rows'] and projected['ends'] == replay['ends']
    return projected


def replay_all(root, policy):
    assert policy['wpt'] == expected_wpt(root, policy)
    if policy['baseline_binding'] is not None:
        here = root / policy['owner_directory']
        return replay_original(root, policy, load('clean_candidate_assessor', here / 'assess.py'), load('clean_stream_checks', root / policy['wpt']['checks_helper']))
