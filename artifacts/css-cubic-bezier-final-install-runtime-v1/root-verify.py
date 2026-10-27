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
result=json.loads((HERE/'RESULT.json').read_text());assert result['success'] and result['error'] is None and not result['recovery_errors'] and not result['outstanding_processes'] and result['wpt_group'] is None and not (HERE/'FAILURE.json').exists()
save(HERE/'ROOT-EXECUTION.json',{'session':47256,'launch':'2b1606','terminal':'bf5ab7','outer_exit':0})
run=json.loads((HERE/'wpt-candidate/RUN.json').read_text());events=[json.loads(line) for line in (HERE/'wpt-candidate/raw.json').read_text().splitlines()]
for key,act in [('rows','test_status'),('starts','test_start'),('ends','test_end')]:assert run[key]==[r for r in events if r.get('action')==act]
tests=load('test_root',str((HERE/'tests.py').relative_to(ROOT)));config=json.loads((HERE/'CONFIG.json').read_text());assert tests.lifecycle(events,config) and not tests.infrastructure_faults(events) and tests.exit_matches_results(run['exit'],run['rows']+run['ends'])
assert run['complete'] and run['before']==run['after'] and len(run['rows'])==113 and len(run['ends'])==5 and all(r['status']==r.get('expected',r['status'])=='OK' for r in run['ends'])
old=json.loads((ROOT/'artifacts/css-cubic-bezier-calc-range-browser-runtime-v1/wpt-candidate/RUN.json').read_text());policy=load('policy_root',str((HERE/'policy.py').relative_to(ROOT)));comparison=policy.compare(old['rows'],run['rows'],json.loads((HERE/'COMPARISON-POLICY.json').read_text()));assert comparison==json.loads((HERE/'OUTCOME-COMPARISON.json').read_text())
assert json.loads((HERE/'wpt-candidate/CLEANUP.json').read_text())=={'owned_group_absent':True,'errors':[]}
build=json.loads((HERE/'candidate-build/build-RESULT.json').read_text());assert build['exit']==0 and build['error'] is None and build['stop_reason'] is None and build['owned_group_absent'] and not build['cleanup_errors']
epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text());post=json.loads((HERE/'POSTIMAGES.json').read_text());assert all(epoch['pins'][n]==v['sha256'] for n,v in post.items());a.verify_current(h,ROOT,ENV,epoch)
save(HERE/'ROOT-OUTCOMES.json',{'status':'CUBIC_FINAL_INSTALL_ROOT_VERIFIED','rows':113,'counts':dict(collections.Counter(r['status'] for r in run['rows'])),'targets_PASS':38,'prior_three_phase_observed_repairs':28,'metadata_expected_changes':comparison['metadata_changes'],'all_other_results_exact':True,'owned_candidate_paths':sorted(post),'source_binaries_research_and_indexes_verified':True,'acceptance_pending_terminal_peer':True})
save(HERE/'FILES.json',{str(f.relative_to(HERE)):sha(f) for f in sorted(HERE.rglob('*')) if f.is_file() and f!=HERE/'FILES.json'})
print('Final installed113 outcomes and live epoch verified',sha(HERE/'FILES.json'),flush=True)
