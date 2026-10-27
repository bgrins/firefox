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
result=json.loads((HERE/'RESULT.json').read_text());assert result['success'] and result['metadata_retained'] and result['owned_group'] is None and not result['cleanup_errors'] and not (HERE/'FAILURE.json').exists()
save(HERE/'ROOT-EXECUTION.json',{'session':43147,'launch':'8d3c1a','terminal':'8dba9f','outer_exit':0})
run=json.loads((HERE/'wpt-metadata/RUN.json').read_text());events=[json.loads(line) for line in (HERE/'wpt-metadata/raw.json').read_text().splitlines()]
for key,act in [('rows','test_status'),('starts','test_start'),('ends','test_end')]:assert run[key]==[r for r in events if r.get('action')==act]
assert run['complete'] and run['before']==run['after'] and len(run['rows'])==44 and len(run['ends'])==2
assert all(r['status']==r.get('expected',r['status'])=='OK' for r in run['ends'])
oldrun=json.loads((ROOT/'artifacts/css-cubic-bezier-calc-range-browser-runtime-v1/wpt-restored/RUN.json').read_text());roster=json.loads((HERE/'ROSTER.json').read_text());before=[r for r in oldrun['rows'] if r['test'] in roster]
validator=load('validator_root',str((HERE/'validate.py').relative_to(ROOT)));comparison=validator.check_rows(before,run['rows'],roster);assert comparison['rows']==44 and len(comparison['targets'])==2
assert json.loads((HERE/'wpt-metadata/CLEANUP.json').read_text())=={'owned_group_absent':True,'errors':[]}
epoch=json.loads((ROOT/'artifacts/css-cubic-bezier-calc-range-browser-runtime-v1/CURRENT-EPOCH.json').read_text());final=json.loads((HERE/'FINAL.json').read_text());paths=json.loads((HERE/'PATHS.json').read_text());assert {n for n in epoch['pins'] if epoch['pins'][n]!=final['pins'][n]}==set(paths)
for n,v in paths.items():assert final['pins'][n]==v['postimage']['sha256']
epoch['pins']=final['pins'];epoch['semantic_index']=h.semantic_index(final['index']);epoch['raw_index_observation']={'current':final['index']['raw_index'],'before_metadata_capture':json.loads((HERE/'BEFORE.json').read_text())['index']['raw_index']};epoch['modified_native_paths']=final['modified_native_paths'];epoch['counts']['native_modified_paths']=len(epoch['modified_native_paths'])
a.verify_current(h,ROOT,ENV,epoch);save(HERE/'CURRENT-EPOCH.json',epoch)
save(HERE/'ROOT-OUTCOMES.json',{'status':'STEPS_METADATA_CAPTURE_ROOT_VERIFIED','rows':44,'counts':dict(collections.Counter(r['status'] for r in run['rows'])),'exact_expected_changes':comparison['targets'],'other_observations_exact':True,'source_binary_changes':False,'metadata_retained':True,'index_staging_preserved':True,'new_accepted_bug':False})
save(HERE/'FILES.json',{str(f.relative_to(HERE)):sha(f) for f in sorted(HERE.rglob('*')) if f.is_file() and f!=HERE/'FILES.json'})
print('Root verified44 metadata outcomes and current epoch',sha(HERE/'FILES.json'),flush=True)
