import copy
import hashlib
import importlib.util
import os
import json
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = read(HERE / 'EXECUTION.json')
assert config['execution_enabled'] is True
plan = read(HERE / 'SYNC-PLAN.json')
parent = read(HERE / 'INITIAL-EPOCH.json')['semantic_index']['head']
files = [HERE / name for name in ('commit.py','check.py','init.py','finish.py','synchronize.py','EXECUTION.json','SYNC-PLAN.json','CHECKPOINT.md','INVENTORY.json','CHECK.json','PLAN.md','ROADMAP.md','INITIAL-EPOCH.json','BEFORE.json','PRE-CURRENT-EPOCH.json','PRE-ROLE.json','PRE-OWNED.json')]
for ident in config['receipt_ids'][:-1]:
    receipt, item = read(HERE / (ident + '-receipt.json')), read(HERE / (ident + '-item.json'))
    assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
    assert receipt['parent'] == parent and sorted(receipt['files']) == sorted(item['files'])
    assert subprocess.check_output(['git','--no-optional-locks','rev-parse',receipt['commit']+'^'],cwd=ROOT,text=True).strip() == parent
    assert subprocess.check_output(['git','--no-optional-locks','rev-parse',receipt['commit']+'^{tree}'],cwd=ROOT,text=True).strip() == receipt['tree']
    assert sorted(subprocess.check_output(['git','--no-optional-locks','diff-tree','--no-commit-id','--name-only','-r',receipt['commit']],cwd=ROOT,text=True).splitlines()) == sorted(item['files'])
    parent = receipt['commit']
    files += [HERE / (ident + suffix) for suffix in ('-selection.json','-item.json','-message.txt','-receipt.json','-commit.log','-signature.log')]
assert read(HERE / 'CURRENT-EPOCH.json')['semantic_index']['head'] == parent
assert sha(HERE/'ROADMAP-PUBLICATION.json') == config['roadmap_publication_sha256']
roadmap = read(HERE/'ROADMAP-PUBLICATION.json')
name = roadmap['target']
assert name == 'artifacts/css-continuation-roadmap-20261028-v1/PLAN.md'
old = (HERE/roadmap['preimage']).read_bytes()
planned = (HERE/roadmap['postimage']).read_bytes()
assert hashlib.sha256(old).hexdigest() == roadmap['before_sha256']
assert hashlib.sha256(planned).hexdigest() == roadmap['after_sha256']
assert planned.endswith(old) and planned != old
assert sha(HERE/'ROADMAP.md') == roadmap['detailed_roadmap_sha256']
assert name not in read(HERE/'research-item.json')['files']
assert sha(ROOT/name) == roadmap['before_sha256']
assert hashlib.sha256(subprocess.check_output(['git','--no-optional-locks','show',parent+':'+name],cwd=ROOT)).hexdigest() == roadmap['before_sha256']
with (HERE/'roadmap-research-signature.log').open('x') as log:
    subprocess.run(['git','--no-optional-locks','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',parent],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
def load(module_name,path):
    spec = importlib.util.spec_from_file_location(module_name,ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
state = load('roadmap_state','artifacts/css-registered-number-native-runtime-v1/state.py')
owner = load('roadmap_owner','artifacts/css-registered-number-source-transition-v4/transition.py')
ENV = dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
runtime = ROOT/'artifacts/css-registered-number-native-runtime-v1'
controls = {n:(HERE/('PRE-'+n)).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert all((runtime/n).read_bytes()==b for n,b in controls.items())
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
epoch = read(HERE/'CURRENT-EPOCH.json')
before = state.a.verify_current(state.h,ROOT,ENV,epoch)
assert epoch['committed_research_working_payloads'][name] == roadmap['before_sha256']
assert all(epoch[key][name]==roadmap['before_sha256'] for key in ('pins','staged_working') if name in epoch[key])
flags = {n:state.h.git(path,ENV,'ls-files','-v','-z') for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
claim = owner.claim(ROOT,name,roadmap['before_sha256'])
local_claim = owner.claim(ROOT,str((HERE/'CURRENT-EPOCH.json').relative_to(ROOT)),sha(HERE/'CURRENT-EPOCH.json'))
current = copy.deepcopy(epoch)
try:
    assert state.a.verify_current(state.h,ROOT,ENV,epoch)==before
    assert all((runtime/n).read_bytes()==b for n,b in controls.items())
    owner.write_owned(ROOT,claim,planned)
    for key in ('pins','staged_working','committed_research_working_payloads'):
        if name in current[key]:current[key][name]=roadmap['after_sha256']
    index = state.h.index_state(ROOT,ENV)
    semantic = state.h.semantic_index(index)
    assert {k:v for k,v in semantic.items() if k!='working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k!='working_diff'}
    current['semantic_index']=semantic
    current['raw_index_observation']['current']=index['raw_index']
    after = state.a.verify_current(state.h,ROOT,ENV,current)
    assert after['nested_index']==before['nested_index']
    assert all(state.h.git(path,ENV,'ls-files','-v','-z')==flags[n] for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
    assert all((runtime/n).read_bytes()==b for n,b in controls.items())
    owner.write_owned(ROOT,local_claim,owner.encoded(current))
except BaseException:
    owner.write_owned(ROOT,claim,old)
    restored=copy.deepcopy(epoch)
    index=state.h.index_state(ROOT,ENV)
    assert state.h.semantic_index(index)==epoch['semantic_index']
    restored['raw_index_observation']['current']=index['raw_index']
    snapshot=state.a.verify_current(state.h,ROOT,ENV,restored)
    expected=copy.deepcopy(before);expected['index']['raw_index']=index['raw_index']
    assert snapshot==expected
    assert all(state.h.git(path,ENV,'ls-files','-v','-z')==flags[n] for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
    assert all((runtime/n).read_bytes()==b for n,b in controls.items())
    owner.write_owned(ROOT,local_claim,owner.encoded(restored))
    raise
state.save(HERE/'ROADMAP-UPDATE.json',{'target':name,'before_sha256':roadmap['before_sha256'],'after_sha256':roadmap['after_sha256'],'prior_history_preserved':True,'canonical_runtime_controls_unchanged':True,'accepted_fix_increment':0})
files += [ROOT/name] + [HERE/n for n in ('ROADMAP-PUBLICATION.json','ROADMAP-PREIMAGE.md','ROADMAP-POSTIMAGE.md','ROADMAP-UPDATE.json','roadmap-research-signature.log')]
previous = ROOT / config['previous_signing']
assert sha(previous / 'FINAL-CHECK.json') == plan['previous_final_check_sha256']
for name,pin in config['previous_evidence'].items():
    assert sha(ROOT/name)==pin
    files.append(ROOT/name)
for name,pin in config['pre_signing_evidence'].items():
    assert sha(ROOT/name)==pin
    files.append(ROOT/name)
pins, already_committed = {}, {}
for path in files:
    assert path.is_file() and not path.is_symlink()
    name = str(path.relative_to(ROOT))
    assert name.startswith('artifacts/') and not name.startswith('artifacts/css-spec-lean/')
    pin = sha(path)
    result = subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','show',parent + ':' + name],cwd=ROOT,capture_output=True)
    if result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == pin:
        already_committed[name] = pin
    else:
        pins[name] = pin
with (HERE / 'CHECKPOINT-ARCHIVE.json').open('x') as stream:
    json.dump({'already_committed_exact':already_committed,'new_checkpoint_paths':sorted(pins),'previous_v37_final_records_preserved':True},stream,indent=2,sort_keys=True);stream.write('\n')
pins[str((HERE/'CHECKPOINT-ARCHIVE.json').relative_to(ROOT))] = sha(HERE/'CHECKPOINT-ARCHIVE.json')
item = {'id':'checkpoint','files':sorted(pins),'source_pins':pins,'message':'No bug - Checkpoint linear easing crash research and next validation steps. r?#firefox-style-system-reviewers'}
selection = HERE / 'checkpoint-selection.json'
with selection.open('x') as stream:
    json.dump(item,stream,indent=2,sort_keys=True);stream.write('\n')
for command, log in [([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(selection)],'checkpoint-driver.log'),([sys.executable,'-I','-S','-B',str(HERE/'synchronize.py')],'synchronize-driver.log')]:
    with (HERE/log).open('x') as stream:
        subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
print('Follow-on research checkpoint signed and runtime epoch synchronized')
