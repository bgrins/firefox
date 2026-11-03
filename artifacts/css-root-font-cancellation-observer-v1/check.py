import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
for path,pin in read(HERE/'REFERENCES.json').items():
    assert sha(ROOT/path)==pin
module=load('observer',HERE/'compare.py')
b=read(HERE/'BINDINGS.json')
assert not b['execution_enabled'] and all(b[k] is None for k in ('owner_manifest','runtime_manifest','owner_terminal','owner_result','build_result','restoration'))
module.authenticate(ROOT/b['baseline']['directory'],b['baseline']['manifest_sha256'])
raw=read(ROOT/b['baseline']['path']);assert sha(ROOT/b['baseline']['path'])==b['baseline']['sha256']
module.authenticate(ROOT/raw['full22_runtime'],raw['full22_manifest_sha256'])
assessor=load('actual_signatures',ROOT/b['baseline']['directory']/'assess.py')
page='/web-animations/animation-model/keyframe-effects/root-font-cancel-child-animation.html'
events=[json.loads(line) for line in (ROOT/raw['full22_runtime']/'raw.jsonl').read_text().splitlines()]
assert [r for r in events if r.get('action')=='test_status' and r.get('test')==page]==raw['rows']
assert [r for r in events if r.get('action')=='test_end' and r.get('test')==page]==raw['endings']
baseline={'rows':[assessor.signature(r) for r in raw['rows']],'ends':[assessor.signature(r) for r in raw['endings']]}
rows,ends=copy.deepcopy((baseline['rows'],baseline['ends']))
r=module.compare_signatures(baseline,rows,ends,True)
assert r['observation_complete'] and not r['witness_closed_under_known_fix']
assert r['fail_to_pass']==0 and r['preserved_pass_signatures']==6 and len(r['remaining_failures'])==2
assert all('expected 46' in v['message'] for v in r['remaining_failures'])
fail_indices=[i for i,r in enumerate(rows) if r['status']=='FAIL']
for i in fail_indices:
    rows[i].update(status='PASS',expected='PASS',expected_field_present=False,message=None,message_field_present=False)
r=module.compare_signatures(baseline,rows,ends,True)
assert r['witness_closed_under_known_fix'] and r['fail_to_pass']==2 and r['preserved_pass_signatures']==6
partial=copy.deepcopy(rows);partial[fail_indices[0]]=copy.deepcopy(baseline['rows'][fail_indices[0]])
r=module.compare_signatures(baseline,partial,ends,True);assert r['fail_to_pass']==1 and not r['witness_closed_under_known_fix']
control=next(i for i,r in enumerate(baseline['rows']) if r['status']=='PASS')
changed=copy.deepcopy(rows);changed[control]['message']='new metadata'
r=module.compare_signatures(baseline,changed,ends,True);assert len(r['changed_prior_pass_signatures'])==1 and not r['witness_closed_under_known_fix']
changed[control].update(status='FAIL',message='control regression')
r=module.compare_signatures(baseline,changed,ends,True);assert r['remaining_failures'][0]['message']=='control regression' and not r['witness_closed_under_known_fix']
changed_end=copy.deepcopy(ends);changed_end[0]['message']='new ending metadata'
r=module.compare_signatures(baseline,rows,changed_end,True);assert not r['ending_signature_preserved'] and not r['witness_closed_under_known_fix']
for observed_rows,observed_ends in [([],[]),(rows[:2],[dict(ends[0],status='CRASH')])]:
    r=module.compare_signatures(baseline,observed_rows,observed_ends,False)
    assert not r['observation_complete'] and not r['witness_closed_under_known_fix'] and 'fail_to_pass' not in r
negatives=[]
def reject(label,fn):
    try:fn()
    except (AssertionError,KeyError,TypeError):negatives.append(label)
    else:raise AssertionError(label)
reject('disabled main',module.main)
for label,mutate in [('missing callback',lambda r,e:r.pop()),('duplicate callback',lambda r,e:r.__setitem__(0,r[1])),('unexpected identity',lambda r,e:r[0].update(subtest='unexpected')),('missing ending',lambda r,e:e.pop()),('duplicate ending',lambda r,e:e.append(copy.deepcopy(e[0]))),('noncompleted callback status',lambda r,e:r[0].update(status='TIMEOUT')),('crash called complete',lambda r,e:e[0].update(status='CRASH'))]:
    r,e=copy.deepcopy((rows,ends));mutate(r,e)
    reject(label,lambda:module.compare_signatures(baseline,r,e,True))
assert not (HERE/'RESULT.json').exists()
print(json.dumps({'saved_only':True,'actual_full22_projection_verified':True,'actual_baseline':{'PASS':6,'FAIL':2,'endings':1},'observation_cases':8,'rejecting_controls':negatives,'native_acceptance':False,'future_candidate_pending':True}))
