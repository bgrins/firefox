import copy, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUNTIME=ROOT/'artifacts/css-registered-number-native-runtime-v1'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
read=lambda p:json.loads(p.read_bytes())
digest=lambda b:hashlib.sha256(b).hexdigest()
state=load('sync_state','artifacts/css-registered-number-native-runtime-v1/state.py')
ownership=load('sync_ownership','artifacts/css-registered-number-source-transition-v4/transition.py')
assert not any(os.environ.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'])
initial_bytes=(HERE/'INITIAL-EPOCH.json').read_bytes()
assert digest(initial_bytes)=='f9576f394e34255b01dadf3f272347f4c3266362a01081c0dbda3085e521afcd'
initial=json.loads(initial_bytes)
epoch_bytes=(HERE/'CURRENT-EPOCH.json').read_bytes();epoch=json.loads(epoch_bytes)
before=state.a.verify_current(state.h,ROOT,ENV,epoch)
assert initial['modified_native_paths']==epoch['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert epoch['registered_number_transition']==initial['registered_number_transition']=={'role':'candidate','variant':'registered-provider-default-v5','compiled':False,'accepted':False,'last_phase':'provider-default-partial-v5-install-1'}
assert epoch['pins']['servo/components/style/custom_properties.rs']=='2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774'
assert epoch['pins']['servo/components/style/properties/cascade.rs']=='2cc7b3d4047b9759277f41809ad7ba7baef99431c26b608bcf459b2d83764656'
assert epoch['staged_working']=={} and len(initial['staged_working'])==36
expected=copy.deepcopy(initial);expected['staged_working']={}
expected['semantic_index']=epoch['semantic_index'];expected['raw_index_observation']['current']=epoch['raw_index_observation']['current']
parent=initial['semantic_index']['head']
identifiers=read(HERE/'SYNC-PLAN.json')['receipt_ids']
assert identifiers[:4]==['cycle-model','initial-independence','provider-observations','provider-repair'] and identifiers[-1]=='checkpoint'
for ident in identifiers:
 receipt=read(HERE/(ident+'-receipt.json'));item=read(HERE/(ident+'-item.json'))
 assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
 assert receipt['parent']==parent and sorted(receipt['files'])==sorted(item['files'])
 assert all(n.startswith('artifacts/') and n!='artifacts/css-spec-lean' and not n.startswith('artifacts/css-spec-lean/') for n in receipt['files'])
 assert state.h.git(ROOT,ENV,'rev-parse',receipt['commit']+'^').decode().strip()==parent
 assert state.h.git(ROOT,ENV,'rev-parse',receipt['commit']+'^{tree}').decode().strip()==receipt['tree']
 assert sorted(state.h.git(ROOT,ENV,'diff-tree','--no-commit-id','--name-only','-r',receipt['commit']).decode().splitlines())==sorted(receipt['files'])
 with (HERE/(ident+'-resync-signature.log')).open('x') as stream:
  subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',receipt['commit']],cwd=ROOT,env=ENV,stdout=stream,stderr=subprocess.STDOUT,check=True)
 expected['committed_research_working_payloads'].update(item['source_pins'])
 parent=receipt['commit']
assert parent==epoch['semantic_index']['head']
expected['counts']['committed_research_payloads']=len(expected['committed_research_working_payloads'])
assert expected==epoch
assert epoch['semantic_index']['working_diff']==initial['semantic_index']['working_diff']
controls={n:(RUNTIME/n).read_bytes() for n in ['CURRENT-EPOCH.json','ROLE.json','OWNED.json']}
assert controls['CURRENT-EPOCH.json']==initial_bytes
assert all(controls[n]==(HERE/('PRE-'+n)).read_bytes() for n in controls)
claims={n:ownership.claim(ROOT,str((RUNTIME/n).relative_to(ROOT)),digest(b)) for n,b in controls.items()}
ownership.quiescent(RUNTIME)
assert not (RUNTIME/'SOURCE-TRANSITION.lock').exists()
try:
 assert state.a.verify_current(state.h,ROOT,ENV,epoch)==before
 for item in claims.values():ownership.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
 ownership.write_owned(ROOT,claims['CURRENT-EPOCH.json'],epoch_bytes)
 assert state.a.verify_current(state.h,ROOT,ENV,epoch)==before
 assert all((RUNTIME/n).read_bytes()==controls[n] for n in ['ROLE.json','OWNED.json'])
except BaseException:
 ownership.write_owned(ROOT,claims['CURRENT-EPOCH.json'],initial_bytes)
 raise
with (HERE/'FINAL-CHECK.json').open('x') as stream:
 json.dump({'head':parent,'signature_chain_verified':True,'runtime_epoch_synchronized':True,'native_dirty_paths':1,'provider_candidate_version':'v5 partial ordinary restoration','provider_candidate_compiled':False,'provider_candidate_accepted':False,'historical_v4_compiled_and_observed':True,'accepted_fixes':138,'tracked_fixes':139,'held_excluded':120,'current_epoch_sha256':digest(epoch_bytes)},stream,indent=2);stream.write('\n')
print('Verified signed research checkpoint; partial v5 remains uncompiled',parent)
