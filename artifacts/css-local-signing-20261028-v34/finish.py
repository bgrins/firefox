import hashlib
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
files = [HERE / name for name in ('commit.py','init.py','finish.py','synchronize.py','EXECUTION.json','SYNC-PLAN.json','CHECKPOINT.md','INVENTORY.json','CHECK.json','PLAN.md','INITIAL-EPOCH.json','BEFORE.json','PRE-CURRENT-EPOCH.json','PRE-ROLE.json','PRE-OWNED.json')]
for ident in config['receipt_ids'][:-1]:
    receipt, item = read(HERE / (ident + '-receipt.json')), read(HERE / (ident + '-item.json'))
    assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
    assert receipt['parent'] == parent and sorted(receipt['files']) == sorted(item['files'])
    parent = receipt['commit']
    files += [HERE / (ident + suffix) for suffix in ('-selection.json','-item.json','-message.txt','-receipt.json','-commit.log','-signature.log')]
assert read(HERE / 'CURRENT-EPOCH.json')['semantic_index']['head'] == parent
previous = ROOT / config['previous_signing']
assert sha(previous / 'FINAL-CHECK.json') == plan['previous_final_check_sha256']
files += [previous / name for name in ('adopt-random-retry.py','PENDING-SIGNING.json','random-failed-commit.log','random-failed-driver.log','random-failed-retry-commit.log','random-retry-adoption.json','random-user-present-retry-commit.log','FINAL-CHECK.json','checkpoint-receipt.json','checkpoint-commit.log','checkpoint-signature.log','random-resync-signature.log','line-height-resync-signature.log','checkpoint-resync-signature.log')]
adoption = read(previous / 'random-retry-adoption.json')
assert sha(previous / adoption['successful_retry_log']) == adoption['successful_retry_log_sha256']
files.append(previous / adoption['successful_retry_log'])
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
    json.dump({'already_committed_exact':already_committed,'new_checkpoint_paths':sorted(pins),'previous_failed_signing_records_preserved':True},stream,indent=2,sort_keys=True);stream.write('\n')
pins[str((HERE/'CHECKPOINT-ARCHIVE.json').relative_to(ROOT))] = sha(HERE/'CHECKPOINT-ARCHIVE.json')
item = {'id':'checkpoint','files':sorted(pins),'source_pins':pins,'message':'No bug - Checkpoint restored experiments and pending random repairs. r?#firefox-style-system-reviewers'}
selection = HERE / 'checkpoint-selection.json'
with selection.open('x') as stream:
    json.dump(item,stream,indent=2,sort_keys=True);stream.write('\n')
for command, log in [([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(selection)],'checkpoint-driver.log'),([sys.executable,'-I','-S','-B',str(HERE/'synchronize.py')],'synchronize-driver.log')]:
    with (HERE/log).open('x') as stream:
        subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
print('Follow-on research checkpoint signed and runtime epoch synchronized')
