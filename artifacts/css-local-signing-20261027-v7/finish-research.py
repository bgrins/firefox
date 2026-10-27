import copy, hashlib, importlib.util, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RUN=ROOT/'artifacts/css-counter-scope-append-comparison-execution-v1'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args): return subprocess.check_output(GIT+list(args),cwd=ROOT,env=ENV)
def read(p): return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
admission=read(ROOT/'artifacts/css-counter-scope-append-admission-v1/ADMISSION.json')
flags_before=git('ls-files','-v','-z')
nested_flags_before=h.git(ROOT/'artifacts/css-spec-lean',ENV,'ls-files','-v','-z')
assert hashlib.sha256(flags_before).hexdigest()==admission['index_flags']['root']
assert hashlib.sha256(nested_flags_before).hexdigest()==admission['index_flags']['nested']
result=read(RUN/'RESULT.json');final=read(RUN/'FINAL.json')
assert result['success'] and result['error'] is None and result['recovery_errors']==[]
assert result['captured_phases']==['original-initial','candidate-first','original-restored','candidate-final']
assert result['outstanding_processes']=={} and result['wpt_group'] is None and not (RUN/'FAILURE.json').exists()
try: os.kill(91626,0)
except ProcessLookupError: pass
else: raise RuntimeError('Comparison process still exists; do not publish')
old=read(ROOT/'artifacts/css-counter-scope-append-admission-v1/CURRENT-EPOCH.json')
current=copy.deepcopy(old)
assert set(final['pins'])==set(old['pins'])
changed={p for p in old['pins'] if final['pins'][p]!=old['pins'][p]}
source={'layout/base/nsCounterManager.cpp','layout/base/nsCounterManager.h'}
binaries=set(read(ROOT/'artifacts/css-counter-scope-append-admission-v1/ADMISSION.json')['binaries'])
assert source<=changed<=source|binaries
sp=read(ROOT/'artifacts/css-counter-scope-append-comparison-inputs-v1/SOURCE-PINS.json')
assert all(final['pins'][n]==sp[n]['candidate_sha256'] for n in source)
state=h.index_state(ROOT,ENV)
assert h.semantic_index(state)==h.semantic_index(final['index'])
assert not git('diff','--cached','--name-only')
current['pins']=final['pins']
current['modified_native_paths']=final['modified_native_paths']
current['semantic_index']=h.semantic_index(state)
current['raw_index_observation']['current']=state['raw_index']
current['counts']['native_modified_paths']=len(current['modified_native_paths'])
current['counter_comparison_transition']={'changed_roles':sorted(changed),'result':'artifacts/css-counter-scope-append-comparison-execution-v1/RESULT.json','outer_exit_observed':False,'driver_pid_absent':True}
a.verify_current(h,ROOT,ENV,current)
save(HERE/'POST-COMPARISON-EPOCH.json',current)
ids=['animation-completion','animation-demand','counter-research','fallback-version-trace','typed-attribute-demand']
receipts=[read(HERE/(n+'-presigned.json')) for n in ids]
base=state['head'];parent=base
for r in receipts:
 assert r['parent']==parent and r['branch_before']['head']==base
 assert r['signature_verified']
 assert git('rev-parse',r['commit']+'^').decode().strip()==parent
 assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',r['commit']).decode().splitlines())==sorted(r['files'])
 for n,digest in r['source_pins'].items():
  assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==digest
  assert hashlib.sha256(git('show',r['commit']+':'+n)).hexdigest()==digest
 parent=r['commit']
tip=parent
assert git('rev-parse','refs/codex/css-signing/20261027-v7').decode().strip()==tip
patch=HERE/'presigned-publication.patch'
patch.write_bytes(git('diff','--binary','--full-index',base,tip))
git('apply','--cached','--check',str(patch))
git('apply','--cached',str(patch))
assert git('write-tree').decode().strip()==receipts[-1]['tree']
git('update-ref','refs/heads/stylo-bloom-verification-2',tip,base)
assert not git('diff','--cached','--name-only')
state=h.index_state(ROOT,ENV)
current['semantic_index']=h.semantic_index(state)
current['raw_index_observation']['current']=state['raw_index']
for r in receipts: current['committed_research_working_payloads'].update(r['source_pins'])
current['counts']['committed_research_payloads']=len(current['committed_research_working_payloads'])
a.verify_current(h,ROOT,ENV,current)
flags_after=set(git('ls-files','-v','-z').split(b'\0'))
assert set(flags_before.split(b'\0'))<=flags_after
assert h.git(ROOT/'artifacts/css-spec-lean',ENV,'ls-files','-v','-z')==nested_flags_before
save(HERE/'INITIAL-EPOCH.json',current)
save(HERE/'CURRENT-EPOCH.json',current)
save(HERE/'RESEARCH-PUBLICATION.json',{'base':base,'head':tip,'commits':{n:r['commit'] for n,r in zip(ids,receipts)},'index_empty':True,'preservation_verified':True,'counter_accepted':False})
print('Published five signed research commits:',tip,flush=True)
