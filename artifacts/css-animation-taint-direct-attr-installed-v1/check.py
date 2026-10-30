import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('saved_waapi_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
old = ROOT / 'artifacts/css-animation-taint-waapi-installed-v1/run.py'
before = {v.name: ast.dump(v) for v in ast.parse(old.read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
after = {v.name: ast.dump(v) for v in ast.parse((HERE / 'run.py').read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
for name in ['authenticate', 'census', 'firefox_relaunch_group', 'cleanup_owned', 'Receiver', 'digest', 'save']:
    assert before[name] == after[name], name

def details(active=False, before=False):
    return {'sink': 'arbitrary observed value', 'variable': 'wrong but preserved',
            'timing': None if before else {'duration': 2000, 'computedDuration': 2000,
                'time': 750 if active else None, 'progress': .375 if active else None,
                'state': 'paused' if active else 'idle'}, 'effectSame': None if before else True}

samples = [{'phase': phase, 'sink': 'any observed value'} for phase in
           ['first-read', 'passive-frame-1', 'passive-frame-2', 'passive-frame-3']]
rows = [{'mode': mode, 'stage': 'complete', 'error': None, 'before': details(before=True),
         'activeSamples': copy.deepcopy(samples), 'active': details(active=True),
         'activeMembership': {'count': 1, 'sameAnimation': True, 'sameEffect': True},
         'cancelSamples': copy.deepcopy(samples), 'cancelled': details(),
         'cancelMembership': {'count': 0, 'sameAnimation': False, 'sameEffect': True},
         'referenceChecks': [{'name': 'synthetic wrong value', 'passed': False}],
         'activeExpectation': {'expectedSink': 'vertical-lr', 'kind': 'control', 'matches': False},
         'policyVerdict': None} for mode in ['tainted-attr', 'untainted-attr', 'literal-attr', 'direct-var']]
payload = {'run_id': 'test', 'report': {'schema': 'direct-attr-observation-v1',
    'status': 'complete', 'userAgent': 'Firefox/158.0', 'policyVerdict': None, 'observations': rows}}
assert runner.validate(payload, 'test', 'firefox') == payload['report']
chrome = copy.deepcopy(payload)
chrome['report']['userAgent'] = 'HeadlessChrome/156.0.8078.80'
runner.validate(chrome, 'test', 'chrome')
partial = copy.deepcopy(payload)
partial['report']['status'] = 'incomplete'
row = partial['report']['observations'][0]
row.update(stage='setup', error={'name': 'Error', 'message': 'setup failed', 'stack': ''},
           before=None, active=None, activeMembership=None, cancelled=None, cancelMembership=None,
           activeSamples=[], cancelSamples=[], activeExpectation=None)
runner.validate(partial, 'test', 'firefox')
nonfinite = copy.deepcopy(payload)
nonfinite['report']['observations'][0]['active']['timing']['time'] = {'nonfinite': 'NaN'}
runner.validate(nonfinite, 'test', 'firefox')

mutations = [
    lambda p: p.update(run_id='wrong'),
    lambda p: p['report'].update(schema='wrong'),
    lambda p: p['report'].update(policyVerdict='PASS'),
    lambda p: p['report']['observations'].pop(),
    lambda p: p['report']['observations'][0].update(mode='direct-var'),
    lambda p: p['report'].update(userAgent='Chrome/156.0.8078.80'),
    lambda p: p['report']['observations'][0]['activeSamples'].pop(),
    lambda p: p['report']['observations'][0]['activeSamples'][0].update(phase='wrong'),
    lambda p: p['report']['observations'][0].update(active=None),
    lambda p: p['report']['observations'][0]['referenceChecks'][0].update(passed='true'),
    lambda p: p['report']['observations'][0].update(policyVerdict=False),
    lambda p: p['report'].update(status='incomplete'),
    lambda p: p['report']['observations'][0]['activeExpectation'].update(matches='true'),
]
for mutate in mutations:
    value = copy.deepcopy(payload)
    mutate(value)
    try:
        runner.validate(value, 'test', 'firefox')
    except (AssertionError, TypeError, KeyError):
        pass
    else:
        raise AssertionError('invalid schema admitted')

policy = json.loads((HERE / 'POLICY.json').read_text())
assert policy['execution_enabled'] is False
with tempfile.TemporaryDirectory(prefix='css-direct-attr-schema-') as temp:
    output = Path(temp)
    receiver = runner.Receiver(policy, 'firefox', output)
    receiver.origin = 'http://127.0.0.1:12345'
    body = copy.deepcopy(payload)
    body['run_id'] = receiver.run_id
    receiver.receive('/report/' + receiver.nonce, receiver.origin, json.dumps(body).encode())
    assert json.loads((output / 'REPORT.json').read_text()) == body
    for path, origin in [('/report/' + receiver.nonce, receiver.origin),
                         ('/report/wrong', receiver.origin),
                         ('/report/' + receiver.nonce, 'http://wrong')]:
        try:
            receiver.receive(path, origin, json.dumps(body).encode())
        except AssertionError:
            pass
        else:
            raise AssertionError('duplicate or foreign report admitted')
assert not output.exists()
from types import SimpleNamespace
main = next(v for v in ast.parse((HERE / 'run.py').read_text()).body if isinstance(v, ast.FunctionDef) and v.name == 'main')
assignment = next(v for v in main.body if isinstance(v, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'active_controls_pass' for t in v.targets))
expression = compile(ast.Expression(assignment.value), '<saved active-control reporting>', 'eval')
def controls(value):
    return eval(expression, {'receiver': SimpleNamespace(report=value)})
positive = copy.deepcopy(payload['report'])
for row in positive['observations']:
    if row['mode'] in ['untainted-attr', 'literal-attr']:
        row['activeExpectation']['matches'] = True
assert controls(positive)
assert not controls(None)
for mode in ['untainted-attr', 'literal-attr']:
    value = copy.deepcopy(positive)
    next(v for v in value['observations'] if v['mode'] == mode)['activeExpectation']['matches'] = False
    assert not controls(value)
print('Separate active-control reporting accepts both controls and rejects either failed control or absent report.')
print('Four schema outcomes, thirteen malformed controls, exclusive report and three transport negatives passed; lifecycle functions unchanged; no browser.')
