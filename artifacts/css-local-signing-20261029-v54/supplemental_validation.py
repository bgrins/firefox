import hashlib
import importlib.util
import json


def verify(root, inputs):
    binding = inputs['supplemental_validation']
    assert isinstance(binding, dict) and binding
    read = lambda name: json.loads((root / name).read_bytes())
    sha = lambda name: hashlib.sha256((root / name).read_bytes()).hexdigest()
    for name in binding.values():
        assert isinstance(name, str) and inputs['evidence_pins'][name] == sha(name)
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, root / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    assessor = load('shadow_sign_supplemental_assessor', binding['assessor'])
    checks = load('shadow_sign_supplemental_checks', binding['checks'])
    policy = read(binding['assessment_policy'])
    original_policy = read(binding['original_assessment_policy'])
    assert policy['expected_subtests'] == original_policy['expected_subtests']
    assert policy['target_subtests'] == original_policy['target_subtests']
    expected = {(test, name) for test, names in policy['expected_subtests'].items() for name in names}
    targets = {(test, name) for test, names in policy['target_subtests'].items() for name in names}
    assert len(expected) == 8 and len(targets) == 2 and targets <= expected
    events = [json.loads(line) for line in (root / binding['raw']).read_text().splitlines() if line.strip()]
    old_events = [json.loads(line) for line in (root / binding['original_raw']).read_text().splitlines() if line.strip()]
    original = assessor.assess(old_events, read(binding['original_result'])['exit'], original_policy, checks, run_binding=read(binding['original_metadata']))
    assert original == read(binding['original_assessment'])
    assert original['complete'] and not original['errors'] and not original['fixture_setup_errors']
    old_rows = [row for row in old_events if row.get('action') == 'test_status']
    assert len(old_rows) == 8 and {(row['test'], row['subtest']) for row in old_rows} == expected
    assert {(row['test'], row['subtest']) for row in old_rows if row['status'] == 'FAIL'} == targets
    assert all(row['status'] == 'PASS' for row in old_rows if (row['test'], row['subtest']) not in targets)
    baseline = read(binding['baseline_result'])
    assert baseline['success'] and baseline['preservation_verified'] and baseline['browser_build_performed'] is False
    assert baseline['phase'] == {'assessment_sha256': sha(binding['original_assessment']), 'raw_sha256': sha(binding['original_raw']), 'result_sha256': sha(binding['original_result'])}
    assert read(binding['original_pre']) == read(binding['original_post'])
    assert read(binding['original_cleanup'])['owned_group_absent'] and read(binding['original_cleanup'])['temporary_root_removed']
    assert read(binding['baseline_terminal'])['exit'] == 0
    result = read(binding['result'])
    assert result['success'] and result['comparison_gate_passed'] and result['preservation_verified']
    assert result['exit'] == 0 and result['execution_error'] is None
    actual = assessor.assess(events, 0, policy, checks, original=original, run_binding=read(binding['metadata']))
    assert actual == read(binding['assessment'])
    assert actual['complete'] and actual['comparison_gate_passed']
    assert not actual['errors'] and not actual['comparison_errors'] and not actual['fixture_setup_errors'] and not actual['unexpected']
    assert len(actual['regression_signature']) == 7
    rows = [row for row in events if row.get('action') == 'test_status']
    ends = [row for row in events if row.get('action') == 'test_end']
    assert len(rows) == 8 and {(row['test'], row['subtest']) for row in rows} == expected
    assert all(row['status'] == 'PASS' for row in rows)
    assert len(ends) == 1 and ends[0]['status'] == 'OK'
    assert read(binding['pre']) == read(binding['post'])
    assert read(binding['metadata']) == read(binding['metadata_post'])
    assert read(binding['cleanup'])['owned_group_absent'] and read(binding['cleanup'])['temporary_root_removed']
    primary = inputs['final_validation']
    assert read(binding['metadata']) == read(primary['metadata'])
    assert read(binding['pre']) == read(primary['post'])
    wrapper = read(primary['wrapper'])
    assert wrapper['success'] and wrapper['preservation_verified'] and wrapper['owned_processes'] == {}
    assert wrapper['epoch_sha256'] == inputs['initial_epoch']
    assert wrapper['supplemental_phase'] == {'assessment_sha256': sha(binding['assessment']), 'raw_sha256': sha(binding['raw']), 'result_sha256': sha(binding['result'])}
    return actual
