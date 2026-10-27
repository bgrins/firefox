import copy, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args,env=ENV): return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
import collections
result=json.loads((HERE/'RESULT.json').read_text());assert result['success'] and result['error'] is None and not result['recovery_errors'] and not result['outstanding_processes'] and result['wpt_group'] is None
save(HERE/'ROOT-EXECUTION.json',{'session':28659,'launch':'6358bf','terminal':'cf8896','outer_exit':0})
policy=json.loads((HERE/'COMPARISON-POLICY.json').read_text());roster=json.loads((HERE/'CANDIDATE-ROSTER.json').read_text());required={(r['test'],r['subtest']) for r in policy['candidate_mandatory_pass']};controls={(r['test'],r['subtest']) for r in policy['exact_fresh_control_identities']}
assert len(required)==38 and len(controls)==75 and not required&controls
maps={};counts={}
tests=load('tests_root',str((HERE/'tests.py').relative_to(ROOT)))
for phase in ['original','candidate','restored']:
 d=HERE/('wpt-'+phase);run=json.loads((d/'RUN.json').read_text());raw=[json.loads(line) for line in (d/'raw.json').read_text().splitlines()]
 for key,action in [('rows','test_status'),('starts','test_start'),('ends','test_end')]:assert run[key]==[e for e in raw if e.get('action')==action]
 assert run['complete'] and run['before']==run['after'] and not run['infrastructure_faults'] and not tests.infrastructure_faults(raw)
 assert tests.lifecycle(raw,{'expected_subtests':roster,'reftests':[]}) and tests.exit_matches_results(run['exit'],run['rows']+run['ends'])
 assert len(run['starts'])==len(run['ends'])==5 and all(r['status']==r.get('expected',r['status'])=='OK' for r in run['ends'])
 assert json.loads((d/'CLEANUP.json').read_text())=={'owned_group_absent':True,'errors':[]}
 normalize=lambda r:{'status':r['status'],'message':r.get('message'),'expected':r.get('expected',r['status']),'known_intermittent':r.get('known_intermittent',[])}
 values={(r['test'],r['subtest']):normalize(r) for r in run['rows']};assert len(values)==len(run['rows'])==113 and set(values)==required|controls
 for name,names in roster.items():assert [r['subtest'] for r in run['rows'] if r['test']==name]==names
 maps[phase]=values;counts[phase]=dict(collections.Counter(r['status'] for r in run['rows']))
assert maps['original']==maps['restored'];assert all(maps['candidate'][k]==maps['original'][k] for k in controls)
assert all(maps['candidate'][k]['status']=='PASS' and maps['candidate'][k]['message'] in (None,'') for k in required)
for k in required:
 for field in ['expected','known_intermittent']:assert maps['candidate'][k][field]==maps['original'][k][field]
repairs=sum(maps['original'][k]['status']=='FAIL' for k in required);assert repairs==28
for phase in ['candidate','restored']:
 build=json.loads((HERE/(phase+'-build')/'build-RESULT.json').read_text());assert build['exit']==0 and build['error'] is None and build['stop_reason'] is None and build['owned_group_absent'] and not build['cleanup_errors']
old=json.loads((ROOT/'artifacts/css-steps-committed-build-runtime-v1/CURRENT-EPOCH.json').read_text());final=json.loads((HERE/'FINAL.json').read_text());epoch=copy.deepcopy(old);epoch['pins']=final['pins'];epoch['counts']['roles']=len(final['pins']);epoch['semantic_index']=h.semantic_index(final['index']);assert epoch['semantic_index']==old['semantic_index']
epoch['raw_index_observation']={'current':final['index']['raw_index'],'before_comparison':json.loads((HERE/'BEFORE.json').read_text())['index']['raw_index'],'bytes_equal':final['index']['raw_index']==json.loads((HERE/'BEFORE.json').read_text())['index']['raw_index'],'cause_if_changed':'not established'}
verified=a.verify_current(h,ROOT,ENV,epoch);save(HERE/'CURRENT-EPOCH.json',epoch)
save(HERE/'ROOT-OUTCOMES.json',{'status':'CUBIC_THREE_PHASE_RAW_OUTCOMES_ROOT_VERIFIED','counts':counts,'candidate_targets_pass':38,'observed_repairs':repairs,'controls_exact':75,'restored_exact':113,'harness_OK_per_phase':5,'final_roles':len(epoch['pins']),'current_live_preservation_verified':True,'raw_index':epoch['raw_index_observation'],'acceptance_pending_metadata_capture':True})
save(HERE/'FILES.json',{str(f.relative_to(HERE)):sha(f) for f in sorted(HERE.rglob('*')) if f.is_file() and f.name!='FILES.json'})
print('Root verified all113 outcomes and live epoch; runtime sealed',sha(HERE/'FILES.json'),flush=True)
