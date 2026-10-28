import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT/'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
read = lambda p:json.loads(p.read_bytes())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs = read(HERE/'INPUTS.json')
assert inputs['execution_enabled'] is True and inputs['final_validation_ready'] is True and inputs['publication_enabled'] is True
assert ROOT/inputs['signing_directory'] == HERE
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
for n,pin in inputs['references'].items(): assert sha(ROOT/n) == pin
assert sha(HERE/'commit.py') == inputs['commit_helper_sha256']
for name,pin in inputs['prior_checkpoint_evidence'].items(): assert sha(ROOT/name)==pin


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


s=load('line_height_sign_state','artifacts/css-registered-number-native-runtime-v1/state.py')
o=load('line_height_sign_owner','artifacts/css-registered-number-source-transition-v4/transition.py')
save=s.save
epoch=read(HERE/'CURRENT-EPOCH.json')
before=s.a.verify_current(s.h,ROOT,ENV,epoch)
assert epoch['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert epoch['line_height_transition']['compiled'] and not epoch['line_height_transition']['accepted']
controls={n:(RUNTIME/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert all(b==(HERE/('PRE-'+n)).read_bytes() for n,b in controls.items())
assert sha(RUNTIME/'CURRENT-EPOCH.json')==inputs['initial_epoch']
initial=read(HERE/'INITIAL-EPOCH.json')
parent=initial['semantic_index']['head']
assert parent==inputs['initial_head']
receipts={}
assert inputs['group_order']==['research','validation','native-fix']
for name in inputs['group_order']:
    r=read(HERE/(name+'-receipt.json'))
    assert r['parent']==parent and r['signature_verified'] and r['working_bodies_and_nested_index_preserved']
    assert s.h.git(ROOT,ENV,'rev-parse',r['commit']+'^').decode().strip()==parent
    assert s.h.git(ROOT,ENV,'rev-parse',r['commit']+'^{tree}').decode().strip()==r['tree']
    assert sorted(s.h.git(ROOT,ENV,'diff-tree','--no-commit-id','--name-only','-r',r['commit']).decode().splitlines())==sorted(r['files'])
    if name!='native-fix': assert all(n.startswith('artifacts/') for n in r['files'])
    subprocess.run(['git','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',r['commit']],cwd=ROOT,env=ENV,check=True)
    parent=r['commit'];receipts[name]=r
assert parent==epoch['semantic_index']['head']
validation=read(HERE/'validation-item.json')['source_pins']
assert validation[inputs['acceptance_path']]==inputs['acceptance_sha256']
assert all(initial['pins'].get(n)==pin for n,pin in read(HERE/'native-selection.json')['source_pins'].items())
flags={n:s.h.git(ROOT/n,ENV,'ls-files','-v','-z') for n in ('.','artifacts/css-spec-lean')}
claims={n:o.claim(ROOT,str((RUNTIME/n).relative_to(ROOT)),hashlib.sha256(b).hexdigest()) for n,b in controls.items()}
assert not (RUNTIME/'SOURCE-TRANSITION.lock').exists()
with (HERE/'render-driver.log').open('x') as log:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'render_checkpoint.py')],cwd=ROOT,env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True)
prepared=HERE/'prepared-checkpoint'
plan=read(prepared/'PLAN.json')
assert plan['native_commit']==parent and plan['canonical_writes_performed'] is False
old={n:(ROOT/n).read_bytes() for n in plan['before']}
planned={n:(prepared/'postimages'/n).read_bytes() for n in plan['after']}
assert set(old)==set(planned)
for n,b in old.items():
    assert hashlib.sha256(b).hexdigest()==plan['before'][n]
    pins=[epoch[k][n] for k in ('pins','committed_research_working_payloads') if n in epoch[k]]
    assert pins and all(pin==plan['before'][n] for pin in pins)
for n,b in planned.items():assert hashlib.sha256(b).hexdigest()==plan['after'][n]
ledger_claims={n:o.claim(ROOT,n,hashlib.sha256(b).hexdigest()) for n,b in old.items()}
local_claim=o.claim(ROOT,str((HERE/'CURRENT-EPOCH.json').relative_to(ROOT)),sha(HERE/'CURRENT-EPOCH.json'))
changed=[]
current=copy.deepcopy(epoch)
try:
    assert s.a.verify_current(s.h,ROOT,ENV,epoch)==before
    assert all((RUNTIME/n).read_bytes()==b for n,b in controls.items())
    for n,b in planned.items():
        changed.append(n);o.write_owned(ROOT,ledger_claims[n],b)
        for key in ('pins','staged_working','committed_research_working_payloads'):
            if n in current[key]:current[key][n]=sha(ROOT/n)
    index=s.h.index_state(ROOT,ENV)
    semantic=s.h.semantic_index(index)
    assert {k:v for k,v in semantic.items() if k!='working_diff'}=={k:v for k,v in epoch['semantic_index'].items() if k!='working_diff'}
    current['semantic_index']=semantic
    current['raw_index_observation']['current']=index['raw_index']
    current['line_height_transition']['accepted']=True
    current['accepted_line_height']={'fix':inputs['fix'],'native_commit':parent,'files':read(HERE/'native-selection.json')['source_pins'],'old_restoration_recipes_require_rebase':True}
    after=s.a.verify_current(s.h,ROOT,ENV,current)
    assert after['nested_index']==before['nested_index']
    assert all(s.h.git(ROOT/n,ENV,'ls-files','-v','-z')==body for n,body in flags.items())
    o.write_owned(ROOT,local_claim,o.encoded(current))
except BaseException:
    for n in reversed(changed):o.write_owned(ROOT,ledger_claims[n],old[n])
    restored=copy.deepcopy(epoch);index=s.h.index_state(ROOT,ENV)
    assert s.h.semantic_index(index)==epoch['semantic_index']
    restored['raw_index_observation']['current']=index['raw_index']
    snapshot=s.a.verify_current(s.h,ROOT,ENV,restored)
    expected=copy.deepcopy(before);expected['index']['raw_index']=index['raw_index'];assert snapshot==expected
    assert all(s.h.git(ROOT/n,ENV,'ls-files','-v','-z')==body for n,body in flags.items())
    o.write_owned(ROOT,local_claim,o.encoded(restored))
    raise
save(HERE/'ROADMAP-UPDATE.json',plan)
(HERE/'CHECKPOINT.md').write_text(read(ROOT/inputs['acceptance_path'])['approved_checkpoint_summary']+'\n\nHeld provider experiment remains unchanged and unaccepted. Earlier binary/restoration receipts are historical; preserve the accepted line-height overlay in future restoration.\n')
files=set(planned)
files.update(inputs['prior_checkpoint_evidence'])
for n in ('commit.py','init.py','finish.py','render_checkpoint.py','INPUTS.json','native-selection.json','INITIAL-EPOCH.json','BEFORE.json','PRE-CURRENT-EPOCH.json','PRE-ROLE.json','PRE-OWNED.json','ROADMAP-UPDATE.json','CHECKPOINT.md','README.md','CHECK.json','PAYLOAD.json'):
    files.add(str((HERE/n).relative_to(ROOT)))
for ident in receipts:
    for suffix in ('-selection.json','-item.json','-receipt.json','-signature.log','-message.txt','-commit.log','-EPOCH.json'):
        filename='native-selection.json' if ident=='native-fix' and suffix=='-selection.json' else ident+suffix
        files.add(str((HERE/filename).relative_to(ROOT)))
files.update(str(p.relative_to(ROOT)) for p in prepared.rglob('*') if p.is_file())
pins={};archived={}
for n in sorted(files):
    body=(ROOT/n).read_bytes()
    existing=subprocess.run(['git','show',parent+':'+n],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    (archived if existing.returncode==0 and existing.stdout==body else pins)[n]=hashlib.sha256(body).hexdigest()
save(HERE/'CHECKPOINT-ARCHIVE.json',{'already_committed_identical':archived,'parent':parent})
pins[str((HERE/'CHECKPOINT-ARCHIVE.json').relative_to(ROOT))]=sha(HERE/'CHECKPOINT-ARCHIVE.json')
save(HERE/'checkpoint-selection.json',{'id':'checkpoint','files':sorted(pins),'source_pins':pins,'message':'No bug - Record validated line-height fix and CSS continuation checkpoint. r?#firefox-style-system-reviewers'})
with (HERE/'checkpoint-driver.log').open('x') as log:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(HERE/'checkpoint-selection.json')],cwd=ROOT,env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True)
final=read(HERE/'CURRENT-EPOCH.json');final_snapshot=s.a.verify_current(s.h,ROOT,ENV,final)
r=read(HERE/'checkpoint-receipt.json')
assert r['parent']==parent and r['commit']==final['semantic_index']['head'] and r['signature_verified'] and r['working_bodies_and_nested_index_preserved']
assert final['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert final_snapshot['nested_index']==before['nested_index']
assert all((RUNTIME/n).read_bytes()==b for n,b in controls.items())
for item in claims.values():o.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
try:
    o.write_owned(ROOT,claims['CURRENT-EPOCH.json'],(HERE/'CURRENT-EPOCH.json').read_bytes())
    assert s.a.verify_current(s.h,ROOT,ENV,read(RUNTIME/'CURRENT-EPOCH.json'))==final_snapshot
    assert all((RUNTIME/n).read_bytes()==controls[n] for n in ('ROLE.json','OWNED.json'))
except BaseException as error:
    failures=[]
    try:o.write_owned(ROOT,claims['CURRENT-EPOCH.json'],controls['CURRENT-EPOCH.json'])
    except BaseException as rollback:failures.append(repr(rollback))
    save(HERE/'SYNCHRONIZATION-FAILURE.json',{'error':repr(error),'rollback_errors':failures,'manual_recovery_required':True,'signed_head':final['semantic_index']['head'],'note':'Signed commits remain; restored prior runtime epoch does not certify new HEAD.'})
    raise
save(HERE/'FINAL-CHECK.json',{'head':final['semantic_index']['head'],'native_commit':parent,'accepted_fix':inputs['fix'],'accepted_fixes':140,'tracked':inputs['fix'],'tracked_fixes':inputs['fix'],'signature_chain_verified':True,'held_excluded':120,'native_dirty_paths':1,'provider_candidate_accepted':False,'runtime_epoch_synchronized':True,'current_epoch_sha256':sha(RUNTIME/'CURRENT-EPOCH.json')})
print('Signed standalone line-height checkpoint; provider experiment remains held')
