import json


def assess(output, code, policy):
    read = lambda path: json.loads(path.read_bytes())
    events = [json.loads(line) for line in (output / 'raw.jsonl').read_text().splitlines()]
    rows = [event for event in events if event.get('action') == 'test_status']
    ends = [event for event in events if event.get('action') == 'test_end']
    ids = ['integer', 'ordinary-repeat', 'subgrid-repeat', 'steps', 'bezier', 'linear-output', 'linear-second-position', 'time']
    prefix = 'Round infinite value constant-result admission: '
    assert len(rows) == 8 and {row['subtest'] for row in rows} == {prefix + key for key in ids}
    assert all(row['test'] == policy['target'] and row['status'] in ['PASS', 'FAIL'] for row in rows)
    assert len(ends) == 1 and ends[0]['test'] == policy['target'] and ends[0]['status'] == 'OK'
    assert not any(event.get('action') in ['crash', 'process_error'] or
                   (event.get('action') == 'log' and event.get('level') == 'ERROR') for event in events)
    assert code in [0, 1]
    observation = read(output / 'observation.json')
    assert observation['caseCount'] == 8 and observation['snapshotCount'] == len(observation['snapshots']) == 32
    assert observation['admissionPolicyObservationOnly'] and not observation['nativeFixAccepted']
    identities = {(row['id'], row['phase']) for row in observation['snapshots']}
    assert identities == {(key, phase) for key in ids for phase in range(4)}
    outcomes = {key: True for key in ids}
    for row in observation['snapshots']:
        phase = row['phase']
        font = [8, 16, 32, 8][phase]
        assert row['font'] == font
        assert row['input']['font'] == str(font) + 'px'
        assert row['input']['difference'] == str(font - 16) + 'px'
        assert float(row['input']['signEncoding']) == [.25, .5, .75, .25][phase]
        assert row['literalSupported'] and row['literalSpecified'] and row['literalComputed']
        assert row['computed'] == row['repeated']
        passed = row['supported'] and bool(row['specified']) and row['computed'] == row['literalComputed']
        outcomes[row['id']] = outcomes[row['id']] and passed
    for row in rows:
        assert row['status'] == ('PASS' if outcomes[row['subtest'].removeprefix(prefix)] else 'FAIL')
    return {'pass': sum(outcomes.values()), 'fail': len(outcomes) - sum(outcomes.values()),
            'snapshots': 32, 'calibration_errors': [], 'admission_outcomes': outcomes,
            'direct_context_is_diagnostic': True, 'native_fix_acceptance': False}
