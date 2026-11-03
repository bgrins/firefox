import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROSTER = json.loads((HERE / 'ROSTER.json').read_bytes())


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def close(a, b):
    return number(a) and number(b) and abs(a - b) < 0.06


def assess(script, report):
    expected = ROSTER[script]['case']
    assert report['schema'] == 'root-self-animation-order-v1'
    assert isinstance(report['userAgent'], str) and report['userAgent']
    assert report['errors'] == [] and report['cleanup'] is True
    assert len(report['cases']) == 1
    row = report['cases'][0]
    assert {key: row[key] for key in expected} == expected
    assert row['error'] is None
    initial, configured = row['initial'], row['configured']
    assert number(initial['rem']) and number(initial['rlh'])
    assert all(number(configured[k]) for k in ('fontSize', 'lineHeight', 'rem', 'rlh'))
    controls = {
        'initialMetrics': initial['rem'] > 0 and initial['rlh'] > 0,
        'configuredRoot': close(configured['fontSize'], 23) and close(configured['lineHeight'], 37),
        'configuredMetricProxies': close(configured['rem'], 23) and close(configured['rlh'], 37),
    }
    assert close(row['normativeExpected'], 46)
    disturbance = row['disturbance']
    assert disturbance['kind'] == 'em-cancel' and number(disturbance['value'])
    assert close(disturbance['expected'], 2 * initial['rem'])
    controls['emCalibration'] = close(disturbance['value'], 2 * initial['rem'])
    if expected['barrier'] == 'root-read':
        before = row['preconditionRead']
        assert number(before['fontSize']) and number(before['lineHeight'])
        controls['restoredRootRead'] = close(before['fontSize'], 23) and close(before['lineHeight'], 37)
    else:
        assert row['preconditionRead'] is None
    animation = row['animation']
    pseudo = expected['target'] == 'root-pseudo-font'
    assert animation['targetIsRoot'] is pseudo
    assert animation['pseudoElement'] == ('::before' if pseudo else None)
    controls['pausedMidpoint'] = (animation['currentTime'] == 500 and animation['playState'] == 'paused'
                                  and number(animation['progress']) and abs(animation['progress'] - 0.5) < 1e-9)
    assert row['controls'] == controls
    assert [sample['timing'] for sample in row['samples']] == ['first', 'settled']
    samples = []
    for sample in row['samples']:
        assert isinstance(sample['raw'], str) and sample['raw'].endswith('px')
        assert close(float(sample['raw'][:-2]), sample['value'])
        samples.append(dict(sample, expected=46, normative_match=close(sample['value'], 46)))
    assert all(number(row['postStateAfterBothSamples'][k]) for k in ('fontSize', 'lineHeight', 'rem', 'rlh'))
    return {'script': script, 'cases': 1, 'case': expected, 'samples': samples,
            'controls': controls, 'controls_valid': all(controls.values()),
            'control_failures': [key for key, value in controls.items() if not value],
            'cleanup': True, 'full34_prerequisite_verified': False,
            'native_cause_proved': False, 'candidate_acceptance': False}


if __name__ == '__main__':
    assert len(sys.argv) == 3
    print(json.dumps(assess(sys.argv[1], json.loads(Path(sys.argv[2]).read_bytes())), indent=2))
