import json


def expected_snapshot(depth, advanced):
    value = 32 if advanced else 16
    nodes = []
    def timing(duration):
        return {'duration': duration, 'progress': 1 if duration == 1000 else 0.75, 'time': 1500, 'state': 'paused'}
    for index in range(depth):
        duration = value * 1000 // 16
        output = 48 - value
        nodes.append({'font': value if index % 2 == 0 else output,
                      'lineHeight': output if index % 2 == 0 else value,
                      'duration': duration, 'timing': timing(duration)})
        value = output
    duration = value * 1000 // 16
    return {'rootFont': 32 if advanced else 16, 'opacity': 1 if value == 16 else 0,
            'leafDuration': duration, 'leaf': timing(duration), 'nodes': nodes}


def require_original_calibration(observations):
    literal = observations['literal']
    depth = literal['depth']
    assert depth in (1, 2, 4, 8)
    for mode, item in observations.items():
        assert item['mode'] == mode and item['depth'] == depth
        assert item['literalInitial'] == item['initial'] == expected_snapshot(depth, False)
    expected = expected_snapshot(depth, True)
    assert literal['beforeMembership'] == literal['afterMembership'] == expected
    assert all(sample['opacity'] == expected['opacity'] for sample in literal['samples'])
    assert all(member['animation'] and member['effect'] for member in literal['membership'])


def report(directory, collection, policy):
    results = {}
    for filename in policy['record_kinds']:
        receipt = collection['records'].get(filename)
        if not receipt or not receipt['schema_valid']:
            results[filename] = {'calibrated': False, 'reason': 'Missing or invalid record; no numeric inference'}
            continue
        try:
            observations = json.loads((directory / filename).read_text())['observations']
            require_original_calibration(observations)
            results[filename] = {'calibrated': True, 'reason': None}
        except (AssertionError, ValueError, KeyError, TypeError) as error:
            results[filename] = {'calibrated': False, 'reason': repr(error)}
    return {'records': results, 'all_calibrated': len(results) == 4 and all(r['calibrated'] for r in results.values()),
            'scope': 'Literal final and both initial snapshots only; contextual outcome remains the actual WPT verdict',
            'no_native_or_css_policy_inference': True}
