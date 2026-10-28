import hashlib
import json
import os
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
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert sha(HERE / 'commit.py') == 'ef3b5cafed2f379372c2cc6948fee914a6a90d176ae9151baee9b34d89ca8ceb'
previous = ROOT / config['previous_signing']
final = read(previous / 'FINAL-CHECK.json')
assert final['signature_chain_verified'] and final['runtime_epoch_synchronized']
assert final['head'] == config['expected_initial_head']
assert final['current_epoch_sha256'] == config['expected_initial_epoch']
assert final['accepted_fixes'] == 139 and final['tracked_fixes'] == 140
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
assert sha(runtime / 'CURRENT-EPOCH.json') == final['current_epoch_sha256']
assert (runtime / 'CURRENT-EPOCH.json').read_bytes() == (previous / 'CURRENT-EPOCH.json').read_bytes()
assert read(runtime / 'CURRENT-EPOCH.json')['semantic_index']['head'] == final['head']
assert not (runtime / 'SOURCE-TRANSITION.lock').exists()
for name in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json'):
    with (HERE / ('PRE-' + name)).open('xb') as stream:
        stream.write((runtime / name).read_bytes())
with (HERE / 'init-driver.log').open('x') as stream:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),'init'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
plan = read(previous / 'SYNC-PLAN.json')
plan.update(initial_head=final['head'], initial_epoch_sha256=sha(HERE/'INITIAL-EPOCH.json'),runtime_epoch_before=sha(HERE/'PRE-CURRENT-EPOCH.json'),role_sha256=sha(HERE/'PRE-ROLE.json'),owned_sha256=sha(HERE/'PRE-OWNED.json'),receipt_ids=config['receipt_ids'],previous_final_check_sha256=sha(previous/'FINAL-CHECK.json'))
with (HERE/'SYNC-PLAN.json').open('x') as stream:
    json.dump(plan,stream,indent=2,sort_keys=True);stream.write('\n')
print('Initialized follow-on signing only after verified v33 synchronization',final['head'])
