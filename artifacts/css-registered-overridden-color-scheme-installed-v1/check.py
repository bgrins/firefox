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
old = ROOT / 'artifacts/css-registered-color-initial-independence-installed-v1/run.py'
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

modes = ['color-no-loser','color-literal','color-normal-before-important','color-normal-after-important','color-normal-before-normal','color-important-before-important','length-no-loser','length-literal','length-normal-before-important']
records = []
for mode in modes:
    length = mode.startswith('length-')
    row = {'caseName': mode, 'initial': '0px' if length else 'rgb(255, 0, 0)', 'phases': []}
    for index in range(2):
        expected = ('40px' if index == 0 else '60px') if length else ('rgb(0, 0, 255)' if index == 0 else 'rgb(0, 128, 0)')
        winner = ('20px' if index == 0 else '30px') if length else ('dark' if index == 0 else 'light')
        row['phases'].append({'phase': index,'declared': expected if mode.endswith('-literal') else ('2em' if length else 'light-dark(green, blue)'),
            'property': 'font-size' if length else 'color-scheme','winner': winner,'expected':expected,'samples':[expected]*4,
            'computedWinner': winner,'reference':expected,'supportedLosingValue':True})
    records.append(row)
tests = [{'name': 'Overridden registered dependency: ' + mode, 'status': 0, 'message': None} for mode in modes]
program = """const fs=require('fs'),vm=require('vm');const x=JSON.parse(fs.readFileSync(0,'utf8'));let cb;
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{overriddenSchemeObservations:x.records},navigator:{userAgent:'Firefox/158.0'},location:{search:'?run=test&nonce=secret'},URLSearchParams,add_completion_callback:f=>cb=f,fetch:async(url,o)=>{if(url!='/report/secret')throw Error('nonce');process.stdout.write(o.body);return {ok:true}}});
cb(x.tests,x.harness).catch(e=>{process.stderr.write(String(e));process.exitCode=1});"""
def bridge(values, outcomes=tests, harness=None):
    return json.loads(subprocess.run(['node','-e',program,str(HERE/'report.js')],input=json.dumps({'records':values,'tests':outcomes,'harness':harness or {'status':0,'message':None}}),text=True,capture_output=True,check=True).stdout)
payload=bridge(records)
runner.validate(payload,'test','firefox')
assert aggregates(payload['report'])['suite_pass']
failed=copy.deepcopy(records)
failed[2]['phases'][0]['samples']=['rgb(255, 0, 0)']*4
failures=copy.deepcopy(tests);failures[2].update(status=1,message='synthetic overridden declaration failure')
observed=bridge(failed,failures);runner.validate(observed,'test','firefox')
assert observed['report']['status']=='complete' and not aggregates(observed['report'])['suite_pass']
assert aggregates(observed['report'])['reference_checks_pass'] and aggregates(observed['report'])['active_controls_pass']
assert not observed['report']['observations'][2]['activeExpectation']['matches']
wrong=copy.deepcopy(records);wrong[0]['phases'][0]['computedWinner']='light'
calibration=bridge(wrong);runner.validate(calibration,'test','firefox')
assert not aggregates(calibration['report'])['reference_checks_pass']
partial=copy.deepcopy(records);partial[2]['phases'].pop()
incomplete=bridge(partial,failures);runner.validate(incomplete,'test','firefox')
assert incomplete['report']['status']=='incomplete' and not aggregates(incomplete['report'])['suite_pass']
missing=bridge(records[:1],failures);runner.validate(missing,'test','firefox')
assert missing['report']['observations'][1]['record'] is None and not aggregates(missing['report'])['suite_pass']
timeout=bridge(records,tests,{'status':2,'message':'timeout'});runner.validate(timeout,'test','firefox')
assert aggregates(timeout['report'])['all_callbacks_pass'] and not aggregates(timeout['report'])['suite_pass']
control=copy.deepcopy(records);control[1]['phases'][0]['samples']=['red']*4
control_report=bridge(control);runner.validate(control_report,'test','firefox')
assert not aggregates(control_report['report'])['active_controls_pass']
assert not aggregates(None)['suite_pass']
chrome=copy.deepcopy(payload);chrome['report']['userAgent']='HeadlessChrome/156.0.8078.80';runner.validate(chrome,'test','chrome')
mutations=[
 lambda p:p.update(run_id='foreign'),lambda p:p['report'].update(schema='foreign'),
 lambda p:p['report'].update(policyVerdict='PASS'),lambda p:p['report'].update(status='incomplete'),
 lambda p:p['report'].update(userAgent='Firefox/1.0'),lambda p:p['report']['observations'].pop(),
 lambda p:p['report']['observations'][0].update(mode='unknown'),lambda p:p['report']['observations'][0]['record'].update(caseName='unknown'),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(phase=True),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(expected='red'),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(winner='blue'),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(supportedLosingValue=1),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(samples=[1]),
 lambda p:p['report']['observations'][0]['referenceChecks'][0].update(passed=False),
 lambda p:p['report']['observations'][0]['activeExpectation'].update(matches=1),
 lambda p:p['report']['observations'][0]['wpt'].update(name='unknown')]
for mutate in mutations:
    bad=copy.deepcopy(payload);mutate(bad)
    try:runner.validate(bad,'test','firefox')
    except (AssertionError,TypeError,KeyError):pass
    else:raise AssertionError('Invalid report admitted')
policy=json.loads((HERE/'POLICY.json').read_text());assert policy['execution_enabled'] is False
runner.authenticate(policy,'firefox',application=False)
with tempfile.TemporaryDirectory(prefix='overridden-schema-') as temp:
    receiver=runner.Receiver(policy,'firefox',Path(temp));receiver.origin='http://127.0.0.1:12345'
    body=copy.deepcopy(payload);body['run_id']=receiver.run_id
    receiver.receive('/report/'+receiver.nonce,receiver.origin,json.dumps(body).encode())
    for path,origin in [('/report/'+receiver.nonce,receiver.origin),('/report/foreign',receiver.origin),('/report/'+receiver.nonce,'http://foreign')]:
        try:receiver.receive(path,origin,json.dumps(body).encode())
        except AssertionError:pass
        else:raise AssertionError('Duplicate or foreign report admitted')
assert not Path(temp).exists()
print(json.dumps({'bridge_cases':8,'schema_negatives':len(mutations),'transport_negatives':3,'unchanged_lifecycle_functions':True,'result_aggregates_checked':True,'browser_executed':False,'live_application_read':False,'scratch_removed':True}))
