import copy
import importlib.util
import json
import os


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy, epoch, h, check_processes=True):
    pair = root / policy['paired_runtime']
    h.authenticate(pair, policy['paired_manifest_sha256'])
    completion = root / policy['pair_completion_directory']
    h.authenticate(completion, policy['pair_completion_sha256'])
    for name, pin in h.read(completion / 'PAYLOADS.json').items():
        assert h.digest((root / name).read_bytes()) == pin
    capsule = root / policy['pair_capsule']
    h.authenticate(capsule, policy['pair_capsule_sha256'])
    pair_policy = h.read(capsule / 'POLICY.json')
    for name, pin in pair_policy['references'].items():
        assert h.digest((root / name).read_bytes()) == pin
    if epoch is not None:
        assert epoch['semantic_index']['head'] == policy['head']
    initial = h.read(pair / 'BASELINE-PRE.json')
    assert initial['controls'] == pair_policy['controls']
    before, after = initial['snapshot'], h.read(pair / 'POST.json')
    projected = copy.deepcopy(before)
    projected['index']['raw_index'] = after['index']['raw_index']
    assert projected == after
    if epoch is not None:
        original_binaries = h.read(pair / 'original-wpt/BINARY-PINS.json')
        assert set(original_binaries) == set(policy['rebuilt_binaries'])
        for name, pin in original_binaries.items():
            assert epoch['pins'][name] == pin
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
    assert set(sources) == set(restored['sources']) == set(policy['sources'])
    for name, source in policy['sources'].items():
        for key in ('base_sha256', 'candidate_sha256', 'git_object'):
            assert sources[name][key] == source[key]
        assert restored['sources'][name] == {'sha256': source['base_sha256'], 'identity': sources[name]['identity']}
        if epoch is not None:
            assert epoch['pins'].get(name, source['base_sha256']) == source['base_sha256']
            assert epoch['installed_identities'].get(name, sources[name]['identity']) == sources[name]['identity']
    build = h.read(pair / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 0 and build['error'] is None and build['stop_reason'] is None
    assert build['owned_group_absent'] and build['cleanup_errors'] == []
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        if check_processes:
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
        assert replay['observed_subtest_count'] == 98 and len(replay['ends']) == 16
        if role == 'original':
            original = replay
        else:
            assert replay['comparison_gate_passed'] and replay['comparison_errors'] == []
            assert phase_result['comparison_gate_passed']
            assert all(row['status'] == 'PASS' for row in replay['rows'])
            assert phase_result['exit'] == 1
            changed_expectations = {(r['test'], r['subtest']) for r in replay['rows'] if r.get('expected', r['status']) != r['status']}
            assert changed_expectations == {('/dom/nodes/moveBefore/custom-element-move-reactions.html', n) for n in policy['deleted_metadata']['expected_fail_subtests']}
            assert result['candidate_phase'] == {'assessment_sha256': h.digest((directory / 'ASSESSMENT.json').read_bytes()), 'raw_sha256': h.digest((directory / 'raw.jsonl').read_bytes()), 'result_sha256': h.digest((directory / 'RESULT.json').read_bytes())}
        cleanup = h.read(directory / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        if check_processes:
            h.group_absent(h.read(directory / 'PROCESS.json')['pgid'])
        for name in policy['primary_tests']:
            item = policy['tests'][name]
            relative = name.removeprefix('testing/web-platform/tests/')
            assert h.digest((directory / 'tests' / relative).read_bytes()) == item['sha256']
    terminal = h.read(pair / 'CANDIDATE-ROOT-REPORTED-TERMINAL.json')
    assert terminal['owner_session'] == 11795 and terminal['terminal_tool_chunk'] == '916239' and terminal['terminal_exit'] == 0
    assert terminal['result_sha256'] == policy['paired_result_sha256']
    supplement = load('shadow_supplement_evidence', root / 'artifacts/css-shadow-move-promotion-v1/supplement.py')
    supplement_binding = supplement.verify_original(root, policy, h, check_processes)
    return {'supplement': supplement_binding, 'paired_result_sha256': policy['paired_result_sha256'], 'pair_completion_sha256': policy['pair_completion_sha256'], 'comparison_gate_passed': True, 'observed_subtests': 98, 'accepted': False}
