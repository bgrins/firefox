from pathlib import Path
import json,hashlib,collections,struct
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'artifacts/css-finite-mod-rem-comparison-runtime-v1';D=ROOT/'artifacts/css-finite-mod-rem-comparison-data-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def auth(p,h):
 assert sha(p)==h
 m=read(p)
 for n,v in m.items():assert sha(p.parent/n)==v,n
 return m
m=auth(P/'FILES.json','ce1ecc4f7d101c22a44f0540f36ff78bc2ae54c76149e0618e7e6ca584d2c3c8');L=lambda n:read(P/n)
a,b=L('INPUTS.json'),L('INPUTS.disabled.json')
assert {k for k in a if a[k]!=b[k]}=={'ready_for_execution','controller_review'} and a['ready_for_execution']
assert a['actual_session'] is None and a['actual_exit'] is None
assert sha(P/'compare.py')==a['compare_sha256']=='786a84d3f249599a1508b3be948431c925fb361fc01229733a79f63e6758ba6e'
for path,h in a['manifests'].items():auth(ROOT/path/'FILES.json',h)
auth(ROOT/a['controller_review']['path']/'FILES.json',a['controller_review']['manifest_sha256'])
assert L('ROOT-REVIEW-BINDING.json')=={'status':'FINITE_MOD_REM_COMPARISON_ROOT_BINDING_GO','inputs_sha256':sha(P/'INPUTS.json'),'compare_sha256':a['compare_sha256'],'controller_review_manifest_sha256':a['controller_review']['manifest_sha256']}
ro=read(D/'ROSTER.json');maps=read(D/'SOURCE-MAPS.json');resource=read(D/'RESOURCES.json');config=L('CONFIG.json')
assert all(config[k]==v for k,v in ro.items()) and ro['expected_total']==700 and len(ro['tests'])==10 and not ro['reftests']
assert len(config['index_expectations']['staged_payload_sha256'])==925 and len(config['modified_native_paths'])==43
before=L('BEFORE.json');final=L('FINAL.json');pre=L('PRE-FLIGHT.json');assert len(resource)==628 and resource==L('BASELINE-PINS.json')
assert pre==dict(before,pins=resource)
assert final['snapshot']==before['snapshot'] and final['installed_tests']==before['installed_tests'] and len(final['installed_tests'])==24
assert len(before['snapshot']['sources'])==72 and final['pins']==L('FINAL-PINS.json')
owned=L('OWNED-TESTS.json');assert len(owned)==1
path,info=next(iter(owned.items()));assert resource[path] is None and len(info['identity'])==2
fixture=read(D/'CANDIDATE.json')['fixture'][path];assert info['sha256']==fixture['sha256']==sha(ROOT/fixture['source'])
bins={};normalized={};counts={};log_issues={}
def norm(rows):
 out={}
 for r in rows:
  k=(r['test'],r['subtest']);assert k not in out
  out[k]={'test':k[0],'subtest':k[1],'status':r['status'],'message':r.get('message'),'expected':r.get('expected'),'effective_expected':r.get('expected',r['status']),'known_intermittent':r.get('known_intermittent',[])}
 return out
for label,phase in [('baseline_capture','baseline'),('candidate','candidate'),('restored','restored')]:
 arc=L(('baseline' if phase=='baseline' else label)+'-ARCHITECTURE.json');assert arc['status']=='SUPPORTED_64_BIT_PHASE_BINARIES';bins[phase]=arc['binary_pins'];assert len(bins[phase])==2
 for n,v in arc['binaries'].items():
  h=struct.unpack('<8I',bytes.fromhex(v['header_hex']));assert h[0]==0xfeedfacf and h[1]==16777228 and v['bits']==64 and v['sha256']==bins[phase][n]
  assert h[3]==(2 if n.endswith('/firefox') else 6)
 expected={**resource,**maps[phase],**bins[phase],path:info['sha256']}
 cap=L(label+'-PRE-CAPTURE.json');assert cap['pins']==expected and cap['snapshot']['sources']==maps[phase] and cap['installed_tests']==before['installed_tests']
 for k in ['head','index_diff_sha256','index_entries_sha256']:assert cap['snapshot'][k]==before['snapshot'][k]
 if phase!='candidate':assert cap['snapshot']==before['snapshot']
 run=L('wpt-'+label+'/RUN.json');events=[json.loads(s) for s in (P/('wpt-'+label)/'raw.json').read_text().splitlines() if s.strip()]
 for action,key in [('test_status','rows'),('test_start','starts'),('test_end','ends')]:assert [e for e in events if e.get('action')==action]==run[key]
 assert run['complete'] and not run['infrastructure_faults'] and run['before']==run['after']==expected
 assert len(run['rows'])==700 and len(run['starts'])==len(run['ends'])==10
 assert set(e['test'] for e in run['starts'])==set(ro['expected_subtests'])==set(e['test'] for e in run['ends'])
 assert all(e['status']=='OK' and e.get('expected','OK')=='OK' and not e.get('known_intermittent') for e in run['ends'])
 started=ended=False;active=None;seen=set();names=[]
 for e in events:
  act=e.get('action')
  if act=='suite_start':assert not started;started=True
  elif act=='test_start':assert started and not ended and active is None and e['test'] not in seen;active=e['test'];seen.add(active);names=[]
  elif act=='test_status':assert active==e['test'] and e['status'] in ('PASS','FAIL');names.append(e['subtest'])
  elif act=='test_end':assert active==e['test'] and names==ro['expected_subtests'][active];active=None
  elif act=='suite_end':assert started and not ended and active is None and seen==set(ro['expected_subtests']);ended=True
 assert started and ended
 unexpected=any(e['status']!=e.get('expected',e['status']) and e['status'] not in e.get('known_intermittent',[]) for e in run['rows']+run['ends'])
 assert run['exit']==int(unexpected)
 normalized[phase]=norm(run['rows']);assert normalized[phase]=={(r['test'],r['subtest']):r for r in L(label+'-OUTCOMES.json')}
 counts[phase]=dict(collections.Counter(r['status'] for r in run['rows']))
 assert L('wpt-'+label+'/CLEANUP.json')=={'owned_group_absent':True,'errors':[]}
 summary=L(label+'-SUMMARY.json');assert summary['status']=='PHASE_EXACT_POLICY_PASS' and not summary['errors']
 if phase!='baseline':
  build=L(label+'-BUILD-SOURCES.json');assert build['before']==build['after']==maps[phase] and build['exit']==0 and build['binaries']==bins[phase]==L(label+'-BINARIES.json')
  assert L(label+'-build.json')=={'command':['./mach','build','binaries'],'exit':0}
  log=(P/(label+'-build.log')).read_text();assert 'Your build was successful!' in log and "KeyError: 'export'" in log
  log_issues[label]=log.count("KeyError: 'export'")
observed=norm(read(D/'OBSERVED-LANDING-BASELINE.json')['rows']);assert all(normalized['baseline'][k]==v for k,v in observed.items())
repairs={k for k,v in observed.items() if v['status']=='FAIL'};assert len(repairs)==16
changed={k for k in normalized['baseline'] if normalized['baseline'][k]!=normalized['candidate'][k]};assert changed==repairs
for k in repairs:assert normalized['candidate'][k]==dict(normalized['baseline'][k],status='PASS',message=None,expected=None,effective_expected='PASS',known_intermittent=[])
assert normalized['restored']==normalized['baseline']
assert counts=={'baseline':{'PASS':684,'FAIL':16},'candidate':{'PASS':700},'restored':{'PASS':684,'FAIL':16}}
assert len(L('candidate-DIFFERENCES.json'))==len(L('candidate-IMPROVEMENTS.json'))==16
assert not L('restored-DIFFERENCES.json') and not L('restored-IMPROVEMENTS.json') and not L('baseline_capture-DIFFERENCES.json')
assert final['pins']=={**resource,**bins['restored']} and all(final['pins'][n]==h for n,h in before['pins'].items() if n not in bins['restored'])
assert L('CLEANUP.json')=={'removed':[path],'errors':[],'comparison_error':None}
result=L('RESULT.json');assert result['completed_phases']==['baseline','candidate','restored'] and result['captured_phases']==['baseline_capture','candidate','restored'] and result['comparison_error'] is None and not result['recovery_errors']
assert result['mutation_started'] and result['fresh_baseline_established'] and result['restoration_capture_required']
trans=result['source_transitions'];assert len(trans)==2 and [L('source-write-1.json'),L('source-write-2.json')]==trans
native,=read(D/'CANDIDATE.json')['native_paths'];assert trans==[{'path':native,'from':maps['baseline'][native],'to':maps['candidate'][native],'recovery':False},{'path':native,'from':maps['candidate'][native],'to':maps['baseline'][native],'recovery':True}]
root=L('ROOT-FINAL-CHECK.json');assert root['status']=='ORIGINAL_STACK_RESTORED_VERIFIED' and root['final_pins_sha256']==sha(P/'FINAL-PINS.json') and not root['recovery_errors'] and root['comparison_error'] is None
terminal=L('ROOT-COMPLETION.json');assert terminal['session']==59511 and terminal['actual_exit']==0 and terminal['roles_live_verified']==628 and terminal['installed_identities_live_verified']==24 and terminal['built_binary_pins']==bins['restored']
assert sha(P/'FILES.json')=='ce1ecc4f7d101c22a44f0540f36ff78bc2ae54c76149e0618e7e6ca584d2c3c8'
print(json.dumps({'status':'MOD_REM_COMPARISON_TERMINAL_REVIEW_GO','runtime_manifest':sha(P/'FILES.json'),'root_receipt':sha(P/'ROOT-FINAL-CHECK.json'),'counts':counts,'repairs':16,'other_changes':0,'restored_exact':True,'payloads':len(m),'roles':628,'source_guards':72,'installed_identities':24,'stage_paths':925,'native_paths':43,'builds':{'candidate':0,'restored':0},'nonfatal_progress_keyerror_counts':log_issues,'live_review_checks':False,'native_acceptance':False},indent=2))
