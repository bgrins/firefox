import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RUNTIME=ROOT/'artifacts/css-registered-number-native-runtime-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
owner=load('owner',ROOT/'artifacts/css-registered-number-source-transition-v4/transition.py')
state=load('state',RUNTIME/'state.py')
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
controls={n:(RUNTIME/n).read_bytes() for n in ('CURRENT-EPOCH.json','OWNED.json','ROLE.json')}
assert sha(controls['CURRENT-EPOCH.json'])=='749a79f52e9b00fabdc896ee60e9587acbfd1c077734f0dc371c879e573b95d6'
epoch=json.loads(controls['CURRENT-EPOCH.json'])
index=state.h.index_state(ROOT,env)
assert index['head']=='2409a410a2641c54a42feefd3c998cd58cbf028e'
assert state.h.semantic_index(index)==epoch['semantic_index']
assert index['cached_diff']==index['working_diff']==sha(b'')
updated=copy.deepcopy(epoch);updated['raw_index_observation']['current']=index['raw_index']
assert updated!=epoch
owner.quiescent(RUNTIME)
lock=RUNTIME/'SOURCE-TRANSITION.lock';lock.mkdir();identity=[lock.stat().st_dev,lock.stat().st_ino]
safe=False
try:
    before=state.a.verify_current(state.h,ROOT,env,updated)
    assert all((RUNTIME/n).read_bytes()==body for n,body in controls.items())
    for n,body in controls.items():
        with (HERE/('PRE-'+n)).open('xb') as f:f.write(body)
    (HERE/'BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
    claim=owner.claim(ROOT,str((RUNTIME/'CURRENT-EPOCH.json').relative_to(ROOT)),sha(controls['CURRENT-EPOCH.json']))
    owner.write_owned(ROOT,claim,owner.encoded(updated))
    after=state.a.verify_current(state.h,ROOT,env,updated);assert after==before
    assert all((RUNTIME/n).read_bytes()==controls[n] for n in ('OWNED.json','ROLE.json'))
    (HERE/'AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
    for n in controls:(HERE/n).write_bytes((RUNTIME/n).read_bytes())
    result={'updated_only':'raw_index_observation.current','old_epoch_sha256':sha(controls['CURRENT-EPOCH.json']),'epoch_sha256':sha((RUNTIME/'CURRENT-EPOCH.json').read_bytes()),'old_raw':epoch['raw_index_observation']['current'],'new_raw':index['raw_index'],'head':index['head'],'semantic_index_unchanged':True,'full_current_state_verified':True,'owned_and_role_unchanged':True,'native_fix_increment':0,'actual_raw_change_cause_unestablished':True}
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));safe=True
finally:
    if safe:
        assert [lock.stat().st_dev,lock.stat().st_ino]==identity;lock.rmdir()
