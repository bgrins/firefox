import copy
import importlib.util
import json
import os


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy, epoch, h):
    pair = root / policy['paired_runtime']
    h.authenticate(pair, policy['paired_manifest_sha256'])
    completion = root / policy['pair_completion_directory']
    h.authenticate(completion, policy['pair_completion_sha256'])
    for name, pin in h.read(completion / 'PAYLOADS.json').items():
        assert h.digest((root / name).read_bytes()) == pin
    capsule = root / policy['pair_capsule']
    h.authenticate(capsule, policy['pair_capsule_sha256'])
    pair_policy = h.read(capsule / 'POLICY.json')
    assert pair_policy['head'] == policy['head'] == epoch['semantic_index']['head']
    initial = h.read(pair / 'BASELINE-PRE.json')
    assert initial['controls'] == pair_policy['controls']
    assert initial['controls']['CURRENT-EPOCH.json'] == policy['expected_baseline_epoch_sha256']
    before, after = initial['snapshot'], h.read(pair / 'POST.json')
    projected = copy.deepcopy(before)
    projected['index']['raw_index'] = after['index']['raw_index']
    assert projected == after
    live_expected = copy.deepcopy(after)
    live_expected['index']['raw_index'] = epoch['raw_index_observation']['current']
    state = h.load_state(root / 'artifacts/css-registered-number-native-runtime-v1')
    assert state.a.verify_current(state.h, root, dict(os.environ, GIT_OPTIONAL_LOCKS='0'), epoch) == live_expected
    assert h.digest((pair / 'RESULT.json').read_bytes()) == policy['paired_result_sha256']
    result = h.read(pair / 'RESULT.json')
    assert result['success'] and result['error'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['native_fix_acceptance'] is False
    restored = h.read(pair / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    cleanup = h.read(pair / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert not (pair / 'backups').exists()
    sources = h.read(pair / 'CANDIDATE-PRE.json')['sources']
    source = policy['source']
    assert set(sources) == set(restored['sources']) == {source['path']}
    for key in ('base_capture', 'candidate_capture', 'base_sha256', 'candidate_sha256'):
        assert sources[source['path']][key] == source[key]
    assert restored['sources'][source['path']] == {'sha256': source['base_sha256'], 'identity': sources[source['path']]['identity']}
    assert epoch['pins'][source['path']] == source['base_sha256']
    assert epoch['installed_identities'][source['path']] == sources[source['path']]['identity']
    build = h.read(pair / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 0 and build['error'] is None and build['stop_reason'] is None
    assert build['owned_group_absent'] and build['cleanup_errors'] == []
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        h.group_absent(h.read(pair / 'candidate-build' / name)['pgid'])
    settings = pair_policy['wpt']
    expected_policy = dict(settings, tests={test: 'testharness' for test in settings['expected_subtests']}, held_subtests={})
    expected_policy['regression_subtests'] = {test: [name for name in names if name not in settings['target_subtests'].get(test, [])] for test, names in settings['expected_subtests'].items()}
    expected_policy['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    checks = load('promotion_wpt_checks', root / settings['checks_helper'])
    assessor = load('promotion_assessor', capsule / 'assess.py')
    original = None
    for role in ('original', 'candidate'):
        directory = pair / (role + '-wpt')
        phase_result = h.read(directory / 'RESULT.json')
        assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
        assert h.read(directory / 'PRE.json') == h.read(directory / 'POST.json')
        metadata = h.read(directory / 'APPLICATION-METADATA.json')
        assert metadata == h.read(directory / 'APPLICATION-METADATA-POST.json')
        assert h.read(directory / 'ASSESSMENT-POLICY.json') == expected_policy
        events = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines()]
        replay = assessor.assess(events, phase_result['exit'], expected_policy, checks, original=original, run_binding=metadata)
        assert json.loads(json.dumps(replay)) == h.read(directory / 'ASSESSMENT.json')
        assert replay['complete'] and replay['errors'] == [] and replay['fixture_setup_errors'] == []
        assert replay['observed_subtest_count'] == 36 and len(replay['ends']) == 7
        if role == 'original':
            original = replay
        else:
            assert replay['comparison_gate_passed'] and replay['comparison_errors'] == []
            assert phase_result['comparison_gate_passed']
            assert result['candidate_phase'] == {'assessment_sha256': h.digest((directory / 'ASSESSMENT.json').read_bytes()), 'raw_sha256': h.digest((directory / 'raw.jsonl').read_bytes()), 'result_sha256': h.digest((directory / 'RESULT.json').read_bytes())}
        cleanup = h.read(directory / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        h.group_absent(h.read(directory / 'PROCESS.json')['pgid'])
        for name, item in policy['tests'].items():
            relative = name.removeprefix('testing/web-platform/tests/')
            assert h.digest((directory / 'tests' / relative).read_bytes()) == item['sha256']
    return {'paired_result_sha256': policy['paired_result_sha256'], 'pair_completion_sha256': policy['pair_completion_sha256'], 'comparison_gate_passed': True, 'observed_subtests': 36, 'accepted': False}
