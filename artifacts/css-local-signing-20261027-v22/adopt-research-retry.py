import hashlib
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
source=(Path(__file__).resolve().parent/'commit.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='ef3b5cafed2f379372c2cc6948fee914a6a90d176ae9151baee9b34d89ca8ceb'
exec(compile(source.split("if sys.argv[1]=='init':",1)[0],'reviewed-commit-helper-prefix','exec'))
read=lambda p:json.loads(p.read_text())
assert len(sys.argv)==3,'Supply exact successful retry commit and successful retry log basename'
commit=sys.argv[1]
successful_log_name=sys.argv[2]
assert Path(successful_log_name).name==successful_log_name
assert successful_log_name.startswith('research-retry-') and successful_log_name.endswith('-commit.log')
retry_number=successful_log_name.removeprefix('research-retry-').removesuffix('-commit.log')
assert retry_number.isdigit() and int(retry_number)>=2
successful_log=HERE/successful_log_name
assert not successful_log.is_symlink() and stat.S_ISREG(successful_log.lstat().st_mode)
assert sha(successful_log) not in {sha(HERE/'research-commit.log'),sha(HERE/'research-retry-1-commit.log')}
item=read(HERE/'research-selection.json');inputs=read(HERE/'INPUTS.json');epoch=read(HERE/'CURRENT-EPOCH.json')
parent=inputs['frozen_head'];selected=set(item['files'])
assert item['id']=='research' and len(selected)==207 and inputs['ready']
assert read(HERE/'research-item.json')==item|{'expected_head':parent,'execution_enabled':True}
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
assert git('rev-parse','HEAD').decode().strip()==commit
assert git('rev-parse',commit+'^').decode().strip()==parent==epoch['semantic_index']['head']
assert git('rev-list','--parents','-n','1',commit).decode().split()==[commit,parent]
assert not git('diff','--cached','--name-only')
assert git('diff','--binary','--full-index',parent,commit)==(HERE/'research-staged.patch').read_bytes()
assert set(git('diff','--name-only',parent,commit).decode().splitlines())==selected
assert git('show','-s','--format=%B',commit).decode().rstrip()==item['message'].rstrip()
for n,pin in item['source_pins'].items():
 assert n.startswith('artifacts/') and sha(ROOT/n)==pin
 assert hashlib.sha256(git('show',commit+':'+n)).hexdigest()==pin
 assert git('ls-tree',commit,'--',n).decode().split()[0]=='100644'
entries=git('ls-files','--stage','-z').split(b'\0')
prior_entries=b''.join(r+b'\0' for r in entries if r and r.split(b'\t',1)[1].decode() not in selected)
assert hashlib.sha256(prior_entries).hexdigest()==epoch['semantic_index']['entries']
flags=git('ls-files','-v','-z');prior_flags=b''.join(r+b'\0' for r in flags.split(b'\0') if r and r[2:].decode() not in selected)
saved_flags=read(ROOT/inputs['candidate_runtime']/'INDEX-FLAGS.json')
assert hashlib.sha256(prior_flags).hexdigest()==saved_flags['.']
assert hashlib.sha256(h.git(ROOT/'artifacts/css-spec-lean',ENV,'ls-files','-v','-z')).hexdigest()==saved_flags['artifacts/css-spec-lean']
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==read(HERE/'BEFORE.json')['nested_index']
for name,key in [('CURRENT-EPOCH.json','runtime_epoch_sha256'),('ROLE.json','role_sha256'),('OWNED.json','owned_sha256')]:
 assert sha(ROOT/'artifacts/css-registered-number-native-runtime-v1'/name)==inputs[key]
state=h.index_state(ROOT,ENV);assert state['working_diff']==epoch['semantic_index']['working_diff']
current=copy.deepcopy(epoch);current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
assert set(git('diff','--name-only').decode().splitlines())==set(epoch['modified_native_paths'])==set(inputs['dirty_native_source_pins'])
assert len(epoch['modified_native_paths'])==7
for n,pin in item['source_pins'].items():current['committed_research_working_payloads'][n]=pin
current['counts']['committed_research_payloads']=len(current['committed_research_working_payloads'])
a.verify_current(h,ROOT,ENV,current)
assert not (HERE/'research-receipt.json').exists() and not (HERE/'research-signature.log').exists()
with (HERE/'research-signature.log').open('x') as f:
 subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
assert h.index_state(ROOT,ENV)==state
assert git('ls-files','-v','-z')==flags
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==read(HERE/'BEFORE.json')['nested_index']
a.verify_current(h,ROOT,ENV,current)
tree=git('rev-parse',commit+'^{tree}').decode().strip()
save(HERE/'research-retry-adoption.json',{'commit':commit,'parent':parent,'tree':tree,'staged_patch_sha256':sha(HERE/'research-staged.patch'),'selection_sha256':sha(HERE/'research-selection.json'),'first_failed_log_sha256':sha(HERE/'research-commit.log'),'prior_failed_retry_log_sha256':sha(HERE/'research-retry-1-commit.log'),'successful_retry_log':successful_log_name,'successful_retry_log_sha256':sha(successful_log),'signature_verified':True,'native_paths':7,'selected_files':207,'no_signing_or_restaging_performed':True})
save(HERE/'research-receipt.json',{'commit':commit,'parent':parent,'tree':tree,'files':item['files'],'signature_verified':True,'working_bodies_and_nested_index_preserved':True,'direct_retry_adopted':True})
save(HERE/'research-EPOCH.json',current)
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Authenticated signed retry and published preservation epoch',commit,flush=True)
