import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / 'raw.json').read_bytes())
rows = data['rows']
assert data['count'] == len(rows) == 54
operations = ['mod', 'rem', 'round', 'division', 'cancellation', 'zeroProduct']
expected_order = [(unit, operation, basis) for unit in ['em', 'rem', 'cqw']
    for operation in operations for basis in [10, 0, 10]]
assert [(r['unit'], r['operation'], r['basis']) for r in rows] == expected_order
mismatches = []
for row in rows:
    unit, operation, basis = row['unit'], row['operation'], row['basis']
    expected = 10 if operation in ['cancellation', 'zeroProduct'] else (
        0 if basis == 0 else 10 + 4*basis if operation == 'round' else
        11 if operation == 'division' else 10 + basis)
    assert row['supported'] and row['expected'] == expected
    for control in ['resolved', 'literal']:
        assert row[control]['rect'] == expected
        assert float(row[control]['width'].removesuffix('px')) == expected
    assert row['calibration']['rect'] == basis
    assert float(row['calibration']['width'].removesuffix('px')) == basis
    absolute = 14 if operation == 'round' else 10 if operation in ['cancellation', 'zeroProduct'] else 11
    assert row['absolute']['rect'] == absolute
    assert float(row['absolute']['width'].removesuffix('px')) == absolute
    assert float(row['target']['width'].removesuffix('px')) == row['target']['rect']
    if row['target']['rect'] != expected:
        assert basis == 0 and operation in ['mod', 'rem', 'round']
        assert row['target']['rect'] == 10 and expected == 0
        mismatches.append({'unit':unit, 'operation':operation, 'actual':10, 'expected':0})
assert len(mismatches) == 9
print(json.dumps({'rows':54, 'target_matches':45, 'target_mismatches':mismatches,
    'all_54_pixel_literal_controls_agree':True, 'all_54_unit_calibrations_pass':True,
    'all_54_fixed_absolute_controls_pass':True, 'accepted_fix_increment':0}, indent=2))
