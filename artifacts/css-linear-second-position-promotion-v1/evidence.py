import copy
import importlib.util
import json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy, epoch, h):
    pair = root / policy['paired_runtime']
    h.authenticate(pair, policy['paired_manifest_sha256'])
    assert h.digest((pair / 'RESULT.json').read_bytes()) == policy['paired_result_sha256']
    result = h.read(pair / 'RESULT.json')
    assert result['success'] and result['error'] is None and not result['publication_errors']
    assert result['backups_removed_after_verification']
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert h.read(pair / 'RESTORATION.json')['errors'] == []
    assert h.read(pair / 'RESTORATION.json')['owned_processes'] == {}
    baseline = h.read(pair / 'PRE-CURRENT-EPOCH.json')
    compared = copy.deepcopy(epoch)
    compared['raw_index_observation']['current'] = baseline['raw_index_observation']['current']
    assert compared == baseline, 'Only independently verified raw-index refresh may follow pair before promotion'
    capsule = root / policy['pair_capsule']
    h.authenticate(capsule, policy['pair_capsule_sha256'])
    runner = load('promotion_test_runner', capsule / 'run.py')
    bindings = load('promotion_test_bindings', capsule / 'bindings.py')
    candidate = pair / 'candidate-wpt'
    candidate_policy = h.read(candidate / 'POLICY.json')
    candidate_epoch = h.read(candidate / 'EPOCH.json')
    bindings.validate_phase(root, capsule, candidate_policy, candidate_epoch, runner)
    original = bindings.validate_original(root, capsule, candidate_policy, runner)
    checks = runner.load('promotion_lifecycle', root / candidate_policy['helpers']['checks'])
    parser = runner.load('promotion_assessor', capsule / 'assess.py')
    candidate_result = h.read(candidate / 'RESULT.json')
    saved = h.read(candidate / 'ASSESSMENT.json')
    assert candidate_result['comparison_gate_passed'] and candidate_result['observation_gate_passed']
    assert candidate_result['execution_error'] is None and candidate_result['preservation_error'] is None
    assert saved['complete'] and saved['execution_preserved'] and saved['comparison_gate_passed']
    assert saved['capsule_manifest_sha256'] == policy['pair_capsule_sha256']
    assert saved['native_sources'] == {policy['source']['path']: policy['source']['candidate_sha256']}
    events = [json.loads(line) for line in (candidate / 'raw.jsonl').read_text().splitlines()]
    replay = parser.assess(events, candidate_result['exit'], candidate_policy, checks,
                          original=original, run_binding=h.read(candidate / 'APPLICATION-METADATA.json'))
    replay = runner.augment_assessment(replay, phase='candidate-1', capsule_sha=policy['pair_capsule_sha256'],
        epoch_sha=candidate_policy['epoch_sha256'], policy=candidate_policy,
        capsule_directory=policy['pair_capsule'], experiment_sha=h.digest((capsule / 'EXPERIMENT.json').read_bytes()), execution_preserved=True)
    assert json.loads(json.dumps(replay)) == saved
    assert replay['comparison_gate_passed'] and replay['phase_gate_passed'] and replay['observed_subtest_count'] == 48
    assert set(result['phase_results']) == {'original-baseline-1', 'original-crash-1', 'candidate-1'}
    phases = [('original-baseline-1', 'original-baseline-wpt'), ('original-crash-1', 'original-crash-wpt'), ('candidate-1', 'candidate-wpt')]
    for phase, label in phases:
        directory = pair / label
        assert result['phase_results'][phase]['wrapper_exit'] == 0
        assert result['phase_results'][phase]['assessment_sha256'] == h.digest((directory / 'ASSESSMENT.json').read_bytes())
        cleanup = h.read(directory / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        assert h.read(pair / (phase + '-WRAPPER-CLEANUP.json'))['restoration_safe']
        h.group_absent(h.read(directory / 'PROCESS.json')['pgid'])
        if phase != 'original-baseline-1':
            for name, item in policy['tests'].items():
                relative = name.removeprefix('testing/web-platform/tests/')
                assert h.digest((directory / 'tests' / relative).read_bytes()) == item['sha256']
    for role in ('original', 'candidate'):
        for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
            h.group_absent(h.read(pair / (role + '-build') / name)['pgid'])
    return {'pair_manifest_sha256': policy['paired_manifest_sha256'],
            'pair_result_sha256': policy['paired_result_sha256'],
            'comparison_gate_passed': True, 'accepted': False}
