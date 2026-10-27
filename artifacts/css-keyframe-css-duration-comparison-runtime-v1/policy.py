import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROSTER = json.loads((HERE / 'ROSTER.json').read_text())
EXPECTED = {(test, name) for test, names in ROSTER['expected_subtests'].items() for name in names}
DURATION = '/css/css-animations/css-duration-reactivation.html'
MANDATORY = {key for key in EXPECTED if key[0] == DURATION}
OBSERVATIONAL = {key for key in EXPECTED if key[0] in {
    '/css/css-animations/responsive/fill-forwards-viewport-units.html',
    '/web-animations/responsive/fill-forwards-viewport-units.html'} or key[1] ==
    'ordinary keyframe attr initialization: attribute cache resets between keyframes'}
ROWS = json.loads((HERE / 'OBSERVED-ROWS.json').read_text())
METADATA = {(r['test'], r['subtest']): (r.get('expected', r['status']), r.get('known_intermittent', [])) for r in ROWS}


def assess(actual, reference, phase):
    differences, improvements, errors = [], [], []
    if set(actual) != EXPECTED or set(reference) != EXPECTED:
        return differences, improvements, ['incomplete exact182 identity map']
    if phase not in ('baseline', 'candidate', 'restored'):
        return differences, improvements, ['unknown phase']
    for key in sorted(EXPECTED):
        value, original = actual[key], reference[key]
        metadata = (value['effective_expected'], value['known_intermittent'])
        if (value['status'] not in ('PASS', 'FAIL') or metadata != METADATA[key]
            or value['expected'] != (None if value['status'] == value['effective_expected'] else value['effective_expected'])):
            errors.append('status/metadata drift: ' + str(key))
        changed = value != original
        if changed:
            differences.append({'baseline': original, 'actual': value, 'observational_only': key in OBSERVATIONAL})
        if key in OBSERVATIONAL:
            continue
        if phase == 'candidate' and key in MANDATORY:
            wanted = {'test': key[0], 'subtest': key[1], 'status': 'PASS', 'message': None,
                      'expected': None, 'effective_expected': 'PASS', 'known_intermittent': []}
            if value != wanted:
                errors.append('duration landing must pass: ' + str(key))
            if original['status'] == 'FAIL' and value == wanted:
                improvements.append({'baseline': original, 'actual': value})
        elif changed:
            errors.append('non-observational control/original/restored change: ' + str(key))
    if phase == 'candidate' and len(improvements) != 2:
        errors.append('both observed duration reuse failures must be repaired')
    return differences, improvements, errors
