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
if sys.argv[1]=='init':
 old=ROOT/'artifacts/css-steps-jump-none-continuation-runtime-v1/CURRENT-EPOCH.json'
 epoch=json.loads(old.read_text());before=a.verify_current(h,ROOT,ENV,epoch)
 epoch['historical_raw_index_observation']=epoch['raw_index_observation']
 epoch['raw_index_observation']={'current':before['index']['raw_index'],'prior_comparison_raw_drift_cause':'unknown; semantic staging preserved'}
 save(HERE/'INITIAL-EPOCH.json',epoch);save(HERE/'CURRENT-EPOCH.json',epoch);save(HERE/'BEFORE.json',before)
 print('Full preservation epoch verified',len(epoch['pins']));sys.exit(0)
item=json.loads(Path(sys.argv[1]).read_text());epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text())
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref','HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
before=a.verify_current(h,ROOT,ENV,epoch);parent=git('rev-parse','HEAD').decode().strip()
assert git('config','--get','commit.gpgsign').strip()==b'true'
item['expected_head']=parent;item['execution_enabled']=True
bound=HERE/(item['id']+'-item.json')
if bound.exists(): assert json.loads(bound.read_text())==item
else: save(bound,item)
for n,pin in item['source_pins'].items(): assert sha(ROOT/n)==pin,n
with tempfile.TemporaryDirectory(prefix='css-signing-index-',dir='/private/tmp') as tmp:
 env=dict(ENV,GIT_INDEX_FILE=str(Path(tmp)/'index'));git('read-tree',parent,env=env)
 if 'patch' in item:
  patch=ROOT/item['patch'];assert sha(patch)==item['patch_sha256'];git('apply','--cached','--check',str(patch),env=env);git('apply','--cached',str(patch),env=env)
 else:
  names=Path(tmp)/'paths';names.write_bytes(b''.join(n.encode()+b'\0' for n in item['files']))
  git('add','-f','--pathspec-from-file='+str(names),'--pathspec-file-nul',env=env)
 assert sorted(git('diff','--cached','--name-only',parent,env=env).decode().splitlines())==sorted(item['files'])
 for n,pin in item['source_pins'].items():
  assert hashlib.sha256(git('show',':'+n,env=env)).hexdigest()==pin,n
  mode=git('ls-files','--stage','--',n,env=env).decode().split()[0]
  assert mode==str(item.get('source_modes',{}).get(n,'100644')), (n,mode)
 tree=git('write-tree',env=env).decode().strip()
 patch_bytes=git('diff','--cached','--binary','--full-index',parent,env=env)
 live_patch=HERE/(item['id']+'-staged.patch');live_patch.write_bytes(patch_bytes)
 git('apply','--cached','--check',str(live_patch));git('apply','--cached',str(live_patch))
 assert git('write-tree').decode().strip()==tree
message=HERE/(item['id']+'-message.txt');message.write_text(item['message'].rstrip()+'\n')
with (HERE/(item['id']+'-commit.log')).open('w') as f:
 rc=subprocess.run(GIT+['commit','--file',str(message)],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,'Commit failed; staging preserved; inspect log'
commit=git('rev-parse','HEAD').decode().strip();assert git('rev-parse',commit+'^').decode().strip()==parent
assert git('rev-parse',commit+'^{tree}').decode().strip()==tree
with (HERE/(item['id']+'-signature.log')).open('w') as f:
 subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
state=h.index_state(ROOT,ENV);assert not git('diff','--cached','--name-only')
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
current=copy.deepcopy(epoch);current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
current['modified_native_paths']=sorted(n for n in git('diff','--name-only').decode().splitlines() if not n.startswith('artifacts/'))
assert set(epoch['modified_native_paths'])-set(current['modified_native_paths'])==set(epoch['modified_native_paths']) & {n for n in item['files'] if not n.startswith('artifacts/')}
assert set(current['modified_native_paths'])<=set(epoch['modified_native_paths'])
for n,pin in item['source_pins'].items():
 if n.startswith('artifacts/'): current['committed_research_working_payloads'][n]=pin
current['counts']['native_modified_paths']=len(current['modified_native_paths']);current['counts']['committed_research_payloads']=len(current['committed_research_working_payloads'])
after=a.verify_current(h,ROOT,ENV,current)
save(HERE/(item['id']+'-receipt.json'),{'commit':commit,'parent':parent,'tree':tree,'files':item['files'],'signature_verified':True,'working_bodies_and_nested_index_preserved':True})
save(HERE/(item['id']+'-EPOCH.json'),current)
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Signed and verified',item['id'],commit,flush=True)
