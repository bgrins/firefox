import importlib.util
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('followup_old20', HERE / 'classify20.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
DURATION = '/css/css-animations/css-duration-reactivation.html'
VIEWPORT = '/css/css-animations/responsive/fill-forwards-calibrated-viewport.html'
ATTR = '/css/css-animations/ordinary-keyframe-attr-initial.html'
EXPLORATORY = 'ordinary keyframe attr initialization: attribute cache resets between keyframes'
NUMBER = old.NUMBER


def read(name):
    return json.loads((HERE / name).read_text())


def decode(text):
    return json.loads(text, object_pairs_hook=old.unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def duration_failure(name, message):
    identity = re.fullmatch(r'CSS duration reactivation: (width|transform), (reuse after change|fresh after change|reuse without change)', name)
    match = re.fullmatch(r'assert_equals: first sample after CSS duration change: (\{.*\}) expected (40|20) but got (' + NUMBER + ')', message)
    if not identity or not match:
        raise ValueError('duration calibration or unrecognized failure')
    observation = decode(match[1])
    expected = 20 if identity[2] == 'reuse without change' else 40
    if (set(observation) != {'property', 'mode', 'observed'} or observation['property'] != identity[1]
        or observation['mode'] != identity[2] or not finite(observation['observed'])
        or observation['observed'] != float(match[3]) or float(match[2]) != expected
        or observation['observed'] == expected):
        raise ValueError('duration observation/assertion mismatch')
    return {'classification': 'CALIBRATED_DURATION_TARGET_MISMATCH', 'observation': observation,
            'is_independent_control': identity[2] != 'reuse after change'}


def viewport_failure(name, message):
    match = re.fullmatch(r'assert_approx_equals: target filled viewport value: (\{.*\}) expected (' + NUMBER + r') \+/- 1 but got (' + NUMBER + ')', message)
    if not match:
        raise ValueError('viewport calibration or unrecognized failure')
    observation = decode(match[1])
    mode = 'CSS Animation' if name.startswith('Late-start CSS Animation:') else 'WAAPI animation'
    if set(observation) != {'mode', 'observations'} or observation['mode'] != mode:
        raise ValueError('viewport mode/schema')
    samples = observation['observations']
    if len(samples) != 4:
        raise ValueError('four viewport samples required')
    first_failure = None
    for item, (stage, width) in zip(samples, [('initial', 200), ('first resize', 400), ('second resize', 600), ('reset', 200)]):
        if (set(item) != {'stage', 'width', 'viewport', 'reference', 'actual', 'repeated'}
            or item['stage'] != stage or item['width'] != width or item['viewport'] != width
            or not all(finite(item[k]) for k in ['reference', 'actual', 'repeated'])
            or abs(item['reference'] - width / 2) > .01 or item['actual'] < 0
            or item['repeated'] < 0 or abs(item['actual'] - item['repeated']) > .01):
            raise ValueError('viewport sample calibration')
        if first_failure is None and abs(item['actual'] - width / 2) > 1:
            first_failure = item
    if first_failure is None or float(match[2]) != first_failure['width'] / 2 or float(match[3]) != first_failure['actual']:
        raise ValueError('viewport first target assertion join')
    return {'classification': 'CALIBRATED_VIEWPORT_TARGET_MISMATCH', 'observations': observation}


def attr_failure(name, message):
    if name.endswith('URL taint rejection'):
        match = re.fullmatch(r'assert_equals: animated tainted URL rejected expected "none" but got (.+)', message)
        if not match:
            raise ValueError('URL control/calibration failure')
        return {'classification': 'INITIAL_URL_TAINT_TARGET_OBSERVATION', 'observed_serialization': match[1],
                'security_claim': False}
    match = re.fullmatch(r'assert_approx_equals: initial computed (start value|end value|midpoint) expected (' + NUMBER + r') \+/- (?:0\.000001|1e-6) but got (' + NUMBER + ')', message)
    if not match:
        raise ValueError('attr admission/ordinary control/sample calibration failure')
    oracle = read('ATTR-ORACLES.json')[name]
    expected = {'start value': oracle['start'], 'end value': oracle['end'], 'midpoint': (oracle['start'] + oracle['end']) / 2}[match[1]]
    actual = float(match[3])
    if (float(match[2]) != expected or not finite(actual) or abs(actual - expected) <= .000001
        or (oracle['property'] == 'opacity' and not 0 <= actual <= 1)):
        raise ValueError('attr expected/range/assertion mismatch')
    return {'classification': 'KNOWN_INCORRECT_ORACLE_EXPLORATORY' if name == EXPLORATORY else 'CALIBRATED_INITIAL_ATTR_TARGET_MISMATCH',
            'stage': match[1], 'observed': actual, 'expected_by_fixture': expected,
            'later_assertions': 'NOT_REACHED', 'normative_oracle_established': name != EXPLORATORY}


def classify(rows):
    roster = read('ROSTER.json')['expected_subtests']
    expected = {(test, name) for test, names in roster.items() for name in names}
    old_tests = set(read('OLD-ROSTER.json')['expected_subtests'])
    old_rows = [row for row in rows if row.get('test') in old_tests]
    inherited = old.classify(old_rows)
    errors, calibration_errors, results = [], list(inherited['errors']), list(inherited['cases'])
    observed_viewport = read('VIEWPORT-OBSERVATIONS.json')
    for row in old_rows:
        if row['test'] in old.VIEWPORT and row['status'] == 'FAIL' and row.get('message') not in observed_viewport[row['test']]:
            calibration_errors.append('unrecognized original viewport failure: ' + row['test'])
    seen = set()
    for row in rows:
        identity = (row.get('test'), row.get('subtest'))
        if identity not in expected or identity in seen:
            errors.append('unknown/duplicate identity: ' + repr(identity))
            continue
        seen.add(identity)
        wanted = 'FAIL' if identity[0] in old.VIEWPORT else 'PASS'
        if row.get('status') not in ('PASS', 'FAIL') or row.get('expected', row.get('status')) != wanted or row.get('known_intermittent') not in (None, []):
            errors.append('status/metadata schema: ' + repr(identity))
        if identity[0] in old_tests:
            continue
        test, name = identity
        item = {'test': test, 'subtest': name, 'status': row.get('status'), 'message': row.get('message')}
        try:
            status = row.get('status')
            if status not in ('PASS', 'FAIL') or row.get('expected', status) != 'PASS' or row.get('known_intermittent') not in (None, []):
                raise ValueError('new case status/metadata')
            if status == 'PASS':
                item['classification'] = 'KNOWN_INCORRECT_ORACLE_EXPLORATORY' if name == EXPLORATORY else 'PASS'
            else:
                handler = {DURATION: duration_failure, VIEWPORT: viewport_failure, ATTR: attr_failure}[test]
                item.update(handler(name, row.get('message', '')))
                if item.get('is_independent_control') or name.endswith(': literal keyframe control'):
                    calibration_errors.append(name + ': independent control failed')
        except (ValueError, TypeError, KeyError) as failure:
            item['classification'] = 'INCONCLUSIVE_CALIBRATION_OR_SCHEMA_FAILURE'
            calibration_errors.append(name + ': ' + str(failure))
        results.append(item)
    if seen != expected or len(rows) != 52:
        errors.append('incomplete exact52 roster')
    duration_controls = [item for item in results if item['test'] == DURATION and not item['subtest'].endswith(', reuse after change')]
    duration_controls_pass = len(duration_controls) == 4 and all(item['status'] == 'PASS' for item in duration_controls)
    if not duration_controls_pass:
        for item in results:
            if item['classification'] == 'CALIBRATED_DURATION_TARGET_MISMATCH':
                item['classification'] = 'INCONCLUSIVE_DURATION_CONTROL_FAILURE'
    prior = {(r['test'], r['subtest']): r for r in read('PRIOR-ROWS.json')}
    changes = []
    for row in old_rows:
        original = prior.get((row['test'], row['subtest']))
        if original and any(original.get(k) != row.get(k) for k in ['status', 'message']):
            changes.append({'test': row['test'], 'subtest': row['subtest'], 'before': original, 'after': row})
    return {'status': 'FOLLOWUP_DIAGNOSTIC_CLASSIFIED' if not errors else 'FOLLOWUP_DIAGNOSTIC_INCONCLUSIVE',
            'counts': {s: sum(r.get('status') == s for r in rows) for s in ['PASS', 'FAIL']},
            'cases': results, 'errors': errors, 'calibration_errors': calibration_errors,
            'all_calibrations_pass': not calibration_errors, 'prior20_changes_observed': changes,
            'duration_controls_pass': duration_controls_pass, 'replay_controls_pass': inherited['replay_controls_pass'],
            'preset_failure_count': None, 'comparison_success': False, 'native_acceptance': False,
            'exploratory_case': EXPLORATORY, 'scope': 'initialization and scheduling observations only'}
