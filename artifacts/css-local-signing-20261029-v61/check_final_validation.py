import hashlib
import importlib.util
import json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy):
    binding = policy["final_validation"]
    assert binding and binding['ready']
    assert binding['source_sha256'] == policy['pending_native']['source']['candidate_sha256']
    assert binding['fixture_sha256'] == policy['pending_native']['test']['sha256']
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name, pin in {**binding['evidence'], **binding['local_references']}.items():
        assert sha(root / name) == pin, name
    final = root / binding['runtime']
    result = read(final / 'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['lint_passed'] and result['metadata_cleanup_validated']
    assert result['owned_processes'] == {} and result['native_fix_acceptance'] is False and result['canonical_updated'] is False
    terminal = read(root / binding['terminal'])
    assert terminal == binding['terminal_record'] and terminal[binding['exit_field']] == 0
    assert terminal['session_id'] == binding['session'] and terminal[binding['terminal_field']] == binding['terminal_tool']
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
    assert built['pow_special_value_transition']['compiled'] and not built['pow_special_value_transition']['accepted']
    assert inputs['source']['candidate_sha256'] == binding['source_sha256']
    assert inputs['fixture_sha256'] == binding['fixture_sha256']
    removed = policy['pending_native']['deleted_metadata']['path']
    assert built['pins'][removed] is None and removed not in built['installed_identities']
    assert built['pow_special_value_transition']['deleted_metadata'] == removed
    assert inputs['controls']['CURRENT-EPOCH.json'] == sha(build / 'EPOCH.json')
    owner = read(root / binding['owner_policy'])
    assert owner['head'] == policy['head'] and owner['execution_enabled']
    assert inputs['deleted_metadata'] == owner['deleted_metadata']
    assert inputs['controls'] == owner['controls']
    assert inputs['baseline_receipts'] == owner['baseline_receipts']
    assert inputs['build_receipts'] == owner['build_receipts']
    assert inputs['lint_receipts'] == owner['lint_receipts']
    assert read(build / 'APPLICATION-METADATA.json')['revision'] == policy['head']
    baseline_helper = load('pow_final_baseline_helper', root / binding['baseline_checker'])
    final_phase_policy = baseline_helper.phase_policy(owner['wpt'])
    assert read(final / 'candidate-wpt/ASSESSMENT-POLICY.json') == final_phase_policy
    old_settings = read(root / binding['baseline_runtime'] / 'original-wpt/ASSESSMENT-POLICY.json')
    for key, expected in owner['wpt'].items():
        if key == 'resources':
            changed = dict(old_settings[key])
            fixture = 'css/css-values/pow-special-value-context.html'
            assert changed[fixture]['sha256'] == expected[fixture]['sha256'] == binding['fixture_sha256']
            changed[fixture] = expected[fixture]
            assert changed == expected
        elif key == 'metadata':
            changed = dict(old_settings[key])
            name = 'css/css-values/hypot-pow-sqrt-computed.html.ini'
            assert changed[name]['sha256'] == owner['deleted_metadata']['sha256']
            assert expected[name] == {'path': removed, 'sha256': None}
            changed[name] = expected[name]
            assert changed == expected
        else:
            assert old_settings[key] == expected
    lint = read(root / binding['lint_result'])
    assert lint['exit'] == 0 and lint['errors'] == 0
    assert lint['fixture_sha256'] == binding['fixture_sha256']
    assert lint['log_sha256'] == sha(root / binding['lint_log'])
    command = read(root / binding['lint_command_receipt'])
    assert command['command'] == owner['lint_command']
    assert command['lint_receipt_sha256'] == sha(root / binding['lint_result'])
    assessor = load('checkpoint_final_assessor', root / binding['assessor'])
    checks = load('checkpoint_final_checks', root / binding['checks_helper'])
    ownership = load('checkpoint_final_ownership', root / binding['ownership_helper'])
    original = None
    for role, phase in [('original', root / binding['baseline_runtime'] / 'original-wpt'), ('candidate', final / 'candidate-wpt')]:
        record = read(phase / 'RESULT.json')
        assert record['success'] and record['preservation_verified'] and record['execution_error'] is None
        assert read(phase / 'PRE.json') == read(phase / 'POST.json')
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        ownership.group_absent(read(phase / 'PROCESS.json')['pgid'])
        replay = assessor.assess([json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()],
            record['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks,
            original=original, run_binding=read(phase / 'APPLICATION-METADATA.json'))
        assert json.loads(json.dumps(replay)) == read(phase / 'ASSESSMENT.json')
        assert replay['complete'] and replay['errors'] == [] and replay['fixture_setup_errors'] == []
        assert replay['observed_subtest_count'] == 147 and len(replay['regression_signature']) == 131
        assert len(replay['ends']) == 2 and all(row['status'] == 'OK' for row in replay['ends'])
        assert sha(phase / 'tests/css/css-values/pow-special-value-context.html') == binding['fixture_sha256']
        if role == 'original':
            original = replay
        else:
            assert replay['comparison_gate_passed'] and replay['comparison_errors'] == []
            assert record['exit'] == 0 and replay['unexpected'] == []
            assert all(row['status'] == 'PASS' for row in replay['rows'])
            assert not (phase / 'metadata/css/css-values/hypot-pow-sqrt-computed.html.ini').exists()
            assert replay['regression_signature'] == original['regression_signature']
            assert result['phase'] == {'assessment_sha256': sha(phase / 'ASSESSMENT.json'), 'raw_sha256': sha(phase / 'raw.jsonl'), 'result_sha256': sha(phase / 'RESULT.json')}
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        ownership.group_absent(read(build / name)['pgid'])
    return {'result_sha256': sha(final / 'RESULT.json'), 'original_assessment_sha256': sha(root / binding['baseline_runtime'] / 'original-wpt/ASSESSMENT.json'),
            'candidate_assessment_sha256': sha(final / 'candidate-wpt/ASSESSMENT.json'),
            'source_sha256': binding['source_sha256'], 'fixture_sha256': binding['fixture_sha256'],
            'comparison_gate_passed': True, 'accepted': False}
