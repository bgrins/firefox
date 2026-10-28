import copy
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
policy=json.loads((HERE/'POLICY.json').read_text());parser=load('assessor',HERE/'assess.py');checks=load('checks',ROOT/policy['helpers']['checks'])
binding={'path':'/synthetic/application.ini','resolved':'/synthetic/application.ini','sha256':'a'*64,'browser_build_id':'20261027000000','revision':policy['frozen_head']}
def events(fail):
    rows=[{'action':'suite_start','run_info':{'os':'mac','debug':False,**binding}}]
    for test,kind in policy['tests'].items():
        rows.append({'action':'test_start','test':test})
        if kind=='testharness':
            for name in (policy['target_subtests']|policy['held_subtests'])[test]:
                rows.append({'action':'test_status','test':test,'subtest':name,'status':'FAIL' if fail else 'PASS','expected':'PASS','message':'observed=[{"width":"20px"},{"width":"30px"}]' if fail else None})
        rows.append({'action':'test_end','test':test,'status':'OK' if kind=='testharness' else 'PASS'})
    rows.append({'action':'suite_end'});return rows
positive=[];rejected=[]
for fail in [False,True]:
    result=parser.assess(events(fail),int(fail),policy,checks,original=None,run_binding=binding)
    assert result['complete'] and result['observed_subtest_count']==775 and not result['comparison_gate_passed'];positive.append('all FAIL observations' if fail else 'all PASS observations')
base=events(True)
def reject(name,rows,code=1):
    assert not parser.assess(rows,code,policy,checks,original=None,run_binding=binding)['complete'],name
    rejected.append(name)
seen=set()
for index,row in enumerate(base):
    if row['action']=='test_status' and row['test'] not in seen:
        seen.add(row['test']);reject('missing identity in '+row['test'],base[:index]+base[index+1:])
index=next(i for i,r in enumerate(base) if r['action']=='test_status')
reject('duplicate identity',base[:index]+[base[index]]+base[index:])
reject('missing suite end',base[:-1]);reject('inconsistent exit',base,0)
for field in ['browser_build_id','revision']:
    rows=copy.deepcopy(base);rows[0]['run_info'][field]='wrong';reject('wrong '+field,rows)
for status in ['TIMEOUT','NOTRUN','ERROR']:
    rows=copy.deepcopy(base);rows[index]['status']=status;reject('noncompleted '+status,rows)
rows=copy.deepcopy(base);next(r for r in rows if r['action']=='test_status' and r['test'] in policy['held_subtests'])['message']='missing snapshots';reject('incomplete held mutation trace',rows)
rows=copy.deepcopy(base);rows.insert(-1,{'action':'crash'});reject('crash',rows)
(HERE/'CONTROLS.json').write_text(json.dumps({'positive_controls':positive,'rejected_controls':rejected,'browser_executed':False},indent=2)+'\n')
print(json.dumps({'positive':len(positive),'rejected':len(rejected),'named_assertions':775}))
