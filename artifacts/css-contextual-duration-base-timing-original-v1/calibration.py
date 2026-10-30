import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def require(kind, observations):
    if kind.startswith('depth-'):
        path = ROOT / 'artifacts/css-contextual-duration-finite-depth-candidate-v1/comparison.py'
        spec = importlib.util.spec_from_file_location('existing_depth_calibration', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.require_original_calibration(observations)
        return
    if kind.startswith('same-element-'):
        filename = kind + '.json'
        reference = json.loads((ROOT / 'artifacts/css-contextual-duration-same-element-original-runtime-1/progress-records' / filename).read_text())['observations']
        for mode in (['literal'] if kind.endswith('acyclic') else ['literal500', 'literal1000']):
            assert observations[mode] == reference[mode]
        return
    assert kind == 'masked-base-acyclic'
    literal = observations['literal']
    assert all(member['animation'] and member['effect'] for member in literal['membership'])
    for snapshot in [literal['initial'], literal['beforeMembership'], literal['afterMembership']]:
        assert abs(snapshot['font'] - 32) <= .02
        assert snapshot['timings'][0]['duration'] == 2000
        assert all(item['time'] == 750 and item['state'] == 'paused' for item in snapshot['timings'])
    assert abs(literal['initial']['opacity'] - .75) <= .0001
    assert literal['initial']['timings'][1]['duration'] == 1000
    assert abs(literal['initial']['timings'][1]['progress'] - .75) <= .0001
    assert all(abs(sample['value'] - .375) <= .0001 for sample in literal['samples'])
    for snapshot in [literal['beforeMembership'], literal['afterMembership']]:
        assert abs(snapshot['opacity'] - .375) <= .0001
        assert snapshot['timings'][1]['duration'] == 2000
        assert abs(snapshot['timings'][1]['progress'] - .375) <= .0001


def report(directory, collection, policy):
    results = {}
    for filename, rule in policy['record_kinds'].items():
        receipt = collection['records'].get(filename)
        if not receipt or not receipt['schema_valid']:
            results[filename] = {'calibrated': False, 'reason': 'Missing or invalid record'}
            continue
        try:
            body = (directory / filename).read_bytes()
            assert hashlib.sha256(body).hexdigest() == receipt['sha256']
            require(rule['kind'], json.loads(body)['observations'])
            results[filename] = {'calibrated': True, 'reason': None}
        except (AssertionError, KeyError, ValueError, TypeError) as error:
            results[filename] = {'calibrated': False, 'reason': repr(error)}
    return {'records': results, 'all_calibrated': len(results) == 7 and all(row['calibrated'] for row in results.values()),
            'scope': 'Literal controls for all kinds; both initial snapshots additionally for depth. Same-element and masked contextual outcomes are hypotheses, not calibration requirements.',
            'callback_outcomes_are_separate': True, 'native_acceptance': False}
