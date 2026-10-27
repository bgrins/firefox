def normalized(row):
    return {'status': row['status'], 'message': row.get('message'),
            'expected': row.get('expected', row['status']),
            'known_intermittent': row.get('known_intermittent', [])}


def values(rows):
    result = {(r['test'], r['subtest']): normalized(r) for r in rows}
    assert len(result) == len(rows) == 77
    return result


def check(rows, policy, phase, baseline=None):
    actual = values(rows)
    controls = {(r['test'], r['subtest']): normalized(r) for r in policy['unchanged_control_rows']}
    required = {(r['test'], r['subtest']) for r in policy['candidate_mandatory_pass']}
    assert len(controls) == 55 and len(required) == 22 and not (set(controls) & required)
    assert set(actual) == set(controls) | required
    reference = controls if phase == 'original' else baseline
    assert reference is not None
    assert all(actual[k] == reference[k] for k in controls), 'controls equal admitted fresh original'
    if phase == 'candidate':
        assert baseline is not None
        for key in required:
            assert actual[key]['status'] == 'PASS' and actual[key]['message'] in (None, '')
            assert actual[key]['expected'] == baseline[key]['expected'], 'metadata unchanged'
            assert actual[key]['known_intermittent'] == baseline[key]['known_intermittent']
    elif phase == 'restored':
        assert actual == baseline, 'exact fresh original restoration'
    return actual
