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
for name,pin in config['previous_evidence'].items():
    assert sha(ROOT/name) == pin
previous = ROOT / config['previous_signing']
final = read(previous / 'FINAL-CHECK.json')
assert final['signature_chain_verified'] and final['runtime_epoch_synchronized']
assert final['head'] == config['expected_initial_head']
assert final['current_epoch_sha256'] == config['previous_evidence'][str((previous/'CURRENT-EPOCH.json').relative_to(ROOT))]
assert final['accepted_fixes'] == 141 and final['tracked_fixes'] == 142
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
assert sha(runtime / 'CURRENT-EPOCH.json') == config['expected_initial_epoch']
assert sha(ROOT / config['initial_epoch_binding']) == config['expected_initial_epoch']
assert (runtime / 'CURRENT-EPOCH.json').read_bytes() == (ROOT / config['initial_epoch_binding']).read_bytes()
original = read(previous / 'CURRENT-EPOCH.json')
updated = read(runtime / 'CURRENT-EPOCH.json')
original['raw_index_observation']['current'] = updated['raw_index_observation']['current']
assert original == updated
for name,pin in config['pre_signing_evidence'].items():
    assert sha(ROOT/name) == pin
result = read(ROOT / config['typecheck_runtime'] / 'RESULT.json')
assert result['success'] and result['source_restored'] and result['preservation_verified']
assert result['runtime_controls_unchanged'] and result['owned_processes'] == {}
assert result['error'] is None and result['publication_errors'] == []
refresh = read(ROOT / config['raw_refresh_runtime'] / 'RESULT.json')
assert refresh['updated'] and refresh['preservation_verified']
assert refresh['only_changed_field'] == 'raw_index_observation.current'
assert refresh['epoch_sha256'] == config['expected_initial_epoch']
assert read(runtime / 'CURRENT-EPOCH.json')['semantic_index']['head'] == final['head']
assert not (runtime / 'SOURCE-TRANSITION.lock').exists()
retired = ROOT / 'testing/web-platform/tests/css/css-properties-values-api/registered-random-alternative-indices.tentative.html'
assert not retired.exists() and not retired.is_symlink()
for name in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json'):
    with (HERE / ('PRE-' + name)).open('xb') as stream:
        stream.write((runtime / name).read_bytes())
with (HERE / 'init-driver.log').open('x') as stream:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),'init'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
plan = {'accepted_payload':{n:{'sha256':pin,'identity':updated['installed_identities'][n]} for n,pin in (updated['accepted_line_height']['files'] | updated['accepted_random_counter']['files']).items()}}
plan.update(initial_head=final['head'], initial_epoch_sha256=sha(HERE/'INITIAL-EPOCH.json'),runtime_epoch_before=sha(HERE/'PRE-CURRENT-EPOCH.json'),role_sha256=sha(HERE/'PRE-ROLE.json'),owned_sha256=sha(HERE/'PRE-OWNED.json'),receipt_ids=config['receipt_ids'],previous_final_check_sha256=sha(previous/'FINAL-CHECK.json'))
with (HERE/'SYNC-PLAN.json').open('x') as stream:
    json.dump(plan,stream,indent=2,sort_keys=True);stream.write('\n')
print('Initialized follow-on signing only after verified v37 synchronization and explicit raw reconciliation',final['head'])
