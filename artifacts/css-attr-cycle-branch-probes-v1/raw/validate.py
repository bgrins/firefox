def summarize(value):
    names = ['raw-literal', 'typed-literal', 'typed-self-bare', 'typed-self-raw',
             'genuine-typed-self', 'nested-bare', 'nested-raw', 'bare-other',
             'typed-string-self-bare', 'bare-missing', 'taken-bare-fallback-cycle',
             'unused-bare-fallback-cycle', 'quoted-function-control']
    assert isinstance(value['userAgent'], str) and value['userAgent']
    assert value['typedSupported'] is True
    rows = value['rows']
    assert [row['id'] for row in rows] == names
    for row in rows:
        assert isinstance(row['observed'], str) and isinstance(row['repeat'], str)
        assert row['repeat'] == row['observed']
    return {'userAgent': value['userAgent'], 'typedSupported': value['typedSupported'],
            'rows': rows,
            'differences': [row['id'] for row in rows if row['observed'] != row['expected']],
            'calibration_failures': [row['id'] for row in rows if row.get('calibration') and row['observed'] != row['expected']]}
