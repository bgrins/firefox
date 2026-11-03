import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('saved_review', HERE/'review.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
binding = m.read(HERE/'BINDINGS.json')
assert binding['execution_enabled'] is False
assert all(binding[x] is None for x in ('candidate','audit','audit_report'))
for path, digest in m.read(HERE/'REFERENCES.json').items():
    assert m.sha(m.ROOT/path) == digest
m.authenticated(binding['owner'])
launch=m.read(m.ROOT/binding['launch']['path'])
assert m.sha(m.ROOT/binding['launch']['path'])==binding['launch']['sha256']
assert launch['owner_manifest_sha256']==binding['owner']['manifest_sha256']
assert launch['pgid']==9316
checks = m.load('existing_checks',m.ROOT/binding['checks'])
snapshot = m.read(m.ROOT/binding['original_snapshot'])
base = {}
rosters = {}
for lane in ('reparse','fallback','controls'):
    suite = m.authenticated(binding['suites'][lane])
    runtime = m.authenticated(binding[lane+'_original'])
    rosters[lane] = m.read(suite/'ROSTER.json')
    base[lane] = m.original(runtime,m.read(suite/'INPUTS.json'),rosters[lane],snapshot,checks)
assert sum(len(r) for r in base.values()) == 85
assert sum(v['status']=='PASS' for r in base.values() for v in r.values()) == 67
assert sum(v['status']=='FAIL' for r in base.values() for v in r.values()) == 12
changed = copy.deepcopy(base['reparse'])
for row in changed.values():
    if row['status']=='FAIL':
        row.update(status='PASS',expected='PASS',expected_field_present=False,message=None,message_field_present=False)
assert m.compare(base['reparse'],changed,True)['comparison_passed']
assert m.compare(base['fallback'],base['fallback'])['comparison_passed']
assert m.compare(base['controls'],base['controls'])['comparison_passed']
negative = 0
for field,value in [('expected','FAIL'),('known_intermittent',['PASS']),('message','unexpected payload')]:
    bad=copy.deepcopy(changed);key=next(k for k,v in base['reparse'].items() if v['status']=='FAIL');bad[key][field]=value
    assert not m.compare(base['reparse'],bad,True)['comparison_passed'];negative += 1
for sample in (binding,dict(binding,execution_enabled=True)):
    try:m.review(sample)
    except AssertionError:negative += 1
    else:raise AssertionError('pending evidence admitted')
for field,value in [('status','FAIL'),('expected','FAIL'),('expected_field_present',True),('known_intermittent',['FAIL']),('intermittent_field_present',False),('message','changed'),('message_field_present',True)]:
    bad=copy.deepcopy(base['controls']);key=next(k for k in bad if k[0]=='test_status');bad[key][field]=value
    assert not m.compare(base['controls'],bad)['comparison_passed'];negative += 1
bad=copy.deepcopy(base['controls']);key=next(k for k in bad if k[0]=='test_end');bad[key]['status']='CRASH'
assert not m.compare(base['controls'],bad)['comparison_passed'];negative += 1
bad=copy.deepcopy(base['fallback']);key=next(k for k,v in bad.items() if v['status']=='FAIL');bad[key]['message']='different failure'
assert not m.compare(base['fallback'],bad)['comparison_passed'];negative += 1
assert not m.compare(base['reparse'],base['reparse'],True)['comparison_passed'];negative += 1
bad=copy.deepcopy(base['reparse']);key=next(k for k,v in bad.items() if v['status']=='FAIL');bad[key]['message']='registration failed'
try:m.compare(bad,changed,True)
except AssertionError:negative += 1
else:raise AssertionError('setup failure admitted')
runtime=m.ROOT/binding['controls_original']['directory'];raw=m.events(runtime/'raw.jsonl');roster=rosters['controls']
cases=[[e for e in raw if e.get('action')!='suite_end'],raw+[next(e for e in raw if e.get('action')=='test_status')],raw+[{'action':'crash'}]]
wrong=copy.deepcopy(raw);next(e for e in wrong if e.get('action')=='test_status')['subtest']='wrong';cases.append(wrong)
wrong=copy.deepcopy(raw);next(e for e in wrong if e.get('action')=='test_end')['test']='/wrong.html';cases.append(wrong)
for rows in cases:
    try:m.signatures(rows,roster,0,checks)
    except AssertionError:negative += 1
    else:raise AssertionError('invalid stream admitted')
try:m.signatures(raw,roster,1,checks)
except AssertionError:negative += 1
else:raise AssertionError('wrong exit admitted')
print(json.dumps({'success':True,'actual_baseline_callbacks':79,'actual_baseline_endings':6,'pass':67,'fail':12,'synthetic_candidate_comparison_positives':3,'negative_controls':negative,'candidate_runtime_read':False,'browser_execution':False,'pending_guard':True}))
