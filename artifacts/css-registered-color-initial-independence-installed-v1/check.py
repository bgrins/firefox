import ast
import copy
import difflib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('saved_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
old = ROOT / 'artifacts/css-registered-color-scheme-installed-v1/run.py'
source = (HERE / 'run.py').read_text()
before = {v.name: ast.dump(v) for v in ast.parse(old.read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
module = ast.parse(source)
after = {v.name: ast.dump(v) for v in module.body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
assert before.keys() == after.keys()
for name in before.keys() - {'validate', 'main'}:
    assert before[name] == after[name], name
assert ''.join(difflib.unified_diff(old.read_text().splitlines(True), source.splitlines(True), fromfile=str(old.relative_to(ROOT)), tofile=str((HERE / 'run.py').relative_to(ROOT)))) == (HERE / 'RUN-DELTA.patch').read_text()
main = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
fields = {'observation_complete', 'all_callbacks_pass', 'harness_ok', 'active_controls_pass', 'reference_checks_pass'}
assigns = [n for n in main.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in fields for t in n.targets)]
assert len(assigns) == len(fields)
result = next(n for n in ast.walk(main) if isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == 'suite_pass' for k in n.keys))
suite = next(v for k, v in zip(result.keys, result.values) if isinstance(k, ast.Constant) and k.value == 'suite_pass')

def aggregates(report):
    context = {'receiver': SimpleNamespace(report=report)}
    exec(compile(ast.Module(body=assigns, type_ignores=[]), 'saved aggregates', 'exec'), context)
    context['suite_pass'] = eval(compile(ast.Expression(body=suite), 'saved suite verdict', 'eval'), context)
    return context

modes = ['red', 'CanvasText', 'light-dark(red, blue)']
records = [{'initialValue': mode, 'syntaxSupported': True, 'controlInitial': 'rgb(255, 0, 0)', 'literalRed': 'rgb(255, 0, 0)', 'accepted': mode == 'red', 'exception': None if mode == 'red' else {'name': 'SyntaxError', 'message': 'synthetic independence rejection'}} for mode in modes]
tests = [{'name': 'Registered color initial independence: ' + mode, 'status': 0, 'message': None} for mode in modes]
program = """const fs=require('fs'),vm=require('vm');const x=JSON.parse(fs.readFileSync(0,'utf8'));let cb;
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{registrationObservations:x.records},navigator:{userAgent:'Firefox/158.0'},location:{search:'?run=test&nonce=secret'},URLSearchParams,add_completion_callback:f=>cb=f,fetch:async(url,o)=>{if(url!='/report/secret')throw Error('nonce');process.stdout.write(o.body);return {ok:true}}});
cb(x.tests,x.harness).catch(e=>{process.stderr.write(String(e));process.exitCode=1});"""

def bridge(values, outcomes=tests, harness=None):
    return json.loads(subprocess.run(['node', '-e', program, str(HERE / 'report.js')], input=json.dumps({'records': values, 'tests': outcomes, 'harness': harness or {'status': 0, 'message': None}}), text=True, capture_output=True, check=True).stdout)

payload = bridge(records)
runner.validate(payload, 'test', 'firefox')
assert aggregates(payload['report'])['suite_pass']
accepted = copy.deepcopy(records)
for r in accepted:
    r.update(accepted=True, exception=None)
failures = copy.deepcopy(tests)
for t in failures[1:]:
    t.update(status=1, message='Contextual initial unexpectedly accepted')
observed = bridge(accepted, failures)
runner.validate(observed, 'test', 'firefox')
assert observed['report']['status'] == 'complete' and not aggregates(observed['report'])['suite_pass']
assert [r['activeExpectation']['matches'] for r in observed['report']['observations']] == [True, False, False]
assert observed['report']['observations'][1]['wpt'] == failures[1]
wrong_exception = copy.deepcopy(records)
wrong_exception[1]['exception']['name'] = 'InvalidModificationError'
wrong = bridge(wrong_exception, failures)
runner.validate(wrong, 'test', 'firefox')
assert not wrong['report']['observations'][1]['activeExpectation']['matches']
partial = bridge(records[:1], failures)
runner.validate(partial, 'test', 'firefox')
assert partial['report']['status'] == 'incomplete' and partial['report']['observations'][1]['record'] is None
assert not aggregates(partial['report'])['suite_pass']
timeout = bridge(records, tests, {'status': 2, 'message': 'timeout'})
runner.validate(timeout, 'test', 'firefox')
assert aggregates(timeout['report'])['all_callbacks_pass'] and not aggregates(timeout['report'])['suite_pass']
bad_calibration = copy.deepcopy(records)
bad_calibration[0]['controlInitial'] = 'green'
calibration = bridge(bad_calibration)
runner.validate(calibration, 'test', 'firefox')
assert not aggregates(calibration['report'])['reference_checks_pass']
assert not aggregates(None)['suite_pass']
chrome = copy.deepcopy(payload)
chrome['report']['userAgent'] = 'HeadlessChrome/156.0.8078.80'
runner.validate(chrome, 'test', 'chrome')
mutations = [
    lambda p: p.update(run_id='foreign'),
    lambda p: p['report'].update(schema='foreign'),
    lambda p: p['report'].update(policyVerdict='PASS'),
    lambda p: p['report'].update(status='incomplete'),
    lambda p: p['report'].update(userAgent='Firefox/1.0'),
    lambda p: p['report']['observations'].pop(),
    lambda p: p['report']['observations'][0].update(mode='unknown'),
    lambda p: p['report']['observations'][0]['record'].update(initialValue='foreign'),
    lambda p: p['report']['observations'][0]['record'].update(accepted='true'),
    lambda p: p['report']['observations'][0]['record'].update(exception={'name': 'Error', 'message': 'unexpected'}),
    lambda p: p['report']['observations'][1]['record']['exception'].update(message=1),
    lambda p: p['report']['observations'][0]['referenceChecks'][0].update(passed=False),
    lambda p: p['report']['observations'][0]['referenceChecks'][0].update(name='foreign'),
    lambda p: p['report']['observations'][0]['activeExpectation'].update(matches=False),
    lambda p: p['report']['observations'][0]['activeExpectation'].update(matches=1),
    lambda p: p['report']['observations'][0]['wpt'].update(name='unknown'),
]
for mutate in mutations:
    bad = copy.deepcopy(payload)
    mutate(bad)
    try:
        runner.validate(bad, 'test', 'firefox')
    except (AssertionError, TypeError, KeyError):
        pass
    else:
        raise AssertionError('Invalid report admitted')
policy = json.loads((HERE / 'POLICY.json').read_text())
assert policy['execution_enabled'] is False
runner.authenticate(policy, 'firefox', application=False)
with tempfile.TemporaryDirectory(prefix='initial-registration-schema-') as temp:
    receiver = runner.Receiver(policy, 'firefox', Path(temp))
    receiver.origin = 'http://127.0.0.1:12345'
    body = copy.deepcopy(payload)
    body['run_id'] = receiver.run_id
    receiver.receive('/report/' + receiver.nonce, receiver.origin, json.dumps(body).encode())
    for path, origin in [('/report/' + receiver.nonce, receiver.origin), ('/report/foreign', receiver.origin), ('/report/' + receiver.nonce, 'http://foreign')]:
        try:
            receiver.receive(path, origin, json.dumps(body).encode())
        except AssertionError:
            pass
        else:
            raise AssertionError('Duplicate or foreign report admitted')
assert not Path(temp).exists()
print(json.dumps({'bridge_positive_cases': 7, 'schema_negatives': len(mutations), 'transport_negatives': 3, 'saved_result_aggregate_expressions_checked': True, 'unchanged_lifecycle_functions': True, 'browser_executed': False, 'live_application_read': False, 'scratch_removed': True}))
