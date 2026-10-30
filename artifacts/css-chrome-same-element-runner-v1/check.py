import copy
import json
from pathlib import Path
import shutil
import tempfile

import run
import launch

policy = json.loads((run.HERE / 'POLICY.json').read_text())
run.authenticate(policy)
assert policy['execution_enabled'] is False
for name in ['run.py', 'launch.py', 'assess.py', 'records.py']:
    compile((run.HERE / name).read_text(), name, 'exec')
a = run.load('synthetic_chrome_assess', run.HERE / 'assess.py')
events = [{'action': 'suite_start', 'run_info': {'product': 'chrome', 'browser_version': policy['version']}},
          {'action': 'test_start', 'test': policy['page']},
          *[{'action': 'test_status', 'test': policy['page'], 'subtest': name, 'status': 'PASS'} for name in policy['expected_names']],
          {'action': 'test_end', 'test': policy['page'], 'status': 'OK'}, {'action': 'suite_end'}]
assert a.assess(events, policy, 0)['complete']
failed = copy.deepcopy(events); failed[2].update(status='FAIL', expected='PASS')
assert a.assess(failed, policy, 1)['complete'] and not a.assess(failed, policy, 1)['all_callbacks_pass']
failed[3].update(status='FAIL', expected='PASS')
assert a.assess(failed, policy, 1)['complete']
negatives = []
for index, key, value in [(0,'run_info',{'product':'firefox','browser_version':policy['version']}),
 (0,'run_info',{'product':'chrome','browser_version':'wrong'}),(2,'subtest','other'),(2,'test','wrong'),
 (2,'status','TIMEOUT'),(2,'expected','FAIL'),(2,'known_intermittent',['FAIL']),(4,'status','ERROR')]:
    bad=copy.deepcopy(events);bad[index][key]=value;negatives.append(bad)
negatives.extend([events[:-1],events+[events[2]],events[:2]+[events[3],events[4],events[2],events[5]],
 events+[{'action':'crash'}],events+[{'action':'log','level':'ERROR','message':'bad'}]])
for bad in negatives:
    assert not a.assess(bad,policy,0)['complete']
assert not a.assess(events,policy,1)['complete']
assert not a.assess(failed,policy,0)['complete']
assert launch.filter_args(['--enable-features=X','--enable-blink-features=Y','--enable-unsafe-extension-debugging','--ignore-certificate-errors','--headless=new']) == ['--headless=new']
try:
    launch.filter_args(['--no-sandbox'])
except AssertionError:
    pass
else:
    raise AssertionError('sandbox disabling accepted')
print(json.dumps({'stream_positives':3,'stream_negatives':len(negatives)+2,'filter_positive':1,'sandbox_negative':1}))
