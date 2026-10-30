import copy
import json
from pathlib import Path

import run
import launch
import calibration

policy = json.loads((run.HERE / 'POLICY.json').read_text())
run.authenticate(policy)
assert policy['execution_enabled'] is False
for name in ['run.py', 'launch.py', 'assess.py', 'records.py', 'calibration.py']:
    compile((run.HERE / name).read_text(), name, 'exec')
inputs=json.loads((run.ROOT/'artifacts/css-contextual-duration-finite-depth-probe-v1/INPUTS.json').read_text())
assert policy['resources']==inputs['resources'] and policy['manifest']==inputs['manifest']
assert {policy['page']:policy['expected_names']}==inputs['source_roster']['tests']
assert list(policy['record_kinds'])==inputs['transport']['expected_files']
for name in ['launch.py','records.py','import_check.py']:
    assert (run.HERE/name).read_bytes()==(run.ROOT/'artifacts/css-chrome-same-element-runner-v1'/name).read_bytes()
a = run.load('synthetic_chrome_assess', run.HERE / 'assess.py')
events = [{'action': 'suite_start', 'run_info': {'product': 'chrome', 'browser_version': policy['version']}},
          {'action': 'test_start', 'test': policy['page']},
          *[{'action': 'test_status', 'test': policy['page'], 'subtest': name, 'status': 'PASS'} for name in policy['expected_names']],
          {'action': 'test_end', 'test': policy['page'], 'status': 'OK'}, {'action': 'suite_end'}]
for count in range(5):
    failed=copy.deepcopy(events)
    for i in range(count):failed[2+i].update(status='FAIL',expected='PASS')
    got=a.assess(failed,policy,1 if count else 0)
    assert got['complete'] and got['failures']==count and got['all_callbacks_pass']==(count==0)
negatives=[]
for index,key,value in [(0,'run_info',{'product':'firefox','browser_version':policy['version']}),
 (0,'run_info',{'product':'chrome','browser_version':'wrong'}),(2,'subtest','other'),(2,'test','wrong'),
 (2,'status','TIMEOUT'),(2,'expected','FAIL'),(2,'known_intermittent',['FAIL']),(6,'status','ERROR')]:
    bad=copy.deepcopy(events);bad[index][key]=value;negatives.append(bad)
negatives.extend([events[:-1],events+[events[2]],events[:2]+[events[3],events[4],events[5],events[6],events[2],events[7]],
 events+[{'action':'crash'}],events+[{'action':'log','level':'ERROR','message':'bad'}]])
for bad in negatives:assert not a.assess(bad,policy,0)['complete']
assert not a.assess(events,policy,1)['complete']
assert not a.assess(failed,policy,0)['complete']
assert launch.filter_args(['--enable-features=X','--enable-blink-features=Y','--enable-unsafe-extension-debugging','--ignore-certificate-errors','--headless=new'])==['--headless=new']
for depth in (1,2,4,8):
    original=run.ROOT/f'artifacts/css-contextual-duration-finite-depth-original-runtime-1/progress-records/depth-{depth}.json'
    observations=json.loads(original.read_text())['observations']
    calibration.require_original_calibration(observations)
    for where,field,value in [('initial','rootFont',99),('literalInitial','rootFont',99),('beforeMembership','opacity',0.25),('afterMembership','leafDuration',77)]:
        bad=copy.deepcopy(observations);bad['literal'][where][field]=value
        try:calibration.require_original_calibration(bad)
        except AssertionError:pass
        else:raise AssertionError('Invalid calibration accepted')
    bad=copy.deepcopy(observations);bad['literal']['membership'][0]['effect']=False
    try:calibration.require_original_calibration(bad)
    except AssertionError:pass
    else:raise AssertionError('Changed literal identity accepted')
print(json.dumps({'stream_positives':5,'stream_negatives':len(negatives)+2,'saved_calibration_positives':4,'calibration_negatives':20,'unchanged_executor_and_collector':True,'fixture_unchanged':True,'browser_executed':False}))
