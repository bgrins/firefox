import hashlib
import importlib.util
import json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, binding):
    assert binding and binding['ready']
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name, pin in binding['evidence'].items():
        assert sha(root / name) == pin, name
    final = root / binding['runtime']
    result = read(final / 'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['lint_passed']
    assert result['owned_processes'] == {} and result['native_fix_acceptance'] is False and result['canonical_updated'] is False
    terminal = read(root / binding['terminal'])
    assert terminal['root_observed_terminal'] and terminal['exit'] == 0
    assert terminal['session_id'] == binding['session'] and terminal['terminal_tool'] == binding['terminal_tool']
    assert terminal['result_sha256'] == sha(final / 'RESULT.json')
    assert read(final / 'PRE.json') == read(final / 'POST.json')
    build = root / binding['build_runtime']
    outer, inner = read(build / 'RESULT.json'), read(build / 'build-RESULT.json')
    assert outer['command_success'] and outer['preservation_verified'] and outer['error'] is None
    assert not outer['owned_processes'] and not outer['publication_errors'] and not outer['accepted']
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assert inner['error'] is None and inner['stop_reason'] is None
    built = read(build / 'EPOCH.json')
    inputs = read(final / 'BINDINGS.json')
    assert built['pins']['servo/components/style/values/generics/calc.rs'] == binding['source_sha256']
    assert built['hypot_finite_scale_transition']['compiled'] and not built['hypot_finite_scale_transition']['accepted']
    assert inputs['source']['candidate_sha256'] == binding['source_sha256']
    assert inputs['fixture_sha256'] == binding['fixture_sha256']
    assert inputs['controls']['CURRENT-EPOCH.json'] == sha(build / 'EPOCH.json')
    lint = read(root / binding['lint_result'])
    assert lint['exit'] == 0 and lint['errors'] == 0
    assert lint['source_sha256'] == binding['fixture_sha256']
    assert lint['log_sha256'] == sha(root / binding['lint_log'])
    assessor = load('checkpoint_final_assessor', root / binding['assessor'])
    checks = load('checkpoint_final_checks', root / binding['checks_helper'])
    ownership = load('checkpoint_final_ownership', root / binding['ownership_helper'])
    original = None
    for role, phase in [('original', root / binding['baseline_runtime'] / 'original-wpt'), ('candidate', final / 'candidate-wpt')]:
        record = read(phase / 'RESULT.json')
        assert record['success'] and record['preservation_verified'] and record['execution_error'] is None
        assert read(phase / 'PRE.json') == read(phase / 'POST.json')
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        ownership.group_absent(read(phase / 'PROCESS.json')['pgid'])
        replay = assessor.assess([json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()],
            record['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks,
            original=original, run_binding=read(phase / 'APPLICATION-METADATA.json'))
        assert json.loads(json.dumps(replay)) == read(phase / 'ASSESSMENT.json')
        assert replay['complete'] and replay['errors'] == [] and replay['fixture_setup_errors'] == []
        assert replay['observed_subtest_count'] == 227 and len(replay['regression_signature']) == 215
        assert len(replay['ends']) == 4 and all(row['status'] == 'OK' for row in replay['ends'])
        assert sha(phase / 'tests/css/css-values/hypot-finite-scale.html') == binding['fixture_sha256']
        if role == 'original':
            original = replay
        else:
            assert replay['comparison_gate_passed'] and replay['comparison_errors'] == []
            assert replay['regression_signature'] == original['regression_signature']
            assert result['phase'] == {'assessment_sha256': sha(phase / 'ASSESSMENT.json'), 'raw_sha256': sha(phase / 'raw.jsonl'), 'result_sha256': sha(phase / 'RESULT.json')}
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        ownership.group_absent(read(build / name)['pgid'])
    return {'result_sha256': sha(final / 'RESULT.json'), 'original_assessment_sha256': sha(root / binding['baseline_runtime'] / 'original-wpt/ASSESSMENT.json'),
            'candidate_assessment_sha256': sha(final / 'candidate-wpt/ASSESSMENT.json'),
            'source_sha256': binding['source_sha256'], 'fixture_sha256': binding['fixture_sha256'],
            'comparison_gate_passed': True, 'accepted': False}
