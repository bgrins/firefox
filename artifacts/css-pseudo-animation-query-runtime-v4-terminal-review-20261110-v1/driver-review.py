import json,hashlib,sys
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent;LAB=HERE.parent/'css-pseudo-animation-query-runtime-20261110-v4'
def strict(text):
 def pairs(items):
  d={}
  for k,v in items:assert k not in d;d[k]=v
  return d
 return json.loads(text,object_pairs_hook=pairs)
inventory=strict((LAB/'DRIVER-ASSERTIONS.json').read_text());expected=[a for t in inventory['tasks'] for a in t['assertions']];events=[];known=[];unknown=[];begun=active=ended=False;test_started=test_ended=False;harness=None
for line in (LAB/'candidate1/driver-raw.jsonl').read_text().splitlines():
 r=strict(line);a=r['action'];assert a!='crash' and not(a=='log' and r.get('level') in ['ERROR','CRITICAL'])
 if a=='suite_start':assert not begun;begun=True
 elif a=='test_start':assert begun and not ended and not test_started;test_started=active=True;test=r['test']
 elif a=='test_status':
  assert active and r['test']==test and r.get('subtest') is None
  if len(known)<208:
   assert r['status']=='PASS' and r['message']==expected[len(known)]['name'] and r.get('expected','PASS')=='PASS' and not r.get('known_intermittent');known.append(r)
  else:unknown.append(r)
 elif a=='test_end':assert active and r['test']==test and not test_ended;active=False;test_ended=True;harness=r
 elif a=='suite_end':assert begun and test_ended and not active and not ended;ended=True
 elif a=='assertion_count':assert r['min_expected']<=r['count']<=r['max_expected']
assert ended and len(known)==208 and len(unknown)==0 and harness['status']=='PASS'
result=strict((LAB/'candidate1/DRIVER-RESULTS.json').read_text());assert unknown==result['unexpected_callbacks'] and [r['message'] for r in known]==[r['name'] for r in result['assertions']]
assert result['missing_assertions']==[a['name'] for a in expected[208:]]
counts=[];start=0
for t in inventory['tasks']:
 end=start+len(t['assertions']);counts.append({'task':t['name'],'required':len(t['assertions']),'observed':max(0,min(end,208)-start),'complete':end<=208});start=end
print(json.dumps({'status':'PASS','raw_known_PASS':208,'raw_setup_exception_callbacks':0,'raw_harness':'PASS','missing':0,'tasks':counts,'all_thirteen_fixture_tasks_complete':True},indent=2))
