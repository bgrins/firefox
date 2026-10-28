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

item=json.loads((HERE/'cycle-model-item.json').read_text())
epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text())
before=json.loads((HERE/'BEFORE.json').read_text())
parent=git('rev-parse','HEAD').decode().strip()
assert parent==item['expected_head']==epoch['semantic_index']['head']
assert git('symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
assert git('config','--get','commit.gpgsign').strip()==b'true'
assert git('diff','--cached','--binary','--full-index',parent)==(HERE/'cycle-model-staged.patch').read_bytes()
assert sorted(git('diff','--cached','--name-only').decode().splitlines())==sorted(item['files'])
for n,pin in item['source_pins'].items():
 assert sha(ROOT/n)==pin
 assert hashlib.sha256(git('show',':'+n)).hexdigest()==pin
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
assert h.semantic_index(h.index_state(ROOT,ENV))['working_diff']==epoch['semantic_index']['working_diff']
tree=git('write-tree').decode().strip()
message=HERE/'cycle-model-message.txt'
assert message.read_text()==item['message'].rstrip()+'\n'
with (HERE/'cycle-model-commit.log').open('w') as f:
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
