from pathlib import Path
import copy
import json
import subprocess

HERE = Path(__file__).resolve().parent
scope = {}
exec(compile((HERE / 'validate.py').read_text(), 'validate.py', 'exec'), scope)
validate = scope['validate']
html = (HERE / 'probe.html').read_text()
script = html.split('<script>')[1].split('</script>')[0]
r = subprocess.run(['node', '--check'], input=script, text=True, capture_output=True)
assert r.returncode == 0, r.stderr
rows = []
for method in ('getCTM', 'getScreenCTM'):
    for viewbox in (True, False):
        for hidden in (False, True):
            warm = [1, 0, 0, 1, *([20, 30] if method == 'getScreenCTM' else [0, 0])]
            changed = [2 if viewbox else 1, *warm[1:]]
            row = {'key': f"{method}-{'viewBox' if viewbox else 'no-viewBox'}-{'hidden' if hidden else 'visible'}",
                   'method': method, 'viewBox': viewbox, 'hidden': hidden,
                   'policy': 'hidden' if hidden else 'visible', 'bbox': [10, 20, 30, 40]}
            row.update({k: warm[:] for k in ('warm', 'twinWarm', 'restored', 'twinRestored')})
            row.update({k: changed[:] for k in ('first', 'repeat', 'twinChanged', 'afterBBox', 'afterLayout', 'revealed')})
            row.update({k: [20, 30, 100, 100] for k in ('warmHost', 'hiddenHost', 'restoredHost')})
            row.update({k: [20, 30, 200, 100] for k in ('hostChanged', 'twinHostChanged', 'forcedRect')})
            rows.append(row)
payload = {'compatMode': 'CSS1Compat', 'scroll': [0, 0], 'rows': rows}
summary = validate(payload)
assert summary['calibrated'] == summary['stable'] == summary['matched'] == 8
stale = copy.deepcopy(payload)
for row in stale['rows']:
    if row['hidden'] and row['viewBox']:
        row['first'] = row['warm'][:]
        row['repeat'] = row['warm'][:]
summary = validate(stale)
assert summary['calibrated'] == summary['stable'] == 8 and summary['mismatched'] == 2
badcal = copy.deepcopy(payload)
badcal['rows'][0]['hostChanged'][2] = 199
assert validate(badcal)['calibrated'] == 7
null = copy.deepcopy(payload)
null['rows'][0]['first'] = None
assert validate(null)['mismatched'] == 1
negatives = []
for mutate in (lambda p: p['rows'].pop(),
               lambda p: p['rows'].__setitem__(1, p['rows'][0]),
               lambda p: p['rows'][0]['first'].__setitem__(0, float('nan')),
               lambda p: p.__setitem__('compatMode', 'BackCompat'),
               lambda p: p.__setitem__('scroll', [1, 0])):
    damaged = copy.deepcopy(payload)
    mutate(damaged)
    try:
        validate(damaged)
    except (AssertionError, KeyError, TypeError):
        negatives.append(True)
    else:
        raise AssertionError('malformed payload accepted')
receipt = {'browser_executed': False, 'javascript_syntax_exit': r.returncode,
           'exact_roster_rows': 8, 'synthetic_all_correct': True,
           'synthetic_two_stale_matrices_retained': True,
           'failed_calibration_retained': True, 'null_observation_retained': True,
           'malformed_negative_checks': len(negatives)}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
