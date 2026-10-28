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

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode=True
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
staged=load('staged_epoch','artifacts/css-registered-provider-expanded-observation-v3/epoch.py')
item=json.loads((HERE/'cycle-model-item.json').read_text())
epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text())
assert sha(HERE/'INITIAL-EPOCH.json')=='f9576f394e34255b01dadf3f272347f4c3266362a01081c0dbda3085e521afcd'
runtime=ROOT/'artifacts/css-registered-number-native-runtime-v1'
assert (runtime/'CURRENT-EPOCH.json').read_bytes()==(HERE/'INITIAL-EPOCH.json').read_bytes()
assert sha(runtime/'ROLE.json')=='c44875d0dea1455e6f58e4410950ff986aa0a57ab8af6e2e5f7cf5d7db377573'
assert epoch['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert epoch['registered_number_transition']=={'role':'candidate','variant':'registered-provider-default-v5','compiled':False,'accepted':False,'last_phase':'provider-default-partial-v5-install-1'}
assert len(item['files'])==36 and set(epoch['staged_working'])==set(item['files'])
before=staged.verify_current(h,ROOT,ENV,epoch)
save(HERE/'BEFORE.json',before)
controls={n:(runtime/n).read_bytes() for n in ['CURRENT-EPOCH.json','ROLE.json','OWNED.json']}
for n,b in controls.items(): (HERE/('PRE-'+n)).write_bytes(b)
flags={n:h.git(ROOT/n,ENV,'ls-files','-v','-z') for n in ['.','artifacts/css-spec-lean']}
assert sha(ROOT/'artifacts/css-registered-number-native-runtime-v1/provider-default-partial-v5-install-1/RESULT.json')=='1db7f1b14fe4a1338a00af24a92a710a2ae7bb76138ab275009e8706be7b234f'
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
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
assert staged.verify_current(h,ROOT,ENV,epoch)==before
assert all((runtime/n).read_bytes()==b for n,b in controls.items())
assert all(h.git(ROOT/n,ENV,'ls-files','-v','-z')==b for n,b in flags.items())
tree=git('write-tree').decode().strip()
message=HERE/'cycle-model-message.txt'
assert message.read_text()==item['message'].rstrip()+'\n'
with (HERE/'cycle-model-commit.log').open('x') as f:
 rc=subprocess.run(GIT+['commit','--file',str(message)],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,'Commit failed; staging preserved; inspect log'
commit=git('rev-parse','HEAD').decode().strip();assert git('rev-parse',commit+'^').decode().strip()==parent
assert git('rev-parse',commit+'^{tree}').decode().strip()==tree
with (HERE/(item['id']+'-signature.log')).open('x') as f:
 subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
state=h.index_state(ROOT,ENV);assert not git('diff','--cached','--name-only')
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
assert all((runtime/n).read_bytes()==b for n,b in controls.items())
assert all(h.git(ROOT/n,ENV,'ls-files','-v','-z')==b for n,b in flags.items())
current=copy.deepcopy(epoch);current['staged_working']={};current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
current['modified_native_paths']=sorted(n for n in git('diff','--name-only').decode().splitlines() if not n.startswith('artifacts/'))
assert set(epoch['modified_native_paths'])-set(current['modified_native_paths'])==set(epoch['modified_native_paths']) & {n for n in item['files'] if not n.startswith('artifacts/')}
assert current['modified_native_paths']==epoch['modified_native_paths']
assert current['semantic_index']['working_diff']==epoch['semantic_index']['working_diff']
for n,pin in item['source_pins'].items():
 if n.startswith('artifacts/'): current['committed_research_working_payloads'][n]=pin
current['counts']['native_modified_paths']=len(current['modified_native_paths']);current['counts']['committed_research_payloads']=len(current['committed_research_working_payloads'])
after=a.verify_current(h,ROOT,ENV,current)
save(HERE/(item['id']+'-receipt.json'),{'commit':commit,'parent':parent,'tree':tree,'files':item['files'],'signature_verified':True,'working_bodies_and_nested_index_preserved':True})
save(HERE/(item['id']+'-EPOCH.json'),current)
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Signed and verified',item['id'],commit,flush=True)
