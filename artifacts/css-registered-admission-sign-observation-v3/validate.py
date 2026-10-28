import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / 'CASES.json').read_text())
ORDER = ['parentFontSize', 'value', 'raw', 'fontSize', 'lineHeight', 'width']
ACTUAL = {'value', 'raw', 'fontSize', 'lineHeight', 'width'}


def require(value, message):
    if not value:
        raise ValueError(message)


def summarize(payload):
    require(isinstance(payload, dict) and set(payload) == {'observation'}, 'payload')
    observation = payload['observation']
    require(isinstance(observation, dict) and set(observation) == {'userAgent', 'queryOrder', 'rows'}, 'observation')
    require(isinstance(observation['userAgent'], str) and observation['userAgent'], 'user agent')
    require(observation['queryOrder'] == ORDER, 'query order')
    rows = observation['rows']
    require(isinstance(rows, list) and len(rows) == len(CASES), 'row count')
    for row, case in zip(rows, CASES):
        require(isinstance(row, dict) and set(row) == {'id', 'registrationErrors', 'snapshots'}, 'row')
        require(row['id'] == case['id'], 'row identity/order')
        require(isinstance(row['registrationErrors'], list) and all(isinstance(x, str) for x in row['registrationErrors']), 'registration errors')
        require(isinstance(row['snapshots'], list) and len(row['snapshots']) == 2, 'snapshot count')
        for step, snapshot in enumerate(row['snapshots']):
            require(isinstance(snapshot, dict) and set(snapshot) == {'step', 'parentCSS', 'specifiedCSS', 'parentFontSize', 'actual'}, 'snapshot')
            require(type(snapshot['step']) is int and snapshot['step'] == step, 'step')
            require(all(isinstance(snapshot[key], str) for key in ['parentCSS', 'specifiedCSS', 'parentFontSize']), 'specified strings')
            require(isinstance(snapshot['actual'], dict) and set(snapshot['actual']) == ACTUAL, 'actual fields')
            require(all(isinstance(value, str) for value in snapshot['actual'].values()), 'actual strings')
    return copy.deepcopy(observation)


def compare(original, candidate):
    summarize({'observation': original})
    summarize({'observation': candidate})
    differences = []
    for before, after in zip(original['rows'], candidate['rows']):
        if before != after:
            differences.append({'id': before['id'], 'original': before, 'candidate': after})
    return {'unchanged': not differences, 'changed_cases': len(differences), 'differences': differences,
            'normative_verdict': 'not evaluated', 'native_fix_acceptance': False}


def checks():
    observation = {'userAgent': 'synthetic', 'queryOrder': ORDER, 'rows': []}
    for case in CASES:
        observation['rows'].append({'id': case['id'], 'registrationErrors': [], 'snapshots': [
            {'step': step, 'parentCSS': 'synthetic', 'specifiedCSS': 'synthetic', 'parentFontSize': '19px',
             'actual': {name: 'synthetic' for name in ACTUAL}} for step in range(2)]})
    payload = {'observation': observation}
    require(compare(summarize(payload), summarize(payload))['unchanged'], 'identity comparison')
    mutations = []
    for index in range(len(CASES)):
        for step in range(2):
            for name in ACTUAL:
                changed = copy.deepcopy(observation)
                changed['rows'][index]['snapshots'][step]['actual'][name] = 'changed'
                require(compare(observation, changed)['changed_cases'] == 1, 'lost field change')
        changed = copy.deepcopy(observation)
        changed['rows'][index]['registrationErrors'] = ['synthetic error']
        require(compare(observation, changed)['changed_cases'] == 1, 'lost registration error')
        missing = copy.deepcopy(payload)
        missing['observation']['rows'].pop(index)
        mutations.append(missing)
        duplicate = copy.deepcopy(payload)
        duplicate['observation']['rows'][index]['id'] = 'wrong'
        mutations.append(duplicate)
        for step in range(2):
            missing = copy.deepcopy(payload)
            missing['observation']['rows'][index]['snapshots'].pop(step)
            mutations.append(missing)
    for mutation in mutations:
        try:
            summarize(mutation)
        except ValueError:
            continue
        raise AssertionError('malformed capture accepted')
    return {'status': 'PASS', 'rows': len(CASES), 'snapshots': len(CASES) * 2,
            'field_mutations_detected': len(CASES) * 2 * len(ACTUAL),
            'registration_mutations_detected': len(CASES), 'malformed_captures_rejected': len(mutations),
            'browser_executed': False}


if __name__ == '__main__':
    print(json.dumps(checks(), indent=2))
