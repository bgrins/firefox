import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
FAILED = ROOT / 'artifacts/css-selective-cancellation-publication-selective-cancellation-runtime-1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
def git(*args):
    return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=ROOT,env=env)
assert git('rev-parse','HEAD').decode().strip() == 'cb5bb52e3a1645f8eaf5db40cf727c4da36cac8b'
assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
failure = read(FAILED/'INSTALL-FAILURE.json')
assert failure['rollback_verified'] and not failure['manual_recovery_required']
assert not (FAILED/'INSTALL-RESULT.json').exists()
claims = read(FAILED/'INITIAL-CLAIMS.json')
for path,claim in claims['sources'].items():
    file=ROOT/path; st=file.stat()
    assert sha(file)==claim['owned_sha256'] and [st.st_dev,st.st_ino]==claim['identity']
for path in claims['parents']:
    assert not os.path.lexists(ROOT/path)
controls={n:(RUNTIME/n).read_bytes() for n in ('CURRENT-EPOCH.json','OWNED.json','ROLE.json')}
epoch=json.loads(controls['CURRENT-EPOCH.json'])
old=read(FAILED/'PRE-CURRENT-EPOCH.json')
expected_epoch=copy.deepcopy(old)
expected_epoch['raw_index_observation']['current']=epoch['raw_index_observation']['current']
assert epoch==expected_epoch
for name in ('OWNED.json','ROLE.json'):
    assert controls[name]==(FAILED/('PRE-'+name)).read_bytes()
assert not (RUNTIME/'SOURCE-TRANSITION.lock').exists()
spec=importlib.util.spec_from_file_location('state',RUNTIME/'state.py')
state=importlib.util.module_from_spec(spec);spec.loader.exec_module(state)
audit=state.a.verify_current(state.h,ROOT,env,epoch)
expected=read(FAILED/'PRE.json')
expected['index']['raw_index']=epoch['raw_index_observation']['current']
assert audit==expected
assert all((RUNTIME/n).read_bytes()==body for n,body in controls.items())
assert not (RUNTIME/'SOURCE-TRANSITION.lock').exists()
for n,body in controls.items():
    with (HERE/n).open('xb') as f:f.write(body)
report={'head':git('rev-parse','HEAD').decode().strip(),'full_current_state_verified':True,'rollback_verified':True,'tracked_diff_empty':True,'staged_diff_empty':True,'new_tests_absent':True,'source_hashes_and_identities_restored':True,'source_transition_lock_absent':True,'epoch_sha256':sha(RUNTIME/'CURRENT-EPOCH.json'),'old_epoch_sha256':sha(FAILED/'PRE-CURRENT-EPOCH.json'),'only_possible_epoch_change':'raw_index_observation.current','controls':{n:sha(RUNTIME/n) for n in controls},'failure_sha256':sha(FAILED/'INSTALL-FAILURE.json'),'snapshot':audit}
with (HERE/'REPORT.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k!='snapshot'}))
