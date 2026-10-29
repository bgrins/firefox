import hashlib
import json


def verify(root, inputs):
    binding = inputs['final_revalidation']
    def read(key):
        name = binding[key]
        body = (root / name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == inputs['evidence_pins'][name]
        return json.loads(body)
    result = read('result')
    assert result['success'] and result['preservation_verified'] and result['historical_records_unchanged']
    assert result['browser_execution_performed'] is False and result['reassessed_actual_completed_run'] is True
    assert result['original_browser_child_exit'] == 0 and result['original_wrapper_exit'] == 1
    assert result['accepted'] is False and result['epoch_sha256'] == inputs['initial_epoch']
    assert result['observed_subtests'] == 70 and result['observed_endings'] == 12
    for key, field in [('raw', 'raw_sha256'), ('original_result', 'original_result_sha256'), ('original_assessment', 'original_assessment_sha256')]:
        name = binding[key]
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == result[field] == inputs['evidence_pins'][name]
    original_result = read('original_result')
    assert original_result['success'] is False and original_result['comparison_gate_passed'] is False
    assert original_result['exit'] == 0 and original_result['preservation_verified'] and original_result['execution_error'] is None
    original, corrected = read('original_assessment'), read('assessment')
    expected = dict(original, comparison_errors=[], comparison_gate_passed=True)
    assert corrected == expected and corrected['complete']
    assert all(corrected[key] == [] for key in ('errors', 'fixture_setup_errors', 'infrastructure_faults', 'unexpected', 'comparison_errors'))
    assert len(corrected['rows']) == 70 and all(row['status'] == 'PASS' for row in corrected['rows'])
    assert len(corrected['ends']) == 12 and all(row['status'] == 'OK' for row in corrected['ends'])
    assert len(corrected['regression_signature']) == 31
    assert read('pre') == read('post')
    changes = read('diff')
    assert len(changes) == 7 and {row['subtest'] for row in changes} == set(binding['changed_subtests'])
    assert all(row['test'] == '/dom/nodes/moveBefore/moveBefore-child-list-selector-invalidation.html' and row['old_intermittent_field_present'] is False and row['correct_intermittent_field_present'] is True for row in changes)
