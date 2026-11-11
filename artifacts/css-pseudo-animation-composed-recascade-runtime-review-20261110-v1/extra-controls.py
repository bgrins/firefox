import copy,importlib.util,itertools,json,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'css-pseudo-animation-composed-recascade-runtime-20261110-v1'
spec=importlib.util.spec_from_file_location('review_parser',SOURCE/'composed-analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
inv=json.loads((SOURCE/'COMPOSED-ASSERTIONS.json').read_text());plan=json.loads((SOURCE/'RUN-PLAN.json').read_text());test=plan['composed_test']
base=[{'action':'suite_start'},{'action':'test_start','test':test}]
for task in inv['tasks']:
 base.append({'action':'log','level':'INFO','test':test,'message':'add_task | Entering '+task['name']})
 base += [{'action':'test_status','test':test,'status':'PASS','message':a['name']} for a in task['assertions']]
 base.append({'action':'log','level':'INFO','test':test,'message':'add_task | Leaving '+task['name']})
base += [{'action':'test_end','test':test,'status':'PASS','message':'Finished in 1ms'},{'action':'suite_end'}]
probes=[i for i,r in enumerate(base) if r.get('message','').startswith('Probe: ')]
nonprobe=next(i for i,r in enumerate(base) if r['action']=='test_status')
accepted=[];rejected=[]
with tempfile.TemporaryDirectory(prefix='composed-independent-controls-') as tmp:
 path=Path(tmp)/'raw.jsonl'
 def parse(rows,code):
  path.write_text(''.join(json.dumps(r)+'\n' for r in rows));return m.parse(path,code)
 def reject(name,rows,code):
  try:v=parse(rows,code)
  except (AssertionError,KeyError,TypeError,ValueError):rejected.append(name);return
  assert not v['investigation_valid'],name
  rejected.append(name)
 for mask in range(8):
  rows=copy.deepcopy(base)
  for j,i in enumerate(probes):
   if mask & (1<<j):rows[i].update(status='FAIL',expected='PASS',message=rows[i]['message']+' - observed X, proposed Y')
  if mask:rows[-2]['status']='FAIL'
  v=parse(rows,int(bool(mask)));assert v['investigation_valid'] and v['nonprobe_assertions_passed']==119 and len(v['probe_failures'])==mask.bit_count() and v['all_assertions_passed']==(mask==0) and v['native_fix_acceptance'] is False
  accepted.append(mask)
 fail=copy.deepcopy(base);fail[probes[2]].update(status='FAIL',message=fail[probes[2]]['message']+' - observed X, proposed Y');fail[-2]['status']='FAIL'
 changes=[
 ('nonprobe-todo-pass',lambda r:r[nonprobe].update(expected='FAIL')),
 ('passing-probe-todo',lambda r:r[probes[0]].update(expected='FAIL')),
 ('passing-probe-intermittent',lambda r:r[probes[0]].update(known_intermittent=['PASS'])),
 ('fail-probe-label-spoof',lambda r:r[probes[2]].update(message=r[probes[2]]['message'].split(' - ')[0]+' extra')),
 ('task-exit-before-assertions',lambda r:r.insert(3,{'action':'log','test':test,'level':'INFO','message':'add_task | Leaving '+inv['tasks'][0]['name']})),
 ('extra-test-end',lambda r:r.insert(-1,copy.deepcopy(r[-2]))),
 ('extra-suite-end',lambda r:r.append({'action':'suite_end'})),
 ('extra-assertion-after-suite',lambda r:r.append(copy.deepcopy(r[nonprobe]))),
 ('boolean-process-exit',lambda r:r.insert(-2,{'action':'process_exit','exitcode':False})),
 ('missing-process-exit-code',lambda r:r.insert(-2,{'action':'process_exit'})),
 ('lsan',lambda r:r.insert(-2,{'action':'lsan_leak'})),
 ('valgrind',lambda r:r.insert(-2,{'action':'valgrind_error'})),
 ('probe-timeout-masquerading-aggregate',lambda r:r[-2].update(status='TIMEOUT')),
 ('non-normal-aggregate-extra-text',lambda r:r[-2].update(message='Finished in 1ms; cleanup failed')),
 ]
 for name,mutate in changes:
  rows=copy.deepcopy(fail);mutate(rows);reject(name,rows,1)
 reject('negative-command-signal',fail,-9)
 reject('float-command-code',fail,1.0)
 path.write_text(''.join(json.dumps(r)+'\n' for r in fail)+'{"action":')
 try:m.parse(path,1)
 except (AssertionError,KeyError,ValueError,TypeError):rejected.append('truncated-final-json')
 else:raise AssertionError('truncation accepted')
print(json.dumps({'status':'PASS','accepted_probe_subsets':accepted,'additional_rejected_controls':rejected,'scratch_removed':not Path(tmp).exists()},indent=2))
