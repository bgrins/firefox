import hashlib
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
CONTEXT = 'sign(1em - 16px)'
CASES = [
    ('positive-infinities', 'infinity', 'infinity'),
    ('negative-infinities', '-infinity', 'infinity'),
    ('contextual-infinities', 'infinity * ' + CONTEXT, 'infinity'),
    ('positive-finite-infinite-step', '1', 'infinity'),
    ('negative-finite-infinite-step', '-1', 'infinity'),
    ('zero-infinite-step', '0', 'infinity'),
    ('nan-infinite-step', 'NaN', 'infinity'),
    ('contextual-finite-infinite-step', CONTEXT, 'infinity'),
    ('infinite-finite-step', 'infinity', '1'),
    ('contextual-infinite-finite-step', 'infinity * ' + CONTEXT, '1'),
    ('finite-zero-step', '1', '0'),
    ('finite-nan-step', '1', 'NaN'),
    ('finite-contextual-step', '1', 'infinity * ' + CONTEXT),
    ('infinite-contextual-step', 'infinity', 'infinity * ' + CONTEXT),
]
MODES = ['nearest', 'up', 'down', 'to-zero']
FONTS = [8, 16, 32, 8]
BOUNDARY = [
    ('positive-up', 'round(up, .65, .1)', '.7', 1),
    ('positive-nearest', 'round(nearest, .66, .1)', '.7', 1),
    ('negative-down', 'round(down, -.65, .1)', '-.7', -1),
    ('negative-nearest', 'round(nearest, -.66, .1)', '-.7', -1),
    ('positive-down-control', 'round(down, .65, .1)', '.6', 1),
    ('positive-to-zero-control', 'round(to-zero, .65, .1)', '.6', 1),
    ('exact-step-control', 'round(up, .65, .125)', '.75', 1),
    ('explicit-dyadic-up', 'round(up, 0.64999997615814208984375, 0.100000001490116119384765625)',
     'calc(7 * 0.100000001490116119384765625)', 1),
]


def sign(value):
    return (value > 0) - (value < 0)


def numeric(text, font):
    if text == CONTEXT:
        return sign(font - 16)
    if text == 'infinity * ' + CONTEXT:
        return math.inf * sign(font - 16)
    return float({'infinity': 'inf', '-infinity': '-inf', 'NaN': 'nan'}.get(text, text))


def token(value):
    if math.isnan(value):
        return 'NaN'
    if math.isinf(value):
        return 'infinity' if value > 0 else '-infinity'
    return str(int(value))


def encoded_round(mode, value, step):
    step = abs(step)
    if math.isnan(value) or math.isnan(step) or step == 0 or math.isinf(value) and math.isinf(step):
        return 0
    if math.isinf(value):
        result = value
    elif math.isinf(step):
        if value == 0 or mode in ('nearest', 'to-zero'):
            result = 0
        elif mode == 'up':
            result = math.inf if value > 0 else 0
        else:
            result = -math.inf if value < 0 else 0
    else:
        quotient = value / step
        coefficient = {'up': math.ceil(quotient), 'down': math.floor(quotient),
                       'to-zero': math.trunc(quotient), 'nearest': math.floor(quotient + 0.5)}[mode]
        result = coefficient * step
    return 0.5 + 0.25 * sign(result)


def expression(mode, value, step):
    return f'calc(0.5 + 0.25 * sign(round({mode}, {value}, {step})))'


def main():
    raw = read(HERE / 'raw.json')
    before, after = read(HERE / 'PRE.json'), read(HERE / 'POST.json')
    assert before == after and len(before) == 11
    assert all(set(item) == {'sha256', 'identity', 'symlink'} and
               len(item['identity']) == 2 and len(item['sha256']) == 64 for item in before.values())
    assert {name: item['symlink'] for name, item in before.items() if item['symlink'] is not None} == {
        'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini':
        '/Users/bgrins/code/firefox/objdir-full.noindex/build/application.ini'}
    assert before['servo/components/style/values/generics/calc.rs']['sha256'] == 'b9a36918f1291b2c08cfb6d83aca73eb309185d1d2691961d6334b7bc69d1274'
    for name in ('css-round-nonfinite-classification-probe-v1', 'css-round-parse-bound-reconstruction-probe-v1'):
        path = 'artifacts/' + name + '/observe.js'
        assert sha(ROOT / path) == before[path]['sha256']
    boundary = raw['boundary']['rows']
    assert [row['id'] for row in boundary] == [case[0] for case in BOUNDARY]
    boundary_issues, boundary_diff = [], []
    for row, (identity, target, reference, direction) in zip(boundary, BOUNDARY):
        assert row['expression'] == target and row['referenceExpression'] == reference
        diff = f'{target} - {reference}' if direction > 0 else f'{reference} - {target}'
        inputs = {'target': f'sign({diff})', 'reference': f'sign({reference} - {reference})',
                  'literalZero': '0', 'literalOne': '1',
                  'nonzeroAmplifier': 'sign(0.7000000476837158203125 - 0.699999988079071044921875)'}
        assert row['inputs'] == inputs and row['expectedTarget'] == '0'
        assert all(set(row[key]) == set(inputs) for key in ('support', 'specified', 'first', 'repeat'))
        first = row['first']
        calibrated = all(value is True for value in row['support'].values()) and all(row['specified'].values()) and first == row['repeat']
        calibrated = calibrated and {key: first[key] for key in ('reference', 'literalZero', 'literalOne', 'nonzeroAmplifier')} == {'reference': '0', 'literalZero': '0', 'literalOne': '1', 'nonzeroAmplifier': '1'}
        assert row['calibrated'] is calibrated and row['matchesExpected'] is (first['target'] == '0')
        if not calibrated:
            boundary_issues.append(identity)
        if first['target'] != '0':
            boundary_diff.append(identity)
    snapshots = raw['nonfinite']['snapshots']
    expected_roster = [(identity, mode, phase, font) for phase, font in enumerate(FONTS) for identity, _, _ in CASES for mode in MODES]
    assert [(row['id'], row['mode'], row['phase'], row['font']) for row in snapshots] == expected_roster
    assert raw['nonfinite']['caseCount'] == 56 and raw['nonfinite']['snapshotCount'] == 224
    assert raw['nonfinite']['unsupportedIsPass'] is False and raw['nonfinite']['nativeFixAccepted'] is False
    assert raw['nonfinite']['userAgent'] == raw['userAgent']
    definitions = {identity: (value, step) for identity, value, step in CASES}
    issues, differences, resolved_differences = [], [], []
    for row in snapshots:
        identity, mode, font = row['id'], row['mode'], row['font']
        source_value, source_step = definitions[identity]
        value, step = numeric(source_value, font), numeric(source_step, font)
        expected = encoded_round(mode, value, step)
        assert row['expected'] == expected
        assert row['authored'] == expression(mode, source_value, source_step)
        assert row['resolvedExpression'] == expression(mode, token(value), token(step))
        calibration = row['inputCalibration']
        assert calibration['expectedDifference'] == f'{font - 16}px' and calibration['expectedSignEncoding'] == 0.5 + 0.25 * sign(font - 16)
        good = row['supported'] is True and row['resolvedSupported'] is True and bool(row['specified']) and bool(row['resolvedSpecified'])
        good = good and row['actual'] == row['repeated'] and float(row['literal']) == expected
        good = good and calibration['font'] == f'{font}px' and calibration['difference'] == f'{font - 16}px'
        good = good and float(calibration['signEncoding']) == 0.5 + 0.25 * sign(font - 16)
        if not good:
            issues.append([identity, mode, row['phase']])
        if float(row['actual']) != expected:
            differences.append(row)
        if float(row['resolved']) != expected:
            resolved_differences.append(row)
    analysis = {'boundary_cases': len(boundary), 'boundary_calibration_failures': boundary_issues,
        'boundary_differences': boundary_diff, 'nonfinite_cases': 56, 'nonfinite_snapshots': len(snapshots),
        'calibration_issues': issues, 'nonfinite_differences': len(differences),
        'resolved_reference_differences': len(resolved_differences),
        'nonfinite_differences_by_id': dict(Counter(row['id'] for row in differences)),
        'nonfinite_differences_by_mode': dict(Counter(row['mode'] for row in differences)),
        'remaining_iframes': raw['remainingIframes'], 'preservation_verified': before == after,
        'native_acceptance': False, 'new_bug_count': 0}
    assert raw['remainingIframes'] == 0
    assert analysis == read(HERE / 'ANALYSIS.json')
    assert differences == read(HERE / 'NONFINITE-DIFFERENCES.json')
    print(json.dumps(analysis, indent=2))


if __name__ == '__main__':
    main()
