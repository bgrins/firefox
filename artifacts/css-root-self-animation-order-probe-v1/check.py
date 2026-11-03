import copy
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('order_assess', HERE / 'assess.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = json.loads((HERE / 'CASES.json').read_text())
embedded = (HERE / 'probe.js').read_text().split('const cases = ', 1)[1].split(';', 1)[0]
assert json.loads(embedded) == cases
assert len(cases) == len({tuple(case.items()) for case in cases}) == 34
report = {'schema': 'root-self-animation-order-v1', 'userAgent': 'synthetic', 'cases': [], 'errors': [], 'cleanup': True}
for case in cases:
    initial = {'fontSize': 16, 'lineHeight': None, 'rem': 16, 'rlh': 19.2}
    configured = {'fontSize': 23, 'lineHeight': 37, 'rem': 23, 'rlh': 37}
    expected = 2 * initial[case['unit']] if case['target'] == 'root-font' else (
        2 * (23 if case['unit'] == 'rem' else initial['rlh']) if case['target'] == 'root-line'
        else 2 * (23 if case['unit'] == 'rem' else 37))
    controls = {'initialMetrics': True, 'configuredRoot': True, 'configuredMetricProxies': True}
    disturbance = None
    if case['history'] == 'em-cancel':
        disturbance = {'kind': 'em-cancel', 'value': 32, 'expected': 32}
        controls['emCalibration'] = True
    elif case['history'] == 'comparator-reset':
        disturbance = {'kind': 'comparator-reset', 'property': 'lineHeight' if case['target'] == 'root-line' else 'fontSize', 'value': expected, 'expected': expected}
        controls['ordinaryComparator'] = True
    before = None
    if case['barrier'] == 'root-read':
        before = {'fontSize': 23, 'lineHeight': 37}
        controls['restoredRootRead'] = True
    controls['pausedMidpoint'] = True
    report['cases'].append(dict(case, error=None, initial=initial, configured=configured, controls=controls,
                               normativeExpected=expected, disturbance=disturbance, preconditionRead=before,
                               samples=[{'timing': timing, 'raw': str(expected) + 'px', 'value': expected} for timing in ('first', 'settled')],
                               animation={'currentTime': 500, 'playState': 'paused', 'progress': 0.5,
                                          'targetIsRoot': case['target'] in ('root-font', 'root-line', 'root-pseudo-font'),
                                          'pseudoElement': '::before' if case['target'] == 'root-pseudo-font' else None},
                               postStateAfterBothSamples=configured))
passed = module.assess(report)
assert passed['controls_valid'] and all(row['normative_match'] for row in passed['rows'])
ordered = copy.deepcopy(report)
for case in ordered['cases']:
    if case['unit'] == 'rem' and case['history'] == 'em-cancel' and case['barrier'] == 'none':
        for sample in case['samples']:
            sample.update(raw='64px', value=64)
observed = module.assess(ordered)
assert observed['controls_valid'] and any(not row['equal'] for row in observed['ordering_comparisons'])
root_defect = copy.deepcopy(report)
for case in root_defect['cases']:
    if case['target'] == 'root-font':
        for sample in case['samples']:
            sample.update(raw='46px', value=46)
observed = module.assess(root_defect)
assert observed['controls_valid'] and any(not row['normative_match'] for row in observed['rows'])
uncalibrated = copy.deepcopy(report)
case = next(row for row in uncalibrated['cases'] if row['barrier'] == 'root-read')
case['preconditionRead']['fontSize'] = 32
case['controls']['restoredRootRead'] = False
observed = module.assess(uncalibrated)
assert not observed['controls_valid'] and len(observed['rows']) == 68
first_only = copy.deepcopy(report)
first_only['cases'][0]['samples'][0].update(raw='128px', value=128)
observed = module.assess(first_only)
assert not observed['rows'][0]['normative_match'] and observed['rows'][1]['normative_match']

mutations = [
    lambda r: r['cases'].pop(),
    lambda r: r['cases'].append(copy.deepcopy(r['cases'][0])),
    lambda r: r['cases'][0].update(target='unknown'),
    lambda r: r['cases'][0]['samples'].pop(),
    lambda r: r['cases'][0]['samples'][0].update(timing='settled'),
    lambda r: r['cases'][0]['samples'][0].update(value=-1),
    lambda r: r['cases'][0]['samples'][0].update(raw='unexpected'),
    lambda r: r['cases'][0].update(normativeExpected=999),
    lambda r: r['cases'][0]['controls'].update(configuredRoot=False),
    lambda r: r['cases'][0]['animation'].update(targetIsRoot=False),
    lambda r: r.update(cleanup=False),
    lambda r: r['errors'].append({'message': 'setup error'}),
]
for change in mutations:
    bad = copy.deepcopy(report)
    change(bad)
    try:
        module.assess(bad)
    except (AssertionError, ValueError, TypeError, KeyError):
        continue
    raise AssertionError('Malformed diagnostic accepted')
syntax = subprocess.run(['node', '--check', str(HERE / 'probe.js')], capture_output=True, text=True)
assert syntax.returncode == 0, syntax.stderr
print(json.dumps({'cases': 34, 'samples': 68, 'synthetic_paths': 5, 'rejecting_controls': len(mutations),
                  'javascript_syntax': True, 'case_roster_matches': True, 'browser_execution': False}))
