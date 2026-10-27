from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'artifacts/css-finite-mod-rem-install-runtime-v2'
D=ROOT/'artifacts/css-finite-mod-rem-comparison-data-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def auth(p,h):
 assert sha(p)==h
 m=read(p)
 for n,v in m.items():assert sha(p.parent/n)==v,n
 return m
manifest='0b285537d94ecbae90e655559a7fcf2049e31370c200ae11d007e880c75d41bf'
m=auth(P/'FILES.json',manifest);L=lambda n:read(P/n)
a,b=L('INPUTS.json'),L('INPUTS.disabled')
assert {k for k in a if a[k]!=b[k]}=={'ready_for_execution','controller_review'} and a['ready_for_execution']
assert a['actual_session'] is None and a['actual_exit'] is None
assert sha(P/'install.py')==a['install_sha256']=='62cfb2f5cb6fbbfb28590779ca4430ad167da7467cf51aa1edc1ebdc7094be8c'
for path,h in a['manifests'].items():auth(ROOT/path/'FILES.json',h)
for k in ['controller_review','acceptance','terminal_review']:
 v=a[k];auth(ROOT/v['path']/'FILES.json',v['manifest_sha256'])
assert L('ROOT-REVIEW-BINDING.json')=={'status':'FINITE_MOD_REM_INSTALL_ROOT_BINDING_GO','inputs_sha256':sha(P/'INPUTS.json'),'install_sha256':a['install_sha256'],'controller_review_manifest_sha256':a['controller_review']['manifest_sha256']}
before,final=L('BEFORE.json'),L('FINAL.json');config=L('CONFIG.json')
assert L('PRE-FLIGHT.json')==before and len(before['pins'])==len(final['pins'])==628
maps=read(D/'SOURCE-MAPS.json');native='servo/components/style/values/generics/calc.rs'
assert before['snapshot']['sources']==maps['baseline'] and final['snapshot']['sources']==maps['candidate']
assert len(maps['candidate'])==72 and {k for k in maps['candidate'] if maps['candidate'][k]!=maps['baseline'][k]}=={native}
assert final['snapshot']['native_diff_sha256']==read(ROOT/'artifacts/css-finite-mod-rem-comparison-runtime-v1/candidate-PRE-CAPTURE.json')['snapshot']['native_diff_sha256']
for k in ['head','index_diff_sha256','index_entries_sha256']:assert before['snapshot'][k]==final['snapshot'][k]
assert len(config['index_expectations']['staged_payload_sha256'])==925 and len(config['modified_native_paths'])==43
owned=L('OWNED-TESTS.json');assert len(owned)==1
path,info=next(iter(owned.items()));assert before['pins'][path] is None and len(info['identity'])==2
fixture=read(D/'CANDIDATE.json')['fixture'][path];assert info['sha256']==fixture['sha256']==sha(ROOT/fixture['source'])
assert len(before['installed_tests'])==24 and len(final['installed_tests'])==25
assert final['installed_tests']=={**before['installed_tests'],**owned}
arc=L('candidate-ARCHITECTURE.json');bins=L('candidate-BINARIES.json')
assert arc['status']=='SUPPORTED_64_BIT_PHASE_BINARIES' and arc['binary_pins']==bins and len(bins)==2
for n,v in arc['binaries'].items():
 h=struct.unpack('<8I',bytes.fromhex(v['header_hex']));assert h[0]==0xfeedfacf and h[1]==16777228 and h[3]==(2 if n.endswith('/firefox') else 6)
 assert v['bits']==64 and v['sha256']==bins[n]
expected={**before['pins'],**maps['candidate'],**bins,path:info['sha256']}
assert final['pins']==L('FINAL-PINS.json')==expected
assert L('candidate-PRE-CAPTURE.json')==final
build=L('candidate-BUILD-SOURCES.json');assert build['before']==build['after']==maps['candidate'] and build['binaries']==bins and build['exit']==0
assert L('candidate-build.json')=={'command':['./mach','build','binaries'],'exit':0}
log=(P/'candidate-build.log').read_text();assert 'Your build was successful!' in log and log.count("KeyError: 'export'")==4
run=L('wpt-candidate/RUN.json');events=[json.loads(s) for s in (P/'wpt-candidate/raw.json').read_text().splitlines() if s.strip()]
for action,key in [('test_status','rows'),('test_start','starts'),('test_end','ends')]:assert [e for e in events if e.get('action')==action]==run[key]
assert run['complete'] and not run['infrastructure_faults'] and run['exit']==0 and run['before']==run['after']==expected
test='/'+path.removeprefix('testing/web-platform/tests/')
names=read(D/'ROSTER.json')['expected_subtests'][test]
assert len(names)==24 and len(run['rows'])==24 and len(run['starts'])==len(run['ends'])==1
assert all(e['status']=='PASS' and e.get('expected','PASS')=='PASS' and not e.get('known_intermittent') for e in run['rows'])
assert run['ends'][0]['status']=='OK' and run['ends'][0].get('expected','OK')=='OK'
started=ended=False;active=None;observed=[]
for e in events:
 act=e.get('action')
 if act=='suite_start':assert not started;started=True
 elif act=='test_start':assert started and not ended and active is None and e['test']==test;active=test
 elif act=='test_status':assert active==e['test'];observed.append(e['subtest'])
 elif act=='test_end':assert active==e['test'] and observed==names;active=None
 elif act=='suite_end':assert started and not ended and active is None and observed==names;ended=True
assert started and ended
def norm(r):return {k:r.get(k) for k in ['test','subtest','status','message','expected']}|{'effective_expected':r.get('expected',r['status']),'known_intermittent':r.get('known_intermittent',[])}
assert [norm(r) for r in run['rows']]==L('candidate-OUTCOMES.json')
assert L('wpt-candidate/CLEANUP.json')=={'owned_group_absent':True,'errors':[]}
summary=L('candidate-SUMMARY.json');assert summary['status']=='PHASE_EXACT_POLICY_PASS' and summary['counts']=={'PASS':24,'FAIL':0} and summary['required_repairs']==16 and summary['additional_improvements']==0 and not summary['errors']
assert len(L('candidate-DIFFERENCES.json'))==len(L('candidate-IMPROVEMENTS.json'))==16
assert L('CLEANUP.json')=={'removed':[],'retained':[path],'errors':[],'installation_error':None}
result=L('RESULT.json');assert result['status']=='ACCEPTED_FIX_INSTALLED' and result['installed'] and result['candidate_ready'] and not result['restored']
assert result['fix']==128 and result['completed_phases']==result['captured_phases']==['candidate'] and result['installation_error'] is None and not result['recovery_errors']
assert result['source_transitions']==[L('source-write-1.json')]==[{'path':native,'from':maps['baseline'][native],'to':maps['candidate'][native],'recovery':False}]
assert not any(n.startswith('RECOVERY-') for n in m)
root=L('ROOT-COMPLETION.json');assert sha(P/'ROOT-COMPLETION.json')=='629014c8370e8d46b60ffcbaea05f33106ff0c5d2e1d8beb1f1783c4c9970334'
assert root['session']==71619 and root['actual_exit']==0 and root['installed'] and root['source_sha256']==maps['candidate'][native]
for field,name in [('final_sha256','FINAL.json'),('final_pins_sha256','FINAL-PINS.json'),('result_sha256','RESULT.json')]:assert root[field]==sha(P/name)
assert L('ROOT-VERIFICATION.json')=={'session':60587,'actual_exit':0,'terminal_chunk':'b24fae','installation_session':71619,'installation_exit':0,'receipt':'ROOT-COMPLETION.json'}
assert sha(P/'FILES.json')==manifest
print(json.dumps({'status':'FINITE_MOD_REM_INSTALL_TERMINAL_REVIEW_GO','session':71619,'actual_exit':0,'runtime_manifest':manifest,'root_receipt':sha(P/'ROOT-COMPLETION.json'),'installed':True,'subtests_pass':24,'harnesses_ok':1,'source_guards':72,'roles':628,'installed_identities':25,'prior_identities_preserved':24,'staged_payloads':925,'native_paths':43,'build_exit':0,'nonfatal_progress_keyerrors':4,'recovery':False,'live_checks':False,'new_native_acceptance':False},indent=2))
