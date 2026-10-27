import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ATTR = '/css/css-animations/keyframe-attribute-dependency.html'
TREE = '/css/css-values/ordinary-tree-counting-cancel.html'
REPLAY = '/css/css-animations/cancelled-contextual-effect-replay.html'
VIEWPORT = {'/css/css-animations/responsive/fill-forwards-viewport-units.html',
            '/web-animations/responsive/fill-forwards-viewport-units.html'}
NUMBER = r'-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate observation key')
        result[key] = value
    return result


def finite_opacity(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def attr_failure(name, message):
    if name.endswith('initial keyframe resolution'):
        match = re.fullmatch(r'assert_equals: initial owning-element attribute value expected 0\.25 but got (' + NUMBER + ')', message)
        if match and finite_opacity(float(match[1])) and float(match[1]) != 0.25:
            return {'classification': 'INITIAL_ATTRIBUTE_RESOLUTION_MISMATCH', 'observed': float(match[1])}
        raise ValueError('initial syntax/provider calibration failure')
    prefixes = {'initial calibration': ('initial', 0.25, 'INITIAL_ATTRIBUTE_RESOLUTION_MISMATCH'),
                'explicit recascade calibration': ('forced', 0.75, 'FORCED_RECASCADE_CALIBRATION_FAILURE'),
                'first read after attribute mutation': ('first', 0.75, 'CALIBRATED_ATTRIBUTE_MUTATION_MISMATCH'),
                'first read after reset': ('reset', 0.25, 'CALIBRATED_ATTRIBUTE_RESET_MISMATCH')}
    for prefix, (field, expected, classification) in prefixes.items():
        match = re.fullmatch(r'assert_equals: ' + re.escape(prefix) + r': (\{.*\}) expected (' + NUMBER + ') but got (' + NUMBER + ')', message)
        if not match:
            continue
        observation = json.loads(match[1], object_pairs_hook=unique_object)
        if set(observation) != {'initial', 'first', 'reset', 'forced'} or not all(map(finite_opacity, observation.values())):
            raise ValueError('invalid observation schema')
        if float(match[2]) != expected or float(match[3]) != observation[field] or observation[field] == expected:
            raise ValueError('assertion/observation mismatch')
        if field != 'initial' and observation['initial'] != 0.25:
            raise ValueError('initial calibration missing')
        if field in ('first', 'reset') and observation['forced'] != 0.75:
            raise ValueError('forced recascade calibration missing')
        if field == 'reset' and observation['first'] != 0.75:
            raise ValueError('preceding first mutation assertion did not pass')
        return {'classification': classification, 'observations': observation}
    raise ValueError('unrecognized attribute failure')


def replay_failure(name, message):
    identity = re.fullmatch(r'Cancelled contextual effect: (width|transform), reuse after change', name)
    match = re.fullmatch(r'assert_equals: first sample after replay: (\{.*\}) expected 40 but got (' + NUMBER + ')', message)
    if not identity or not match:
        raise ValueError('replay initial/playback/control calibration failure')
    observation = json.loads(match[1], object_pairs_hook=unique_object)
    if set(observation) != {'property', 'mode', 'observed'}:
        raise ValueError('replay observation schema')
    value = observation['observed']
    if (observation['property'] != identity[1] or observation['mode'] != 'reuse after change'
        or type(value) not in (int, float) or not math.isfinite(value)
        or value != float(match[2]) or value == 40):
        raise ValueError('replay assertion/observation mismatch')
    return {'classification': 'CALIBRATED_INACTIVE_REPLAY_MISMATCH', 'observations': observation}


def classify(rows):
    roster = json.loads((HERE / 'OLD-ROSTER.json').read_text())['expected_subtests']
    expected = {(test, name) for test, names in roster.items() for name in names}
    errors, results, seen = [], [], set()
    for row in rows:
        identity = (row.get('test'), row.get('subtest'))
        if identity not in expected or identity in seen:
            errors.append('unknown/duplicate identity: ' + repr(identity))
            continue
        seen.add(identity)
        test, name = identity
        status = row.get('status')
        effective_expected = row.get('expected', status)
        wanted = 'FAIL' if test in VIEWPORT else 'PASS'
        item = {'test': test, 'subtest': name, 'status': status, 'effective_expected': effective_expected}
        try:
            if status not in ('PASS', 'FAIL') or effective_expected != wanted or row.get('known_intermittent') not in (None, []):
                raise ValueError('status/metadata schema')
            if test in VIEWPORT:
                item['classification'] = 'EXISTING_VIEWPORT_EXPECTATION_OBSERVED'
                item['message'] = row.get('message')
            elif status == 'PASS':
                item['classification'] = 'PASS'
            elif test == REPLAY:
                item.update(replay_failure(name, row.get('message', '')))
            elif test == ATTR and ': typed attr ' in name:
                item.update(attr_failure(name, row.get('message', '')))
                if item['classification'] == 'FORCED_RECASCADE_CALIBRATION_FAILURE':
                    errors.append(name + ': forced recascade failed; scheduling attribution inconclusive')
            else:
                raise ValueError('mandatory independent control failed')
        except (ValueError, TypeError) as error:
            item['classification'] = 'REJECTED_CALIBRATION_OR_SCHEMA'
            errors.append(name + ': ' + str(error))
        results.append(item)
    if seen != expected or len(rows) != 20:
        errors.append('incomplete exact20 roster')
    controls = [r for r in results if r['test'] == REPLAY and not r['subtest'].endswith(', reuse after change')]
    replay_controls_pass = len(controls) == 4 and all(r['classification'] == 'PASS' for r in controls)
    if not replay_controls_pass:
        for item in results:
            if item['classification'] == 'CALIBRATED_INACTIVE_REPLAY_MISMATCH':
                item['classification'] = 'INCONCLUSIVE_REPLAY_CONTROL_FAILURE'
    return {'status': 'DEPENDENCY_DIAGNOSTIC_CLASSIFIED' if not errors else 'DEPENDENCY_DIAGNOSTIC_REJECTED',
            'counts': {status: sum(r.get('status') == status for r in rows) for status in ('PASS', 'FAIL')},
            'cases': results, 'errors': errors, 'replay_controls_pass': replay_controls_pass,
            'preset_failure_count': None, 'new_bug_accepted': False}
