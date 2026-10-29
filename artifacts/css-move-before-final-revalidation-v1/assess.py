import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-move-before-paired-browser-v1/assess.py'
spec = importlib.util.spec_from_file_location('move_historical_assessor', SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)
signature = implementation.signature
bound_run_info = implementation.bound_run_info


def projected_candidate(settings):
    item = settings['historical_candidate_assessment']
    raw = (ROOT / item['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    prior = json.loads(raw)
    assert prior['complete'] and prior['comparison_gate_passed']
    assert len(prior['rows']) == 70 and len(prior['ends']) == 12
    assert all(row['status'] == 'PASS' for row in prior['rows'])
    test = '/dom/nodes/moveBefore/moveBefore-child-list-selector-invalidation.html'
    names = settings['deleted_metadata']['expected_fail_subtests']
    assert len(names) == len(set(names)) == 7
    rows = [signature(row) for row in prior['rows'] + prior['ends']]
    for name in names:
        matches = [row for row in rows if row['kind'] == 'test_status' and row['test'] == test and row['subtest'] == name]
        assert len(matches) == 1
        row = matches[0]
        assert row['status'] == 'PASS' and row['expected'] == 'FAIL' and row['expected_field_present']
        assert row['known_intermittent'] == [] and row['intermittent_field_present']
        row.update(expected='PASS', expected_field_present=False)
    return sorted(rows, key=lambda row: (row['test'], row['kind'], row['subtest'] or ''))


def assess(events, code, policy, checks, original=None, run_binding=None):
    assert original is None
    result = implementation.assess(events, code, policy, checks, run_binding=run_binding)
    settings = json.loads((ROOT / 'artifacts/css-move-before-promotion-v1/POLICY.json').read_bytes())
    expected = projected_candidate(settings)
    actual = sorted([signature(row) for row in result['rows'] + result['ends']],
                    key=lambda row: (row['test'], row['kind'], row['subtest'] or ''))
    errors = []
    if code != 0:
        errors.append('final installed WPT must exit zero after metadata removal')
    if len(result['rows']) != 70 or any(row['status'] != 'PASS' for row in result['rows']):
        errors.append('final installed suite requires 70 PASS callbacks')
    if len(result['ends']) != 12 or any(row['status'] != 'OK' for row in result['ends']):
        errors.append('final installed suite requires 12 OK endings')
    if actual != expected:
        errors.append('final signatures differ outside exact seven obsolete expectation fields')
    result['comparison_errors'] = errors
    result['comparison_gate_passed'] = result['complete'] and not errors
    result['oracle_caveat'] = 'Historical pair retains old metadata and exit1; final installed suite requires exact metadata projection,70PASS,12OK,exit0.'
    return result
