import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPSULE = ROOT / 'artifacts/css-move-before-promotion-v1'
PHASE = ROOT / 'artifacts/css-move-before-promotion-runtime-1/candidate-wpt'
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replay():
    for name, pin in read(HERE / 'REFERENCES.json').items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin
    policy = read(CAPSULE / 'POLICY.json')
    settings = policy['wpt']
    expected_policy = dict(settings, tests={test: 'testharness' for test in settings['expected_subtests']}, held_subtests={})
    expected_policy['regression_subtests'] = {test: [name for name in names if name not in settings['target_subtests'].get(test, [])] for test, names in settings['expected_subtests'].items()}
    expected_policy['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    assert read(PHASE / 'ASSESSMENT-POLICY.json') == expected_policy
    result = read(PHASE / 'RESULT.json')
    assert result == {'comparison_gate_passed': False, 'execution_error': None, 'exit': 0,
                      'native_fix_acceptance': False, 'preservation_verified': True, 'success': False}
    assert read(PHASE / 'PRE.json') == read(PHASE / 'POST.json')
    metadata = read(PHASE / 'APPLICATION-METADATA.json')
    assert metadata == read(PHASE / 'APPLICATION-METADATA-POST.json')
    cleanup = read(PHASE / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    events = [json.loads(line) for line in (PHASE / 'raw.jsonl').read_text().splitlines()]
    checks = load('revalidation_checks', ROOT / settings['checks_helper'])
    old = load('failed_final_assessor', CAPSULE / 'assess.py')
    original = old.assess(events, 0, expected_policy, checks, run_binding=metadata)
    assert json.loads(json.dumps(original)) == read(PHASE / 'ASSESSMENT.json')
    assert original['complete'] and original['errors'] == [] and original['fixture_setup_errors'] == []
    assert original['comparison_errors'] == ['final signatures differ outside exact seven obsolete expectation fields']
    assert not original['comparison_gate_passed']
    corrected = load('corrected_final_assessor', HERE / 'assess.py')
    assessment = corrected.assess(events, 0, expected_policy, checks, run_binding=metadata)
    expected = copy.deepcopy(original)
    expected['comparison_errors'] = []
    expected['comparison_gate_passed'] = True
    assert assessment == expected
    assert len(assessment['rows']) == 70 and all(row['status'] == 'PASS' for row in assessment['rows'])
    assert len(assessment['ends']) == 12 and all(row['status'] == 'OK' for row in assessment['ends'])
    prior = old.projected_candidate(policy)
    actual = corrected.projected_candidate(policy)
    differences = []
    for a, b in zip(prior, actual):
        if a != b:
            assert dict(a, intermittent_field_present=True) == b
            assert a['known_intermittent'] == b['known_intermittent'] == []
            differences.append({'test': a['test'], 'subtest': a['subtest'],
                                'old_intermittent_field_present': False, 'correct_intermittent_field_present': True})
    assert len(prior) == len(actual) == 82 and len(differences) == 7
    assert {d['subtest'] for d in differences} == set(policy['deleted_metadata']['expected_fail_subtests'])
    return assessment, differences
