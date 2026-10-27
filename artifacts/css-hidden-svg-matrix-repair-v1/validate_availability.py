import math


def validate(payload):
    assert payload['compatMode'] == 'CSS1Compat'
    expected = [(method, mode) for method in ('getCTM', 'getScreenCTM')
                for mode in ('detached', 'display-none', 'defs', 'singular')]
    assert len(payload['rows']) == 8
    for row, (method, mode) in zip(payload['rows'], expected):
        assert row['key'] == f'{method}-{mode}'
        assert row['method'] == method and row['mode'] == mode
        assert row['connected'] is (mode != 'detached')
        for phase in ('first', 'repeat'):
            value = row[phase]
            assert value['kind'] in ('matrix', 'null', 'exception')
            if value['kind'] == 'matrix':
                assert set(value) == {'kind', 'values'} and len(value['values']) == 6
                assert all(type(n) in (int, float) and math.isfinite(n) for n in value['values'])
            elif value['kind'] == 'null':
                assert set(value) == {'kind'}
            else:
                assert set(value) == {'kind', 'name'} and isinstance(value['name'], str) and value['name']
    return {'rows': payload['rows'], 'stable': sum(r['first'] == r['repeat'] for r in payload['rows'])}
