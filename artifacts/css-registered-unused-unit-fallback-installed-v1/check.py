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
old = ROOT / 'artifacts/css-registered-overridden-color-scheme-installed-v1/run.py'
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

modes = ['defined','missing','literal']
records = []
for mode in modes:
    row = {'mode': mode, 'initial': '0px', 'phases': []}
    for index in range(2):
        expected = '0px' if mode == 'missing' else ('30px' if index else '20px')
        font = ('17px' if index else '11px') if mode == 'missing' else expected
        row['phases'].append({'phase': index,'samples':[expected]*4,'font':font,
            'size':'' if mode == 'missing' else ('30px' if index else '20px'),
            'parentFont':'17px' if index else '11px','expectedCustom':expected,'expectedFont':font})
    records.append(row)
tests = [{'name': 'Registered unused unit fallback: ' + mode, 'status': 0, 'message': None} for mode in modes]
program = """const fs=require('fs'),vm=require('vm');const x=JSON.parse(fs.readFileSync(0,'utf8'));let cb;
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{unusedUnitFallbackObservations:x.records},navigator:{userAgent:'Firefox/158.0'},location:{search:'?run=test&nonce=secret'},URLSearchParams,add_completion_callback:f=>cb=f,fetch:async(url,o)=>{if(url!='/report/secret')throw Error('nonce');process.stdout.write(o.body);return {ok:true}}});
cb(x.tests,x.harness).catch(e=>{process.stderr.write(String(e));process.exitCode=1});"""
def bridge(values, outcomes=tests, harness=None):
    return json.loads(subprocess.run(['node','-e',program,str(HERE/'report.js')],input=json.dumps({'records':values,'tests':outcomes,'harness':harness or {'status':0,'message':None}}),text=True,capture_output=True,check=True).stdout)
payload=bridge(records)
runner.validate(payload,'test','firefox')
assert aggregates(payload['report'])['suite_pass']
failed=copy.deepcopy(records);failed[0]['phases'][0]['samples']=['0px']*4
failures=copy.deepcopy(tests);failures[0].update(status=1,message='synthetic unused fallback failure')
observed=bridge(failed,failures);runner.validate(observed,'test','firefox')
assert observed['report']['status']=='complete' and not aggregates(observed['report'])['suite_pass']
assert aggregates(observed['report'])['reference_checks_pass'] and aggregates(observed['report'])['active_controls_pass']
assert not observed['report']['observations'][0]['activeExpectation']['matches']
wrong=copy.deepcopy(records);wrong[0]['phases'][0]['parentFont']='12px'
calibration=bridge(wrong);runner.validate(calibration,'test','firefox')
assert not aggregates(calibration['report'])['reference_checks_pass']
partial=copy.deepcopy(records);partial[0]['phases'].pop()
incomplete=bridge(partial,failures);runner.validate(incomplete,'test','firefox')
assert incomplete['report']['status']=='incomplete' and not aggregates(incomplete['report'])['suite_pass']
missing=bridge(records[:1],failures);runner.validate(missing,'test','firefox')
assert missing['report']['observations'][1]['record'] is None and not aggregates(missing['report'])['suite_pass']
timeout=bridge(records,tests,{'status':2,'message':'timeout'});runner.validate(timeout,'test','firefox')
assert aggregates(timeout['report'])['all_callbacks_pass'] and not aggregates(timeout['report'])['suite_pass']
control=copy.deepcopy(records);control[2]['phases'][0]['font']='0px'
control_report=bridge(control);runner.validate(control_report,'test','firefox')
assert not aggregates(control_report['report'])['active_controls_pass']
assert not aggregates(None)['suite_pass']
chrome=copy.deepcopy(payload);chrome['report']['userAgent']='HeadlessChrome/156.0.8078.80';runner.validate(chrome,'test','chrome')
mutations=[
 lambda p:p.update(run_id='foreign'),lambda p:p['report'].update(schema='foreign'),
 lambda p:p['report'].update(policyVerdict='PASS'),lambda p:p['report'].update(status='incomplete'),
 lambda p:p['report'].update(userAgent='Firefox/1.0'),lambda p:p['report']['observations'].pop(),
 lambda p:p['report']['observations'][0].update(mode='unknown'),lambda p:p['report']['observations'][0]['record'].update(mode='unknown'),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(phase=True),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(expectedCustom='1em'),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(expectedFont='blue'),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(size=1),
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
with tempfile.TemporaryDirectory(prefix='unused-unit-schema-') as temp:
    receiver=runner.Receiver(policy,'firefox',Path(temp));receiver.origin='http://127.0.0.1:12345'
    body=copy.deepcopy(payload);body['run_id']=receiver.run_id
    receiver.receive('/report/'+receiver.nonce,receiver.origin,json.dumps(body).encode())
    for path,origin in [('/report/'+receiver.nonce,receiver.origin),('/report/foreign',receiver.origin),('/report/'+receiver.nonce,'http://foreign')]:
        try:receiver.receive(path,origin,json.dumps(body).encode())
        except AssertionError:pass
        else:raise AssertionError('Duplicate or foreign report admitted')
assert not Path(temp).exists()
print(json.dumps({'bridge_cases':8,'schema_negatives':len(mutations),'transport_negatives':3,'unchanged_lifecycle_functions':True,'result_aggregates_checked':True,'browser_executed':False,'live_application_read':False,'scratch_removed':True}))
