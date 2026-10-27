import copy,hashlib,importlib.util,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
RUN=ROOT/'artifacts/css-keyframe-typed-attribute-demand-runtime-v1'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0');GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT,env=ENV)
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
phase=read(RUN/'binaries-2/RESULT.json');assert phase['owned_processes']=={}
command=read(RUN/'binaries-2/COMMAND.json')
try:os.kill(command['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Native phase driver still active')
epoch=read(RUN/'CURRENT-EPOCH.json');before=a.verify_current(h,ROOT,ENV,epoch)
flags=git('ls-files','-v','-z');nestedflags=h.git(ROOT/'artifacts/css-spec-lean',ENV,'ls-files','-v','-z')
ids=read(HERE/'ORDER.json');receipts=[read(HERE/(n+'-presigned.json')) for n in ids]
base=before['index']['head'];parent=base
pins={}
for r in receipts:
 assert r['parent']==parent and r['branch_before']['head']==base and r['signature_verified']
 assert git('rev-parse',r['commit']+'^').decode().strip()==parent
 assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',r['commit']).decode().splitlines())==sorted(r['files'])
 for n,digest in r['source_pins'].items():
  assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==digest,n
  assert hashlib.sha256(git('show',r['commit']+':'+n)).hexdigest()==digest,n
 pins.update(r['source_pins']);parent=r['commit']
assert git('rev-parse','refs/codex/css-signing/20261027-v8').decode().strip()==parent
save(HERE/'PRE-PUBLICATION-EPOCH.json',epoch)
patch=HERE/'publication.patch';patch.write_bytes(git('diff','--binary','--full-index',base,parent))
git('apply','--cached','--check',str(patch));git('apply','--cached',str(patch))
assert git('write-tree').decode().strip()==receipts[-1]['tree']
git('update-ref','refs/heads/stylo-bloom-verification-2',parent,base)
assert not git('diff','--cached','--name-only')
current=copy.deepcopy(epoch);state=h.index_state(ROOT,ENV)
current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
current['committed_research_working_payloads'].update(pins)
current['counts']['committed_research_payloads']=len(current['committed_research_working_payloads'])
a.verify_current(h,ROOT,ENV,current)
assert set(flags.split(b'\0'))<=set(git('ls-files','-v','-z').split(b'\0'))
assert h.git(ROOT/'artifacts/css-spec-lean',ENV,'ls-files','-v','-z')==nestedflags
save(HERE/'CURRENT-EPOCH.json',current)
(RUN/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
save(HERE/'PUBLICATION.json',{'base':base,'head':parent,'commits':{n:r['commit'] for n,r in zip(ids,receipts)},'index_empty':True,'sources_and_nested_preserved':True,'accepted_fix_count':135,'native_phase_result':phase})
print('Published signed local research chain:',parent,flush=True)
