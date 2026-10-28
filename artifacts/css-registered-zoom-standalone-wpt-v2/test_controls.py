import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

helper, comparison = load('run'), load('compare')
experiment = helper.read(HERE / 'EXPERIMENT.json')
historical = load('history').validate(ROOT,HERE,helper)
comparison.signatures(historical['events'],experiment)
rows = [copy.deepcopy(e) for e in historical['events'] if e['action']=='test_status']
ends = [copy.deepcopy(e) for e in historical['events'] if e['action']=='test_end']
for e in rows:
    if e['test'] in experiment['zoom_tests']:
        e['status']='FAIL';e['message']='observed baseline failure'
original = {'complete':True,'execution_preserved':True,'rows':rows,'ends':ends,
            'run_info':{'browser_build_id':'original','os':'test'},'run_binding':{'revision':experiment['frozen_head']}}
candidate = copy.deepcopy(original)
candidate['run_info']['browser_build_id']='candidate'
positives=[]; negatives=[]
def passes(name, current):
    assert comparison.compare(original,current,experiment,historical)['broad_regression_gate_passed'],name
    positives.append(name)
def rejects(name, current):
    try:
        result=comparison.compare(original,current,experiment,historical)
        assert not result['broad_regression_gate_passed'],name
    except (ValueError,KeyError):pass
    negatives.append(name)
passes('unchanged broad with all zoom70 failing is allowed',candidate)
held = next(e for e in candidate['rows'] if e['test'] in experiment['held_subtests'])
c=copy.deepcopy(candidate); next(e for e in c['rows'] if e['test']==held['test'])['status']='PASS'
passes('held FAIL to PASS is an observed repair',c)
for label, mutate in [
 ('missing row',lambda c:c['rows'].pop()),
 ('duplicate row',lambda c:c['rows'].append(copy.deepcopy(c['rows'][0]))),
 ('missing completion',lambda c:c['ends'].pop()),
 ('unknown identity',lambda c:c['rows'][0].update(subtest='unknown')),
 ('unpreserved execution',lambda c:c.update(execution_preserved=False)),
 ('incomplete execution',lambda c:c.update(complete=False)),
 ('different HEAD',lambda c:c['run_binding'].update(revision='other')),
 ('different run_info',lambda c:c['run_info'].update(os='other')),
 ('held changed unresolved message',lambda c:next(e for e in c['rows'] if e['test']==held['test']).update(message='different observed value')),
 ('broad PASS to FAIL',lambda c:next(e for e in c['rows'] if e['test'] in experiment['broad_tests'] and e['status']=='PASS').update(status='FAIL')),
 ('reftest PASS to FAIL',lambda c:next(e for e in c['ends'] if e['status']=='PASS').update(status='FAIL')),
 ('held expected field drift',lambda c:next(e for e in c['rows'] if e['test']==held['test']).update(expected='FAIL')),
]:
    c=copy.deepcopy(candidate);mutate(c);rejects(label,c)
for index,e in enumerate(candidate['rows']):
    if e['test'] in experiment['held_subtests']:
        c=copy.deepcopy(candidate);c['rows'][index]['message']='changed full failure signature';rejects('held signature '+e['subtest'],c)
observed=comparison.compare(None,original,experiment,historical)
assert observed['complete'] and not observed['broad_regression_gate_passed']
result={'positive_controls':positives,'negative_controls':negatives,'historical_raw_replays':3,
        'historical_subtests':len(rows),'historical_test_completions':len(ends),'browser_executed':False}
(HERE/'CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'positive':len(positives),'negative':len(negatives),'historical_subtests':len(rows),'completions':len(ends)}))
