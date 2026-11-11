import json
from pathlib import Path


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def constant(value):
        raise ValueError('Non-finite JSON number: ' + value)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def validate(rows, cases):
    admitted = [case for case in cases if case['bridge_eligible']]
    if type(rows) is not list or len(rows) != len(admitted):
        raise ValueError('Wrong model row count/type')
    for row, case in zip(rows, admitted):
        if type(row) is not list or len(row) != 4:
            raise ValueError('Wrong model row shape')
        if type(row[0]) is not str or row[0] != case['tail']:
            raise ValueError('Wrong model input string')
        if type(row[1]) is not bool or row[1] is not False or type(row[3]) is not bool or row[3] is not False:
            raise ValueError('Wrong model-only error flags')
        observation = row[2]
        if type(observation) is not list or len(observation) != 7:
            raise ValueError('Wrong observation shape')
        for codes in observation[:5]:
            if type(codes) is not list or any(type(code) is not int or not 0 <= code < 128 for code in codes):
                raise ValueError('Expected lists of ASCII natural numbers')
        if type(observation[5]) is not bool or type(observation[6]) is not bool:
            raise ValueError('Expected exact Boolean observation flags')
    return rows


def read(path, cases):
    return validate([strict_json(line) for line in Path(path).read_text().splitlines()], cases)
