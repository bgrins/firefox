import hashlib
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
source=(Path(__file__).resolve().parent/'commit.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=="ef3b5cafed2f379372c2cc6948fee914a6a90d176ae9151baee9b34d89ca8ceb"
exec(compile(source.split("if sys.argv[1]=='init':",1)[0],'reviewed-commit-helper-prefix','exec'))
read=lambda p:json.loads(p.read_text())
assert len(sys.argv)==3, 'Supply exact successful commit and its commit-log basename'
commit, successful_log_name=sys.argv[1:]
assert Path(successful_log_name).name==successful_log_name
assert successful_log_name.startswith('random-') and successful_log_name.endswith('.log')
successful_log=HERE/successful_log_name
assert not successful_log.is_symlink() and stat.S_ISREG(successful_log.lstat().st_mode)
item=read(HERE/'random-selection.json');epoch=read(HERE/'CURRENT-EPOCH.json')
parent='b04304be4b2083686920e8b3788e8e7614d26496'
selected=set(item['files'])
assert item['id']=='random' and len(selected)==165 and selected==set(item['source_pins'])
assert all(n.startswith('artifacts/') and not n.startswith('artifacts/css-spec-lean/') for n in selected)
assert read(HERE/'random-item.json')==item|{'expected_head':parent,'execution_enabled':True}
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
assert git('rev-parse','HEAD').decode().strip()==commit
assert git('rev-list','--parents','-n','1',commit).decode().split()==[commit,parent]
assert parent==epoch['semantic_index']['head']
assert not git('diff','--cached','--name-only')
assert git('diff','--binary','--full-index',parent,commit)==(HERE/'random-staged.patch').read_bytes()
assert set(git('diff','--name-only',parent,commit).decode().splitlines())==selected
assert git('show','-s','--format=%B',commit).decode().rstrip()==item['message'].rstrip()
for name,pin in item['source_pins'].items():
 assert sha(ROOT/name)==pin
 assert hashlib.sha256(git('show',commit+':'+name)).hexdigest()==pin
 assert git('ls-tree',commit,'--',name).decode().split()[0]=='100644'
entries=git('ls-files','--stage','-z').split(b'\0')
prior_entries=b''.join(r+b'\0' for r in entries if r and r.split(b'\t',1)[1].decode() not in selected)
assert hashlib.sha256(prior_entries).hexdigest()==epoch['semantic_index']['entries']
before=read(HERE/'BEFORE.json')
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
runtime=ROOT/'artifacts/css-registered-number-native-runtime-v1'
controls={name:(HERE/('PRE-'+name)).read_bytes() for name in ['CURRENT-EPOCH.json','ROLE.json','OWNED.json']}
assert all((runtime/name).read_bytes()==body for name,body in controls.items())
assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest()=='10893d33655602ae74a20df6302987051711f84281ff6ff154797809be7db3f4'
state=h.index_state(ROOT,ENV)
assert state['working_diff']==epoch['semantic_index']['working_diff']
assert epoch['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert git('diff','--name-only').decode().splitlines()==epoch['modified_native_paths']
current=copy.deepcopy(epoch);current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
current['committed_research_working_payloads'].update(item['source_pins'])
current['counts']['committed_research_payloads']=len(current['committed_research_working_payloads'])
a.verify_current(h,ROOT,ENV,current)
assert not (HERE/'random-receipt.json').exists() and not (HERE/'random-signature.log').exists()
with (HERE/'random-signature.log').open('x') as f:
 subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
assert h.semantic_index(h.index_state(ROOT,ENV))==h.semantic_index(state)
assert h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
assert all((runtime/name).read_bytes()==body for name,body in controls.items())
a.verify_current(h,ROOT,ENV,current)
tree=git('rev-parse',commit+'^{tree}').decode().strip()
save(HERE/'random-retry-adoption.json',{'commit':commit,'parent':parent,'tree':tree,'staged_patch_sha256':sha(HERE/'random-staged.patch'),'selection_sha256':sha(HERE/'random-selection.json'),'successful_retry_log':successful_log_name,'successful_retry_log_sha256':sha(successful_log),'signature_verified':True,'no_signing_or_restaging_performed':True})
save(HERE/'random-receipt.json',{'commit':commit,'parent':parent,'tree':tree,'files':item['files'],'signature_verified':True,'working_bodies_and_nested_index_preserved':True,'direct_retry_adopted':True})
save(HERE/'random-EPOCH.json',current)
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Authenticated signed retry and published signing preservation epoch',commit,flush=True)
