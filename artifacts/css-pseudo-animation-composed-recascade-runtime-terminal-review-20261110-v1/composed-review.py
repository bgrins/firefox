import json
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent;LAB=HERE.parent/'css-pseudo-animation-composed-recascade-runtime-20261110-v1'
def strict(s):
 def pairs(xs):
  d={}
  for k,v in xs:assert k not in d;d[k]=v
  return d
 return json.loads(s,object_pairs_hook=pairs)
inventory=strict((LAB/'COMPOSED-ASSERTIONS.json').read_text());expected=[dict(a,task=t['name']) for t in inventory['tasks'] for a in t['assertions']];tasks=[t['name'] for t in inventory['tasks']]
assert len(expected)==122 and len(tasks)==5
begun=active=ended=False;scope=None;entered=[];left=[];rows=[];harness=None
for line in (LAB/'candidate1/composed-raw.jsonl').read_text().splitlines():
 r=strict(line);a=r['action'];assert a!='crash' and not(a=='log' and r.get('level') in ['ERROR','CRITICAL'])
 if a=='suite_start':assert not begun;begun=True
 elif a=='test_start':assert begun and not active and not ended;active=True
 elif a=='log' and r.get('message','').startswith('add_task | '):
  m=r['message'];assert active
  if m.startswith('add_task | Entering '):assert scope is None;scope=m.removeprefix('add_task | Entering ');entered.append(scope)
  else:assert m=='add_task | Leaving '+scope;left.append(scope);scope=None
 elif a=='test_status':
  assert active and len(rows)<122;v=expected[len(rows)];assert scope==v['task'] and r.get('subtest') is None and r.get('expected','PASS')=='PASS' and not r.get('known_intermittent')
  if v['classification']=='probe':assert r['status']=='FAIL' and r['message'].startswith(v['name']+' - ')
  else:assert r['status']=='PASS' and r['message']==v['name']
  rows.append(r)
 elif a=='test_end':assert active and scope is None;active=False;harness=r
 elif a=='suite_end':assert begun and not active and not ended;ended=True
 elif a=='process_exit':assert r['exitcode']==0
assert ended and len(rows)==122 and entered==left==tasks and harness['status']=='FAIL' and harness['message']=='Finished in 29ms'
probes=[r['message'] for r,e in zip(rows,expected) if e['classification']=='probe']
assert probes==['Probe: Non-sampling animation does not select animation origin - got "50px", expected null','Probe: Transition remains the highest sampled effect - got null, expected "50px"','Probe: Before no-fill animation does not demote transition below important author - got "30px", expected "50px"']
print(json.dumps({'status':'PASS','observed_assertions':len(rows),'task_lifecycles':tasks,'classifications':dict(Counter(e['classification'] for e in expected)),'hard_assertions_passed':119,'probe_failures':probes,'setup_all_pass':True,'normal_aggregate':'FAIL Finished in 29ms','all_assertions_passed':False,'normative_bug_or_native_fix_claim':False},indent=2))
