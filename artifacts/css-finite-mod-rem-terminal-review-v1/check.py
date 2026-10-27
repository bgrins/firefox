from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'artifacts/css-finite-mod-rem-runtime-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def auth(p,h):
 assert sha(p)==h
 m=read(p)
 for n,v in m.items():assert sha(p.parent/n)==v,n
 return m
m=auth(P/'FILES.json','90dce7991da1c70f56832eb68fe85002926ae08531c569ec48df2fbf1ff03791');L=lambda n:read(P/n)
a=L('INPUTS.json');base=ROOT/'artifacts/css-finite-mod-rem-browser-v2';b=read(base/'INPUTS.json')
auth(base/'DRAFT-FILES.json','a7459b6ae333ae80786bacc6caa4defe194c2abca078bca1aefb2a0f333a04ac')
assert {k for k in a if a[k]!=b[k]}=={'ready_for_execution','controller_review','preservation_review'}
assert a['ready_for_execution'] and a['actual_session'] is None and a['actual_exit'] is None
for k in ['epoch','epoch_review','controller_review','preservation_epoch','preservation_review']:
 v=a[k];auth(ROOT/v['path']/'FILES.json',v['manifest_sha256'])
for n,h in b['local_pins'].items():assert sha(P/n)==h
assert sha(P/'capture.py')==b['capture_sha256']
old=read(ROOT/a['preservation_epoch']['path']/'FINAL.json');before=L('BEFORE.json');final=L('FINAL.json');pre=L('PRE-CAPTURE.json')
assert before==read(ROOT/a['epoch']['path']/'FINAL.json')
assert final['snapshot']==old['snapshot']==before['snapshot']
assert final['installed_tests']==old['installed_tests']==before['installed_tests'] and len(final['installed_tests'])==24
assert final==L('PRE-FLIGHT.json') and len(final['snapshot']['sources'])==72
assert final['pins']==L('FINAL-PINS.json')==L('BASELINE-PINS.json')
assert len(final['pins'])==620 and len(old['pins'])==618
assert all(k in final['pins'] and final['pins'][k]==v for k,v in old['pins'].items())
assert final['pins']==read(base/'STATIC-BASELINE-PINS.json')
owned=L('OWNED-TESTS.json');assert len(owned)==1
path,info=next(iter(owned.items()));assert info['sha256']==sha(P/'fixture.html') and len(info['identity'])==2
expected=dict(final['pins']);assert expected[path] is None;expected[path]=info['sha256']
assert pre['pins']==expected and pre['snapshot']==final['snapshot'] and pre['installed_tests']==final['installed_tests']
r=L('wpt-diagnostic/RUN.json');events=[json.loads(s) for s in (P/'wpt-diagnostic/raw.json').read_text().splitlines() if s.strip()]
for action,key in [('test_status','rows'),('test_start','starts'),('test_end','ends')]:assert [e for e in events if e.get('action')==action]==r[key]
roster=L('ROSTER.json')['expected_subtests'];assert len(roster)==1
test,names=next(iter(roster.items()));assert len(names)==24
assert [(e['test'],e['subtest']) for e in r['rows']]==[(test,n) for n in names]
assert len(r['starts'])==len(r['ends'])==1 and r['starts'][0]['test']==r['ends'][0]['test']==test and r['ends'][0]['status']=='OK'
assert events.index(r['starts'][0])<events.index(r['rows'][0])<events.index(r['rows'][-1])<events.index(r['ends'][0])
assert r['complete'] and not r['infrastructure_faults'] and r['exit']==1 and r['before']==r['after']==expected
for i,e in enumerate(r['rows'][:16]):
 assert e['status']=='FAIL' and e['expected']=='PASS' and not e['known_intermittent']
 h=json.loads(re.fullmatch(r'assert_true: target: finite remainder (.+) expected true got false',e['message'])[1])
 case=L('CASES.json')[i//2];route=['literal','contextual'][i%2]
 assert all(h[k]==v for k,v in case.items()) and h['route']==route
 A,B=case['a'],case['b'];q=abs(A)//abs(B)*(1 if A*B>=0 else -1)
 oracle=A%B if case['op']=='mod' else A-q*B
 assert oracle==case['expected'] and abs(oracle)<abs(B)
 dividend=str(A) if route=='literal' else f'{A} * sign(1em - 16px)'
 assert h['expression']==f"calc(0.5 + {case['op']}({dividend}, {B}) / 8)"
 assert e['subtest']==f"{case['op']} exact finite remainder: A={A}, B={B}, {route}"
 fonts=[16] if route=='literal' else [16,32,16]
 assert h['history']==[{'font':font,'expected':.5 if route=='contextual' and font==16 else .5+oracle/8,'first':.5,'repeat':.5} for font in fonts]
 assert L('SUMMARY.json')['rows'][i]['history']==h
assert all(e['status']=='PASS' and not e.get('known_intermittent') for e in r['rows'][16:])
summary=L('SUMMARY.json');assert not summary['errors'] and summary['calibrated_mismatches']==16 and summary['counts']=={'PASS':8,'FAIL':16}
assert L('wpt-diagnostic/CLEANUP.json')=={'owned_group_absent':True,'errors':[]}
assert L('CLEANUP.json')=={'removed':[path],'errors':[],'capture_error':None}
root=L('ROOT-FINAL-CHECK.json');assert root['status']=='FINITE_MOD_REM_BASELINE_PRESERVATION_PASS' and root['final_pins_sha256']==sha(P/'FINAL-PINS.json')
assert (root['roles'],root['sources'],root['installed_identities'],root['staged_paths'],root['native_paths'])==(620,72,24,925,43)
t=L('ROOT-COMPLETION.json');assert t['session']==44048 and t['actual_exit']==0 and not t['new_acceptance']
print(json.dumps({'status':'FINITE_MOD_REM_TERMINAL_REVIEW_GO','payloads':len(m),'subtests':24,'harnesses':1,'calibrated_targets':16,'strict_guards_pass':8,'roles':620,'source_guards':72,'installed_identities':24,'staged_payloads':925,'native_paths':43,'live_checks':False,'new_acceptance':False},indent=2))
