import hashlib,json
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
LAB=HERE.parent/'css-pseudo-animation-transient-recascade-runtime-20261110-v4'
def strict(text):
 def pairs(items):
  d={}
  for k,v in items:assert k not in d;d[k]=v
  return d
 return json.loads(text,object_pairs_hook=pairs)
reports=[]
for prefix,inventory_name,result_name,count,tasks in [('driver','DRIVER-ASSERTIONS.json','DRIVER-RESULTS.json',208,13),('recascade','RECASCADE-ASSERTIONS.json','RECASCADE-RESULTS.json',100,6)]:
 inventory=strict((LAB/inventory_name).read_text());expected=[a for t in inventory['tasks'] for a in t['assertions']]
 assert len(expected)==count and len(inventory['tasks'])==tasks and len(set(x['name'] for x in expected))==count
 rows=[];begun=active=ended=False;test_started=test_ended=False;harness=None
 for line in (LAB/'candidate1'/(prefix+'-raw.jsonl')).read_text().splitlines():
  r=strict(line);a=r['action'];assert a!='crash' and not(a=='log' and r.get('level') in ['ERROR','CRITICAL'])
  if a=='suite_start':assert not begun;begun=True
  elif a=='test_start':assert begun and not ended and not test_started;test_started=active=True;test=r['test']
  elif a=='test_status':
   assert active and r['test']==test and r.get('subtest') is None and len(rows)<count
   assert r['status']=='PASS' and r['message']==expected[len(rows)]['name'] and r.get('expected','PASS')=='PASS' and not r.get('known_intermittent');rows.append(r)
  elif a=='test_end':assert active and r['test']==test and not test_ended;active=False;test_ended=True;harness=r
  elif a=='suite_end':assert begun and test_ended and not active and not ended;ended=True
  elif a=='assertion_count':assert r['min_expected']<=r['count']<=r['max_expected']
 assert ended and len(rows)==count and harness['status']=='PASS'
 saved=strict((LAB/'candidate1'/result_name).read_text())
 assert saved['gate_passed'] and not any(saved[n] for n in ['unexpected_callbacks','missing_assertions','failed_assertions','integrity_errors'])
 assert saved['exact_assertion_order'] and len(saved['tasks'])==tasks and len(saved['assertions'])==count
 for r,v in zip(rows,saved['assertions'],strict=True):assert r['message']==v['name']==v['message'] and v['passed'] and v['status']=='PASS'
 for t,v in zip(inventory['tasks'],saved['tasks'],strict=True):assert t['name']==v['task'] and v['setup_gates_passed'] and v['all_assertions_passed'] and not v['failed_or_missing_setup']
 reports.append({'fixture':prefix,'assertions':count,'tasks':tasks,'statuses':dict(Counter(r['status'] for r in rows)),'classification_counts':dict(Counter(r['classification'] for r in expected)),'harness':'PASS','all_setup_gates_passed':True,'exact_order_and_messages':True,'no_extra_missing_crash_or_error':True})
print(json.dumps({'status':'PASS','fixtures':reports,'total_assertions':308,'total_tasks':19},indent=2))
