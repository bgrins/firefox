import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
CONTROL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
PAIR = ROOT / 'artifacts/css-nowrap-native-pair-runtime-1'
OUT = ROOT / 'artifacts/css-nowrap-raw-index-refresh-v1'
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
state = load('refresh_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
owner = load('refresh_owner', 'artifacts/css-registered-number-source-transition-v4/transition.py')
prior = load('refresh_derive', 'artifacts/css-prioritary-published-raw-index-refresh-v1/run.py')
assert sha((PAIR/'FILES.json').read_bytes()) == 'f4bb8776b2d4c9b3746210143073f8c44456fec6e15140941b44f1eb5aaf9f7c'
owner.authenticate(PAIR, sha((PAIR/'FILES.json').read_bytes()))
terminal = read(PAIR/'ROOT-LIVE-AUDIT-TERMINAL.json')
assert terminal['exit'] == 0 and terminal['audit_sha256'] == sha((PAIR/'ROOT-LIVE-RESTORATION.json').read_bytes())
audit = read(PAIR/'ROOT-LIVE-RESTORATION.json')
assert audit['independent_live_restoration_verified'] and audit['backup_removed']
assert audit['source_and_binary_hashes_restored'] and audit['controls_unchanged']
controls = {n:(CONTROL/n).read_bytes() for n in ('CURRENT-EPOCH.json','OWNED.json','ROLE.json')}
assert sha(controls['CURRENT-EPOCH.json']) == '9273945a2580eef52fb5ee38a4d0fd655e6e9377ad2dc6e5e2d1d9995bcd19b2'
old = json.loads(controls['CURRENT-EPOCH.json'])
updated = prior.derive(old, read(PAIR/'PAIR-PRE.json')['snapshot'], read(PAIR/'POST.json'), read(PAIR/'RAW-INDEX-OBSERVATION.json'))
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert state.a.verify_current(state.h, ROOT, env, updated) == audit['snapshot']
receipt_path = ROOT/'artifacts/css-research-checkpoint-20261030-v96/result.json'
receipt = read(receipt_path)
assert receipt['committed'] and receipt['signature_verified'] and receipt['epoch_sha256'] == sha(controls['CURRENT-EPOCH.json'])
assert receipt['head'] == updated['semantic_index']['head'] == '10e043823f5fb60317be96ada71e8fd39794e100'
state.h.git(ROOT, env, '-c', 'gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', receipt['head'])
owner.quiescent(CONTROL)
owner.quiescent(ROOT/'artifacts/css-page-selector-native-runtime-v1')
for group in audit['independently_absent_process_groups']: owner.group_absent(group)
lock=CONTROL/'SOURCE-TRANSITION.lock'
assert not lock.exists() and not OUT.exists()
OUT.mkdir()
(OUT/'PRE-CURRENT-EPOCH.json').write_bytes(controls['CURRENT-EPOCH.json'])
claim=owner.claim(ROOT,str((CONTROL/'CURRENT-EPOCH.json').relative_to(ROOT)),sha(controls['CURRENT-EPOCH.json']))
lock.mkdir()
identity=(lock.stat().st_dev,lock.stat().st_ino)
body=owner.encoded(updated)
safe=False
try:
    assert all((CONTROL/n).read_bytes()==b for n,b in controls.items())
    owner.write_owned(ROOT,claim,body)
    assert state.a.verify_current(state.h,ROOT,env,updated)==audit['snapshot']
    assert all((CONTROL/n).read_bytes()==controls[n] for n in ('OWNED.json','ROLE.json'))
    result=copy.deepcopy(receipt)
    result.update(epoch_sha256=sha(body), updated_only='raw_index_observation.current', semantic_index_unchanged=True, prior_signed_receipt=str(receipt_path.relative_to(ROOT)), prior_signed_receipt_sha256=sha(receipt_path.read_bytes()), prior_epoch_sha256=sha(controls['CURRENT-EPOCH.json']), raw_before=old['raw_index_observation']['current'], raw_after=updated['raw_index_observation']['current'], full_current_state_verified=True, no_new_commit=True)
    (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    safe=True
except BaseException:
    owner.write_owned(ROOT,claim,controls['CURRENT-EPOCH.json'])
    assert state.a.verify_current(state.h,ROOT,env,updated)==audit['snapshot']
    safe=True
    raise
finally:
    if safe:
        assert (lock.stat().st_dev,lock.stat().st_ino)==identity
        lock.rmdir()
print(json.dumps(result))
