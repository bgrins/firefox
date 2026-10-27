import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
namespace = {'__name__': 'scroll_client_validator_test'}
exec(compile((HERE / 'validate.py').read_text(), 'validate.py', 'exec'), namespace)
validate = namespace['validate']
expected_style = namespace['expected_style']
rows = []
for axis in ['x', 'y']:
    for base in [16, 16777200]:
        for extra in [0, 17]:
            row = {'key': f'{axis}-{base}-{extra}', 'axis': axis, 'base': base, 'extra': extra}
            for phase in namespace['PHASES']:
                padding = 0 if phase == 'reset' else extra
                content = [base, 16] if axis == 'x' else [16, base]
                expected = [base + padding, 16] if axis == 'x' else [16, base + padding]
                rect = [40, 40, *expected]
                row[phase] = {'scrollSize': expected[:], 'clientSize': expected[:], 'clientOrigin': [0, 0],
                    'rect': rect, 'rects': [rect[:]], 'hostRect': [40, 40, 100, 100],
                    'style': expected_style(*content, 0, 0, 'absolute',
                        ('paddingRight' if axis == 'x' else 'paddingBottom', padding)),
                    'hostStyle': expected_style(100, 100, 40, 40, 'fixed'),
                    'parentMatches': True, 'empty': True, 'scrollPosition': [0, 0], 'viewport': [800, 600]}
            rows.append(row)
payload = {'compatMode': 'CSS1Compat', 'rows': rows}
summary = validate(payload)
assert summary['calibrated'] == summary['repeat_stable'] == summary['restored_stable'] == 8
assert summary['phase_calibrated'] == 32 and summary['first_scroll_matches'] == summary['first_client_matches'] == 8
old = copy.deepcopy(payload)
for row in old['rows']:
    if row['base'] == 16777200 and row['extra'] == 17:
        for phase in ['first', 'repeat', 'restored']:
            row[phase]['scrollSize'][int(row['axis'] == 'y')] += 1
            row[phase]['clientSize'][int(row['axis'] == 'y')] += 1
prediction = validate(old)
assert prediction['calibrated'] == 8 and prediction['first_scroll_matches'] == 6 and prediction['first_client_matches'] == 6
bad_geometry = copy.deepcopy(old)
bad_geometry['rows'][3]['first']['rect'][2] += 1
invalid = validate(bad_geometry)['rows'][3]['phases']['first']
assert not invalid['calibrated'] and invalid['scroll_matches'] is invalid['client_matches'] is None
bad_parent = copy.deepcopy(payload)
bad_parent['rows'][0]['first']['parentMatches'] = False
assert not validate(bad_parent)['rows'][0]['phases']['first']['calibrated']
bad_reset = copy.deepcopy(payload)
bad_reset['rows'][1]['reset']['style']['paddingRight'] = 17
assert not validate(bad_reset)['rows'][1]['phases']['reset']['calibrated']
for label, mutation in [('roster', lambda p: p['rows'].pop()),
                        ('duplicate', lambda p: p['rows'].__setitem__(1, copy.deepcopy(p['rows'][0]))),
                        ('noninteger', lambda p: p['rows'][0]['first']['scrollSize'].__setitem__(0, True))]:
    malformed = copy.deepcopy(payload)
    mutation(malformed)
    try:
        validate(malformed)
    except AssertionError:
        pass
    else:
        raise AssertionError(label)
script = (HERE / 'probe.html').read_text().split('<script>')[1].split('</script>')[0]
with (HERE / 'syntax.log').open('w') as log:
    result = subprocess.run(['node', '--check'], input=script, text=True, stdout=log, stderr=subprocess.STDOUT)
assert result.returncode == 0
receipt = {'html_script_sha256': hashlib.sha256(script.encode()).hexdigest(), 'node_syntax_exit': 0,
           'synthetic_exact_rows': 8, 'synthetic_exact_phases': 32,
           'synthetic_old_scroll_first_matches': 6, 'synthetic_old_client_first_matches': 6,
           'calibration_failure_masks_observer_verdicts': True,
           'rejected_bad_roster_duplicate_and_boolean_metric': True,
           'browser_execution': False, 'native_build_or_mutation': False}
(HERE / 'CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
(HERE / 'PREDICTED-OLD-SUMMARY.json').write_text(json.dumps(prediction, indent=2) + '\n')
consolidated = copy.deepcopy(old)
for row, exact in zip(consolidated['rows'], payload['rows']):
    for phase in namespace['PHASES']:
        row[phase]['scrollSize'] = exact[phase]['scrollSize'][:]
consolidated_prediction = validate(consolidated)
assert consolidated_prediction['first_scroll_matches'] == 8 and consolidated_prediction['first_client_matches'] == 6
(HERE / 'PREDICTED-OFFSET-SCROLL-FIX-SUMMARY.json').write_text(json.dumps(consolidated_prediction, indent=2) + '\n')
print(json.dumps(receipt))
