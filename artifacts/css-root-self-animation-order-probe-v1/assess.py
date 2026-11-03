import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / 'CASES.json').read_text())


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def close(a, b):
    return number(a) and number(b) and abs(a - b) < 0.06


def assess(report):
    assert report['schema'] == 'root-self-animation-order-v1'
    assert isinstance(report['userAgent'], str) and report['userAgent']
    assert report['errors'] == [] and report['cleanup'] is True
    assert len(report['cases']) == len(CASES) == 34
    rows, conditions = [], []
    for case, expected_case in zip(report['cases'], CASES):
        assert {key: case[key] for key in expected_case} == expected_case
        assert case['error'] is None
        initial, configured = case['initial'], case['configured']
        assert number(initial['rem']) and number(initial['rlh'])
        for key in ('fontSize', 'lineHeight', 'rem', 'rlh'):
            assert number(configured[key])
        controls = {
            'initialMetrics': initial['rem'] > 0 and initial['rlh'] > 0,
            'configuredRoot': close(configured['fontSize'], 23) and close(configured['lineHeight'], 37),
            'configuredMetricProxies': close(configured['rem'], 23) and close(configured['rlh'], 37),
        }
        base = initial[case['unit']]
        expected = 2 * base if case['target'] == 'root-font' else (
            2 * (23 if case['unit'] == 'rem' else initial['rlh']) if case['target'] == 'root-line'
            else 2 * (23 if case['unit'] == 'rem' else 37))
        assert close(case['normativeExpected'], expected)
        if case['history'] == 'none':
            assert case['disturbance'] is None
        else:
            disturbance = case['disturbance']
            assert disturbance['kind'] == case['history'] and number(disturbance['value'])
            if case['history'] == 'em-cancel':
                assert close(disturbance['expected'], 2 * initial['rem'])
                controls['emCalibration'] = close(disturbance['value'], 2 * initial['rem'])
            else:
                assert disturbance['property'] == ('lineHeight' if case['target'] == 'root-line' else 'fontSize')
                assert close(disturbance['expected'], expected)
                controls['ordinaryComparator'] = close(disturbance['value'], expected)
        if case['barrier'] == 'root-read':
            before = case['preconditionRead']
            assert number(before['fontSize']) and number(before['lineHeight'])
            controls['restoredRootRead'] = close(before['fontSize'], 23) and close(before['lineHeight'], 37)
        else:
            assert case['preconditionRead'] is None
        animation = case['animation']
        assert animation['targetIsRoot'] == (case['target'] in ('root-font', 'root-line', 'root-pseudo-font'))
        assert animation['pseudoElement'] == ('::before' if case['target'] == 'root-pseudo-font' else None)
        controls['pausedMidpoint'] = animation['currentTime'] == 500 and animation['playState'] == 'paused' and isinstance(animation['progress'], (int, float)) and abs(animation['progress'] - 0.5) < 1e-9
        assert case['controls'] == controls
        failures = [key for key, value in controls.items() if not value]
        conditions.append(dict(expected_case, controls=controls, failures=failures))
        assert [sample['timing'] for sample in case['samples']] == ['first', 'settled']
        for sample in case['samples']:
            assert sample['raw'].endswith('px') and number(sample['value'])
            assert close(float(sample['raw'][:-2]), sample['value'])
            rows.append(dict(expected_case, timing=sample['timing'], raw=sample['raw'], value=sample['value'],
                             expected=expected, normative_match=close(sample['value'], expected), control_failures=failures))
        assert all(number(case['postStateAfterBothSamples'][key]) for key in ('fontSize', 'lineHeight', 'rem', 'rlh'))
    comparisons = []
    indexed = {(r['unit'], r['target'], r['history'], r['barrier'], r['timing']): r for r in rows}
    for row in rows:
        if row['barrier'] != 'none' or row['history'] == 'none':
            continue
        observed = indexed[(row['unit'], row['target'], row['history'], 'root-read', row['timing'])]
        comparisons.append({key: row[key] for key in ('unit', 'target', 'history', 'timing')} | {
            'without_read': row['value'], 'with_root_read': observed['value'],
            'equal': close(row['value'], observed['value']),
            'control_failures_without': row['control_failures'], 'control_failures_with': observed['control_failures']})
    return {'cases': 34, 'samples': 68, 'controls_valid': all(not row['failures'] for row in conditions),
            'conditions': conditions, 'rows': rows, 'ordering_comparisons': comparisons,
            'native_cause_proved': False, 'candidate_acceptance': False,
            'scope': 'Target values are observations; controls and normative comparisons remain separate. No flush-count or Device-state inference.'}


if __name__ == '__main__':
    print(json.dumps(assess(json.loads(Path(sys.argv[1]).read_text())), indent=2))
