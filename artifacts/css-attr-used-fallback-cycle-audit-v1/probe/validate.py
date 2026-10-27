def summarize(value):
    names = ['missing-bare-self', 'missing-raw-self', 'invalid-number-self', 'invalid-unit-self',
             'missing-unit-self', 'missing-bare-mutual', 'missing-bare-mutual-reordered',
             'direct-var-self', 'missing-typed-self', 'missing-bare-acyclic',
             'missing-bare-ready-provider', 'present-bare-unused-self', 'valid-number-unused-self']
    assert isinstance(value['userAgent'], str) and value['userAgent']
    assert value['typedSupported'] is True
    rows = value['rows']
    assert [row['id'] for row in rows] == names
    for row in rows:
        assert isinstance(row['observed'], str) and isinstance(row['repeat'], str)
        assert row['repeat'] == row['observed']
    differs = lambda row: row['observed'] != row['expected'] or row['color'] != row['expectedColor']
    return {'userAgent': value['userAgent'], 'typedSupported': value['typedSupported'],
            'rows': rows, 'differences': [row['id'] for row in rows if differs(row)],
            'calibration_failures': [row['id'] for row in rows if row.get('calibration') and differs(row)]}
