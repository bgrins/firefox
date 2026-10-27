import json
import math
import sys


def validate(payload):
    assert payload['compatMode'] == 'CSS1Compat'
    expected = [(axis, base, extra, sign) for axis in ('x', 'y')
                for base in (16, 8388600) for extra in (0, 9)
                for sign in (-1, 1)]
    rows = payload['rows']
    assert len(rows) == len(expected)
    results = []
    for row, (axis, base, extra, sign) in zip(rows, expected):
        assert (row['axis'], row['base'], row['extra'], row['sign']) == (axis, base, extra, sign)
        assert row['key'] == f'{axis}-{base}-{extra}-{sign}'
        assert row['expected'] == sign * (base + extra)
        assert row['recoveryExpected'] == sign * base
        assert row['first'] == row['repeat'] == row['restored']
        matched = {}
        for phase in ('first', 'repeat', 'recovery', 'restored'):
            value = row[phase]
            margin = 0 if phase == 'recovery' else sign * extra
            coordinate = sign * base + margin
            assert type(value['parentMatches']) is bool and value['parentMatches']
            assert type(value['singleBox']) is bool and value['singleBox']
            for field in ('offset', 'base', 'margin', 'width', 'height', 'geometricOffset'):
                assert type(value[field]) in (int, float) and math.isfinite(value[field])
            assert value['offset'] == int(value['offset'])
            assert value['base'] == sign * base and value['margin'] == margin
            assert value['position'] == 'absolute' and value['transform'] == 'none'
            assert value['zoom'] == '1'
            assert value['width'] == 4 and value['height'] == 4
            assert type(value['hostRect']) is list and len(value['hostRect']) == 4
            assert all(type(v) in (int, float) and math.isfinite(v) for v in value['hostRect'])
            assert value['hostRect'] == [0, 0, 100, 100]
            assert value['geometricOffset'] == coordinate
            matched[phase] = value['offset'] == coordinate
        results.append(dict(key=row['key'], matched=matched,
                            observed=row['first']['offset'], expected=row['expected']))
    return dict(calibrated=len(results), stable=len(results), rows=results,
                matching={phase: sum(row['matched'][phase] for row in results)
                          for phase in ('first', 'repeat', 'recovery', 'restored')})


if __name__ == '__main__':
    print(json.dumps(validate(json.load(open(sys.argv[1]))), indent=2))
