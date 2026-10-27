def normalized(row):
    return {'status': row['status'], 'message': row.get('message'),
            'expected': row.get('expected', row['status']),
            'known_intermittent': row.get('known_intermittent', [])}


def values(rows):
    assert all(r['status'] in ('PASS', 'FAIL') for r in rows)
    result = {(r['test'], r['subtest']): normalized(r) for r in rows}
    assert len(result) == len(rows) == 113
    return result


def check(rows, policy, phase, baseline=None):
    assert phase in ('original', 'candidate', 'restored')
    actual = values(rows)
    controls = {(r['test'], r['subtest']) for r in policy['exact_fresh_control_identities']}
    required = {(r['test'], r['subtest']) for r in policy['candidate_mandatory_pass']}
    assert len(controls) == 75 and len(required) == 38 and not (controls & required)
    assert set(actual) == controls | required
    if phase == 'original':
        return actual
    assert baseline is not None and set(baseline) == set(actual)
    assert all(actual[k] == baseline[k] for k in controls), 'controls equal fresh original'
    if phase == 'candidate':
        for key in required:
            assert actual[key]['status'] == 'PASS' and actual[key]['message'] in (None, '')
            assert actual[key]['expected'] == baseline[key]['expected'], 'metadata unchanged'
            assert actual[key]['known_intermittent'] == baseline[key]['known_intermittent']
    else:
        assert actual == baseline, 'exact fresh original restoration'
    return actual
