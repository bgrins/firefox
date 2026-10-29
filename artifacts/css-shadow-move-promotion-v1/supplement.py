import copy
import importlib.util
import json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_original(root, policy, h, check_processes=True):
    binding = policy['supplemental_baseline']
    capsule = root / policy['supplemental_capsule']['directory']
    h.authenticate(capsule, policy['supplemental_capsule']['sha256'])
    baseline_policy = h.read(capsule / 'POLICY.json')
    assert baseline_policy['head'] == policy['head']
    for name, pin in baseline_policy['references'].items():
        assert h.digest((root / name).read_bytes()) == pin
    runtime = root / binding['directory']
    assert baseline_policy['output'] == binding['directory']
    h.authenticate(runtime, binding['manifest_sha256'])
    terminal = h.read(runtime / binding['terminal_path'])
    assert terminal == binding['terminal'] and terminal['exit'] == 0
    completed = h.read(runtime / 'BASELINE-RESULT.json')
    assert h.digest((runtime / 'BASELINE-RESULT.json').read_bytes()) == binding['result_sha256']
    assert completed['success'] and completed['preservation_verified']
    assert completed['error'] is None and completed['preservation_error'] is None
    assert completed['owned_processes'] == {} and completed['browser_build_performed'] is False
    initial = h.read(runtime / 'BASELINE-PRE.json')
    assert initial['controls'] == baseline_policy['controls']
    phase = runtime / 'original-wpt'
    assert h.read(phase / 'PRE.json') == h.read(phase / 'POST.json') == initial['snapshot']
    result = h.read(phase / 'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['execution_error'] is None
    assert result['exit'] == 1
    metadata = h.read(phase / 'APPLICATION-METADATA.json')
    assert metadata == h.read(phase / 'APPLICATION-METADATA-POST.json')
    settings = baseline_policy['wpt']
    expected = dict(settings, tests={test: 'testharness' for test in settings['expected_subtests']}, held_subtests={})
    expected['regression_subtests'] = {test: [n for n in names if n not in settings['target_subtests'].get(test, [])] for test, names in settings['expected_subtests'].items()}
    expected['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    assert h.read(phase / 'ASSESSMENT-POLICY.json') == expected
    checks = load('shadow_supplement_checks', root / settings['checks_helper'])
    assessor = load('shadow_supplement_assessor', capsule / 'assess.py')
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    replay = assessor.assess(events, result['exit'], expected, checks, run_binding=metadata)
    assert json.loads(json.dumps(replay)) == h.read(phase / 'ASSESSMENT.json')
    assert replay['complete'] and replay['errors'] == []
    targets = {(test, name) for test, names in settings['target_subtests'].items() for name in names}
    assert len(targets) == 2 and len(replay['rows']) == 8 and len(replay['ends']) == 1
    assert all(row['status'] == ('FAIL' if (row['test'], row['subtest']) in targets else 'PASS') for row in replay['rows'])
    assert replay['ends'][0]['status'] == 'OK'
    assert completed['phase'] == {'assessment_sha256': h.digest((phase / 'ASSESSMENT.json').read_bytes()),
        'raw_sha256': h.digest((phase / 'raw.jsonl').read_bytes()),
        'result_sha256': h.digest((phase / 'RESULT.json').read_bytes())}
    cleanup = h.read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    if check_processes:
        h.group_absent(h.read(phase / 'PROCESS.json')['pgid'])
    test = policy['supplemental_test']
    relative = test.removeprefix('testing/web-platform/tests/')
    assert h.digest((phase / 'tests' / relative).read_bytes()) == policy['tests'][test]['sha256']
    assert h.read(phase / 'BINARY-PINS.json') == h.read(root / policy['paired_runtime'] / 'original-wpt/BINARY-PINS.json')
    return {'baseline_manifest_sha256': binding['manifest_sha256'], 'phase': completed['phase'],
            'callbacks': 8, 'target_failures': 2, 'controls_pass': 6, 'end_ok': 1}


def final_policy(root, policy):
    baseline = json.loads((root / policy['supplemental_capsule']['directory'] / 'POLICY.json').read_bytes())
    expected = copy.deepcopy(baseline['wpt'])
    test = policy['supplemental_test']
    expected['resources'][test.removeprefix('testing/web-platform/tests/')] = {'path': test, 'sha256': policy['tests'][test]['sha256']}
    expected['harness_revision'] = policy['head']
    expected['phase_revisions']['candidate'] = policy['head']
    assert policy['supplemental_wpt'] == expected
    return dict(policy, wpt=expected)
