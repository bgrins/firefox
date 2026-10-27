import json
import math
import re

NAMES = [f'{unit}: {history} independent iframe history'
         for unit in ('vw','vh') for history in ('visible-resize','hidden-only','hidden-resize')]
NAMES += [f'px: {history} independent iframe history' for history in ('hidden-only','hidden-resize')]
FIELDS = {'unit','history','initialSize','warmed','fallbackSize','fallbackValue','preResizeSize',
          'first','repeat','hostSize','postQuerySize','postQueryValue','revealSize','revealValue','resetSize','resetValue'}

def strict_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result

def reject_constant(value):
    raise ValueError('nonfinite JSON constant')

def finite(value):
    try:
        return type(value) in (int,float) and math.isfinite(value)
    except OverflowError:
        return False

def classify(rows, names, need):
    need(names == NAMES and len(rows) == 8 and [r['subtest'] for r in rows] == NAMES, 'eight ordered unique identities')
    failures = []
    for row in rows:
        need(row['status'] in ('PASS','FAIL'), 'completed outcome')
        if row['status'] == 'PASS':
            continue
        unit, rest = row['subtest'].split(': ',1)
        history = rest.removesuffix(' independent iframe history')
        need(unit in ('vw','vh') and history in ('hidden-only','hidden-resize'), 'control failure')
        message = row.get('message')
        need(isinstance(message,str) and len(message.encode('utf-8')) <= 16384, 'bounded failure message')
        match = re.fullmatch(r'assert_equals: current viewport hypothesis; snapshot=(\{.*\}) expected (-?\d+(?:\.\d+)?) but got (-?\d+(?:\.\d+)?)', message)
        need(match is not None, 'only final hypothesis assertion admitted')
        try:
            snapshot = json.loads(match[1], object_pairs_hook=strict_object, parse_constant=reject_constant)
        except (ValueError,TypeError,RecursionError):
            need(False, 'invalid snapshot JSON')
        need(type(snapshot) is dict and set(snapshot) == FIELDS and snapshot['unit'] == unit
             and snapshot['history'] == history, 'snapshot identity/fields')
        for key in ('initialSize','fallbackSize','preResizeSize','hostSize','postQuerySize','revealSize','resetSize'):
            values = snapshot[key]
            need(type(values) is list and len(values) == (2 if key in ('preResizeSize','hostSize') else 4)
                 and all(finite(v) and 0 <= v for v in values), 'finite bounded dimensions')
        for key in ('warmed','fallbackValue','first','repeat','postQueryValue','revealValue','resetValue'):
            need(finite(snapshot[key]), 'finite snapshot value')
        size = [240,120] if history == 'hidden-only' else [460,260]
        axis = 0 if unit == 'vw' else 1
        expected = size[axis] / 10
        stale = [24,12][axis]
        fallback = [30,15][axis]
        observed_expected, observed_first = float(match[2]),float(match[3])
        need(finite(observed_expected) and finite(observed_first) and observed_expected == expected
             and observed_first == snapshot['first'] and observed_first != expected
             and observed_first in (stale,fallback), 'declared first outcome')
        need(snapshot['initialSize'] == snapshot['resetSize'] == [240,120,240,120]
             and snapshot['preResizeSize'] == [240,120] and snapshot['hostSize'] == size
             and snapshot['fallbackSize'] == [300,150,300,150] and snapshot['revealSize'] == size+size
             and snapshot['warmed'] == snapshot['resetValue'] == stale
             and snapshot['fallbackValue'] == fallback and snapshot['revealValue'] == expected, 'snapshot calibration agreement')
        failures.append({'subtest':row['subtest'],'expected_hypothesis':expected,'first':observed_first,
                         'classification':'fallback-compatible' if observed_first == fallback else 'stale-compatible',
                         'snapshot':snapshot,'message':message})
    return {'calibrated':8,'counts':{s:sum(r['status']==s for r in rows) for s in ('PASS','FAIL')},
            'first_read_mismatches':failures,'rows':rows,'native_flush_branch_observed':False,
            'later_snapshot_fields_are_observations':True,'passing_rows_do_not_export_snapshots':True,
            'historical_four_case_normative_verdict':'INCONCLUSIVE',
            'normative_assessment':'Separate pending root assessment; no verdict selected by measurement', 'accepted_bug':False}
