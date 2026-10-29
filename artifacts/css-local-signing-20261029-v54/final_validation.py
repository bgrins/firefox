import hashlib
import importlib.util
import json
import runpy
from pathlib import Path


def verify(root, inputs):
    binding = inputs['final_validation']
    assert isinstance(binding, dict) and binding
    read = lambda name: json.loads((root / name).read_bytes())
    sha = lambda name: hashlib.sha256((root / name).read_bytes()).hexdigest()
    for name, pin in inputs['evidence_pins'].items():
        assert sha(name) == pin
    for name in binding.values():
        assert isinstance(name, str) and name in inputs['evidence_pins']
    result = read(binding['result'])
    wrapper = read(binding['wrapper'])
    assessment = read(binding['assessment'])
    assert result['success'] and result['comparison_gate_passed'] and result['preservation_verified']
    assert result['exit'] == 0 and result['execution_error'] is None
    assert wrapper['success'] and wrapper['preservation_verified'] and wrapper['owned_processes'] == {}
    assert wrapper['native_fix_acceptance'] is False
    assert wrapper['epoch_sha256'] == inputs['initial_epoch']
    assert wrapper['phase'] == {'assessment_sha256': sha(binding['assessment']), 'raw_sha256': sha(binding['raw']), 'result_sha256': sha(binding['result'])}
    assert read(binding['pre']) == read(binding['post'])
    assert read(binding['metadata']) == read(binding['metadata_post'])
    assert read(binding['cleanup'])['owned_group_absent'] and read(binding['cleanup'])['temporary_root_removed']
    assert read(binding['terminal'])['exit'] == 0
    assert assessment['complete'] and assessment['comparison_gate_passed']
    assert assessment['observed_subtest_count'] == 98
    assert not assessment['errors'] and not assessment['comparison_errors'] and not assessment['fixture_setup_errors']
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, root / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    assessor = load('shadow_sign_assessor', binding['assessor'])
    checks = load('shadow_sign_checks', binding['checks'])
    policy = read(binding['assessment_policy'])
    events = [json.loads(line) for line in (root / binding['raw']).read_text().splitlines() if line.strip()]
    original_events = [json.loads(line) for line in (root / binding['original_raw']).read_text().splitlines() if line.strip()]
    original_assessor = load('shadow_sign_original_assessor', binding['original_assessor'])
    original_policy = read(binding['original_assessment_policy'])
    original = original_assessor.assess(original_events, read(binding['original_result'])['exit'], original_policy, checks, run_binding=read(binding['original_metadata']))
    assert original == read(binding['original_assessment'])
    assert original['complete'] and not original['errors'] and not original['fixture_setup_errors']
    replay = assessor.assess(events, 0, policy, checks, run_binding=read(binding['metadata']))
    assert replay == assessment
    rows = [row for row in events if row.get('action') == 'test_status']
    ends = [row for row in events if row.get('action') == 'test_end']
    targets = {(test, name) for test, names in policy['target_subtests'].items() for name in names}
    expected = {(test, name) for test, names in policy['expected_subtests'].items() for name in names}
    assert len(expected) == 98 and len(targets) == 8 and targets <= expected
    assert original_policy['expected_subtests'] == policy['expected_subtests']
    assert original_policy['target_subtests'] == policy['target_subtests']
    original_rows = [row for row in original_events if row.get('action') == 'test_status']
    assert len(original_rows) == 98 and {(row['test'], row['subtest']) for row in original_rows} == expected
    assert {(row['test'], row['subtest']) for row in original_rows if row['status'] == 'FAIL'} == targets
    assert all(row['status'] == 'PASS' for row in original_rows if (row['test'], row['subtest']) not in targets)
    assert len(rows) == 98 and {(row['test'], row['subtest']) for row in rows} == expected
    assert all(row['status'] == 'PASS' for row in rows)
    assert len(ends) == 16 and len({row['test'] for row in ends}) == 16 and all(row['status'] == 'OK' for row in ends)
    assert len(assessment['regression_signature']) == 106
    assert not assessment['unexpected']
    runpy.run_path(str(Path(__file__).with_name('supplemental_validation.py')))['verify'](root, inputs)
    return assessment
