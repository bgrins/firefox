import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import signal

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
assert json.loads((HERE / "POLICY.json").read_bytes()).get("execution_enabled") is True, "Historical disabled preparation; use a reviewed successor"
RUNTIME=ROOT/'artifacts/css-registered-number-native-runtime-v1'
OUT=ROOT/'artifacts/css-random-counter-native-runtime-v1'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def interrupted(signum, frame): raise RuntimeError('Interrupted '+str(signum))
signal.signal(signal.SIGINT,interrupted)
signal.signal(signal.SIGTERM,interrupted)
manifest,epoch_digest=sys.argv[1:]
h=load('random_owner','artifacts/css-registered-number-source-transition-v4/transition.py')
s=h.load_state(RUNTIME)
h.authenticate(HERE,manifest)
p=read(HERE/'POLICY.json')
h.authenticate(ROOT/p['source_package'],p['source_manifest'])
for n,pin in p['references'].items():assert sha(ROOT/n)==pin
assert not any(os.environ.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'])
controls={n:(RUNTIME/n).read_bytes() for n in ['CURRENT-EPOCH.json','OWNED.json','ROLE.json']}
assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest()==epoch_digest==p['starting_epoch']
epoch=json.loads(controls['CURRENT-EPOCH.json']);owned=json.loads(controls['OWNED.json'])
assert epoch['semantic_index']['head']==p['head'] and epoch['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert epoch['page_selector_transition']['accepted'] is True
before=s.a.verify_current(s.h,ROOT,ENV,epoch)
h.quiescent(RUNTIME);h.quiescent(ROOT/'artifacts/css-page-selector-native-runtime-v1')
assert read(ROOT/'artifacts/css-random-ordinary-observation-v1/RESULT.json')['owned_sessions_closed']
claims={n:h.claim(ROOT,str((RUNTIME/n).relative_to(ROOT)),hashlib.sha256(b).hexdigest()) for n,b in controls.items()}
current=copy.deepcopy(epoch);new_owned=copy.deepcopy(owned)
for name,record in p['sources'].items():
    assert sha(ROOT/name)==record['base_sha256']
    assert hashlib.sha256(s.h.git(ROOT,ENV,'show','HEAD:'+name)).hexdigest()==record['base_sha256']
    assert s.h.git(ROOT,ENV,'ls-files','-v','--',name).decode().strip()=='H '+name
    item=h.claim(ROOT,name,record['base_sha256'],epoch['installed_identities'].get(name))
    if name in owned:assert owned[name]==item
    if name in epoch['pins']:assert epoch['pins'][name]==record['base_sha256']
    current['pins'][name]=record['base_sha256']
    current['installed_identities'][name]=item['identity'];new_owned[name]=item
assert len(p['sources'])==3
for name,record in p['tests'].items():
    assert name not in epoch['pins'] and name not in owned
    item=h.claim(ROOT,name,record['sha256'],record['identity'])
    current['pins'][name]=record['sha256'];current['installed_identities'][name]=item['identity'];new_owned[name]=item
assert len(p['tests'])==2
current['counts']['roles']=len(current['pins'])
current['counts']['installed_identities']=len(current['installed_identities'])
current['random_counter_transition']={'role':'original','compiled':False,'accepted':False,'manifest_sha256':manifest,'source_manifest_sha256':p['source_manifest']}
assert not OUT.exists();OUT.mkdir()
for n,b in controls.items():(OUT/('PRE-'+n)).write_bytes(b)
h.save(OUT/'PRE.json',before)
changed=[]
try:
    assert s.a.verify_current(s.h,ROOT,ENV,epoch)==before
    h.authenticate(HERE,manifest)
    for item in claims.values():h.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
    after=s.a.verify_current(s.h,ROOT,ENV,current);assert after==before
    for n,value in [('OWNED.json',new_owned),('CURRENT-EPOCH.json',current)]:
        changed.append(n);h.write_owned(ROOT,claims[n],h.encoded(value))
    assert (RUNTIME/'ROLE.json').read_bytes()==controls['ROLE.json']
    assert s.a.verify_current(s.h,ROOT,ENV,current)==before
    h.save(OUT/'ADOPTED-EPOCH.json',current);h.save(OUT/'POST.json',after)
    h.save(OUT/'ADOPTION-RESULT.json',{'adopted':True,'metadata_only':True,'native_sources_changed':False,'preservation_verified':True,'compiled':False,'epoch_sha256':sha(RUNTIME/'CURRENT-EPOCH.json'),'source_paths':sorted(p['sources'])})
    print('Adopted exact original random source roles',sha(RUNTIME/'CURRENT-EPOCH.json'),flush=True)
except BaseException as error:
    failures=[]
    for n in reversed(changed):
        try:h.write_owned(ROOT,claims[n],controls[n])
        except BaseException as rollback:failures.append(repr(rollback))
    try:assert s.a.verify_current(s.h,ROOT,ENV,epoch)==before
    except BaseException as rollback:failures.append(repr(rollback))
    h.save(OUT/'FAILURE.json',{'error':repr(error),'rollback_errors':failures,'manual_recovery_required':bool(failures)})
    raise
