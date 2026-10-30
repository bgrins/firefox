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
old = ROOT / 'artifacts/css-animation-taint-registered-defaulting-installed-v1/run.py'
before = {v.name: ast.dump(v) for v in ast.parse(old.read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
after = {v.name: ast.dump(v) for v in ast.parse((HERE / 'run.py').read_text()).body if isinstance(v, (ast.FunctionDef, ast.ClassDef))}
for name in ['authenticate', 'census', 'firefox_relaunch_group', 'cleanup_owned', 'Receiver', 'digest', 'save']:
    assert before[name] == after[name], name
modes = ['flush0-equal0-opacity0', 'flush0-equal0-opacity1', 'flush0-equal1-opacity0', 'flush0-equal1-opacity1', 'flush1-equal0-opacity0', 'flush1-equal0-opacity1', 'flush1-equal1-opacity0', 'flush1-equal1-opacity1', 'literal']
records = {}
for mode in modes:
    registered = True
    records[mode] = {'mode': mode,
        'registration': {'name': '--v', 'syntax': '<custom-ident>', 'inherits': False, 'initialValue': 'horizontal-tb', 'returnedSuccessfully': True} if registered else None,
        'calibration': {'initial': 'horizontal-tb' if registered else 'vertical-lr', 'multiIdent': 'horizontal-tb'},
        'before': {'variable': 'vertical-rl' if 'equal1' in mode else 'vertical-lr', 'sink': 'vertical-rl'} if mode.startswith('flush1') or mode == 'literal' else None,
        'phases': [{'label': label, 'readings': ['vertical-rl' if mode != 'literal' else 'vertical-lr'] * 4,
            'variable': 'vertical-rl', 'opacity': '1' if mode.endswith('opacity1') or mode == 'literal' else '0.25', 'cssDuration': '2s', 'currentTime': 750, 'playState': 'paused',
            'duration': 2000, 'progress': .375, 'sameAnimation': True, 'sameEffect': True}
            for label in ['initial', 'ordinary-mutation']]}
tests = [{'name': 'Registered keyframe ordering observation: ' + mode, 'status': 0 if mode == 'literal' else 1, 'message': None if mode == 'literal' else 'ordinary tentative failure'} for mode in modes]
program = """const fs=require('fs'),vm=require('vm');const x=JSON.parse(fs.readFileSync(0,'utf8'));let cb;
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{registeredOrderingObservations:x.records},navigator:{userAgent:'Firefox/158.0'},location:{search:'?run=test&nonce=secret'},URLSearchParams,add_completion_callback:f=>cb=f,fetch:async(url,o)=>{process.stdout.write(o.body);return {ok:true}}});
cb(x.tests,{status:0,message:null}).catch(e=>{process.stderr.write(String(e));process.exitCode=1});"""
def bridge(values):
    return json.loads(subprocess.run(['node', '-e', program, str(HERE / 'report.js')], input=json.dumps({'records': values, 'tests': tests}), text=True, capture_output=True, check=True).stdout)
payload = bridge(records)
runner.validate(payload, 'test', 'firefox')
assert all(check['passed'] for row in payload['report']['observations'] for check in row['referenceChecks'])
assert [row['activeExpectation']['matches'] for row in payload['report']['observations']] == [False] * 8 + [True]
assert [row['wpt']['status'] for row in payload['report']['observations']] == [1] * 8 + [0]
for value in ['horizontal-tb', 'vertical-rl', 'vertical-lr']:
    variant = copy.deepcopy(records)
    for mode in modes[:-1]:
        for phase in variant[mode]['phases']:
            phase['readings'] = [value] * 4
    report = bridge(variant); runner.validate(report, 'test', 'firefox')
    assert all(c['passed'] for row in report['report']['observations'] for c in row['referenceChecks'])
for mode, key, value in [(modes[0], 'variable', 'horizontal-tb'), ('literal', 'readings', ['horizontal-tb'] * 4), (modes[0], 'opacity', '1')]:
    variant = copy.deepcopy(records); variant[mode]['phases'][0][key] = value
    report = bridge(variant);runner.validate(report, 'test', 'firefox')
    assert not all(c['passed'] for row in report['report']['observations'] for c in row['referenceChecks'])
fixture = ROOT / 'artifacts/css-animation-taint-registered-ordering-probe-v1/tests/css/css-variables/animation-taint-registered-ordering.tentative.html'
functions = 'function configuration(mode) {' + fixture.read_text().split('function configuration(mode) {', 1)[1].split('\nfor (const mode', 1)[0]
assert functions in (HERE / 'report.js').read_text()
chrome = copy.deepcopy(payload); chrome['report']['userAgent'] = 'HeadlessChrome/156.0.8078.80';runner.validate(chrome, 'test', 'chrome')
partial_records = copy.deepcopy(records);partial_records[modes[0]] = {'mode': modes[0], 'registration': None, 'calibration': None, 'before': None, 'phases': []}
partial = bridge(partial_records);runner.validate(partial, 'test', 'firefox');assert partial['report']['status'] == 'incomplete'
absent_records = copy.deepcopy(records);del absent_records[modes[0]];runner.validate(bridge(absent_records), 'test', 'firefox')
nonfinite = copy.deepcopy(payload);nonfinite['report']['observations'][0]['record']['phases'][0]['currentTime'] = {'nonfinite': 'NaN'};runner.validate(nonfinite, 'test', 'firefox')
mutations = [
 lambda p:p.update(run_id='foreign'),
 lambda p:p['report'].update(schema='foreign'),
 lambda p:p['report'].update(policyVerdict='PASS'),
 lambda p:p['report'].update(status='incomplete'),
 lambda p:p['report']['observations'].pop(),
 lambda p:p['report']['observations'][0].update(mode='typed'),
 lambda p:p['report']['observations'][0]['record']['phases'].pop(),
 lambda p:p['report']['observations'][0]['record']['phases'][0]['readings'].pop(),
 lambda p:p['report']['observations'][0]['record']['phases'][0].update(label='other'),
 lambda p:p['report']['observations'][0]['referenceChecks'][0].update(passed='true'),
 lambda p:p['report']['observations'][0]['activeExpectation'].update(matches='true'),
 lambda p:p['report']['observations'][1]['record']['registration'].update(syntax='<length>'),
 lambda p:p['report']['observations'][0]['wpt'].update(name='unknown'),
]
for mutate in mutations:
    value=copy.deepcopy(payload);mutate(value)
    try:runner.validate(value,'test','firefox')
    except (AssertionError,TypeError,KeyError):pass
    else:raise AssertionError('Invalid schema admitted')
policy=json.loads((HERE/'POLICY.json').read_text());assert policy['execution_enabled'] is False
if policy['fixture_manifest'] is not None:
    runner.authenticate(policy,'firefox',application=False)
with tempfile.TemporaryDirectory(prefix='registered-taint-schema-') as temp:
    receiver=runner.Receiver(policy,'firefox',Path(temp));receiver.origin='http://127.0.0.1:12345'
    body=copy.deepcopy(payload);body['run_id']=receiver.run_id
    receiver.receive('/report/'+receiver.nonce,receiver.origin,json.dumps(body).encode())
    for path,origin in [('/report/'+receiver.nonce,receiver.origin),('/report/foreign',receiver.origin),('/report/'+receiver.nonce,'http://foreign')]:
        try:receiver.receive(path,origin,json.dumps(body).encode())
        except AssertionError:pass
        else:raise AssertionError('Duplicate or foreign report admitted')
assert not Path(temp).exists()
print(json.dumps({'schema_and_bridge_positive_cases':5,'schema_negatives':len(mutations),'transport_negatives':3,'unchanged_lifecycle_functions':True,'browser_executed':False,'live_application_read':False,'scratch_removed':True}))
