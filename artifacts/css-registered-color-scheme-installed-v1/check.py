import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('saved_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
old = ROOT / 'artifacts/css-animation-taint-registered-ordering-installed-v1/run.py'
before = {v.name: ast.dump(v) for v in ast.parse(old.read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
after = {v.name: ast.dump(v) for v in ast.parse((HERE / 'run.py').read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
assert before.keys() == after.keys()
for name in before.keys() - {'validate', 'main'}:
    assert before[name] == after[name], name
assert (HERE / 'run.py').read_text().split('def main():', 1)[1] == old.read_text().split('def main():', 1)[1].replace("prefix='css-registered-ordering-'", "prefix='css-color-scheme-observation-'").replace("'animation_taint_policy_verdict': None", "'color_scheme_dependency_policy_verdict': None")
modes = ['union-plain', 'union-unused-attr', 'color-first-unused-attr', 'ident-unused-attr', 'literal']
records = [{'mode': mode, 'syntax': '<custom-ident>' if mode == 'ident-unused-attr' else '<color> | <custom-ident>' if mode == 'color-first-unused-attr' else '<custom-ident> | <color>', 'registeredInitial': 'normal', 'snapshots': [{'expected': v, 'firstScheme': v, 'custom': v} for v in ['light', 'dark']]} for mode in modes]
tests = [{'name': 'Selected identifier color-scheme dependency: ' + mode, 'status': 0, 'message': None} for mode in modes]
program = """const fs=require('fs'),vm=require('vm');const x=JSON.parse(fs.readFileSync(0,'utf8'));let cb;
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{colorSchemeDependencyObservations:x.records},navigator:{userAgent:'Firefox/158.0'},location:{search:'?run=test&nonce=secret'},URLSearchParams,add_completion_callback:f=>cb=f,fetch:async(url,o)=>{process.stdout.write(o.body);return {ok:true}}});
cb(x.tests,x.harness).catch(e=>{process.stderr.write(String(e));process.exitCode=1});"""
def bridge(values, outcomes=tests, harness=None):
    return json.loads(subprocess.run(['node', '-e', program, str(HERE / 'report.js')], input=json.dumps({'records': values, 'tests': outcomes, 'harness': harness or {'status': 0, 'message': None}}), text=True, capture_output=True, check=True).stdout)
payload = bridge(records)
runner.validate(payload, 'test', 'firefox')
assert all(check['passed'] for row in payload['report']['observations'] for check in row['referenceChecks'])
assert all(row['activeExpectation']['matches'] for row in payload['report']['observations'])
wrong = copy.deepcopy(records)
wrong[1]['snapshots'] = [{'expected': v, 'firstScheme': 'normal', 'custom': 'normal'} for v in ['light', 'dark']]
failures = copy.deepcopy(tests);failures[1].update(status=1, message='ordinary assertion failure')
observed = bridge(wrong, failures);runner.validate(observed,'test','firefox')
assert observed['report']['status'] == 'complete' and not observed['report']['observations'][1]['activeExpectation']['matches']
assert observed['report']['observations'][1]['wpt'] == failures[1]
partial = bridge(records[:-1], tests[:-1], {'status':2,'message':'timed out'})
runner.validate(partial,'test','firefox');assert partial['report']['status'] == 'incomplete'
assert partial['report']['harness'] == {'status':2,'message':'timed out'}
bad_calibration = copy.deepcopy(records);bad_calibration[0]['registeredInitial']='one two'
calibration = bridge(bad_calibration);runner.validate(calibration,'test','firefox');assert not calibration['report']['observations'][0]['referenceChecks'][0]['passed']
chrome=copy.deepcopy(payload);chrome['report']['userAgent']='HeadlessChrome/156.0.8078.80';runner.validate(chrome,'test','chrome')
mutations=[
 lambda p:p.update(run_id='foreign'),
 lambda p:p['report'].update(schema='foreign'),
 lambda p:p['report'].update(policyVerdict='PASS'),
 lambda p:p['report'].update(status='incomplete'),
 lambda p:p['report']['observations'].pop(),
 lambda p:p['report']['observations'][0].update(mode='unknown'),
 lambda p:p['report']['observations'][0]['record'].update(syntax='*'),
 lambda p:p['report']['observations'][0]['record']['snapshots'][0].update(expected='dark'),
 lambda p:p['report']['observations'][0]['record']['snapshots'][0].update(firstScheme=1),
 lambda p:p['report']['observations'][0]['record']['snapshots'].pop(),
 lambda p:p['report']['observations'][0]['referenceChecks'][0].update(passed='true'),
 lambda p:p['report']['observations'][0]['activeExpectation'].update(matches='true'),
 lambda p:p['report']['observations'][0]['wpt'].update(name='unknown'),
]
for mutate in mutations:
    value=copy.deepcopy(payload);mutate(value)
    try:runner.validate(value,'test','firefox')
    except (AssertionError,TypeError,KeyError):pass
    else:raise AssertionError('Invalid schema admitted')
policy=json.loads((HERE/'POLICY.json').read_text());assert policy['execution_enabled'] is False
runner.authenticate(policy,'firefox',application=False)
with tempfile.TemporaryDirectory(prefix='color-scheme-schema-') as temp:
    receiver=runner.Receiver(policy,'firefox',Path(temp));receiver.origin='http://127.0.0.1:12345'
    body=copy.deepcopy(payload);body['run_id']=receiver.run_id
    receiver.receive('/report/'+receiver.nonce,receiver.origin,json.dumps(body).encode())
    for path,origin in [('/report/'+receiver.nonce,receiver.origin),('/report/foreign',receiver.origin),('/report/'+receiver.nonce,'http://foreign')]:
        try:receiver.receive(path,origin,json.dumps(body).encode())
        except AssertionError:pass
        else:raise AssertionError('Duplicate or foreign report admitted')
assert not Path(temp).exists()
print(json.dumps({'schema_and_bridge_positive_cases':5,'schema_negatives':len(mutations),'transport_negatives':3,'unchanged_lifecycle':True,'browser_executed':False,'live_application_read':False,'scratch_removed':True}))
