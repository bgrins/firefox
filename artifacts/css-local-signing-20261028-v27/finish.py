import hashlib, json, subprocess, sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_bytes())
first=read(HERE/'cycle-model-receipt.json')
assert first['signature_verified'] and first['working_bodies_and_nested_index_preserved']
ids=read(HERE/'SYNC-PLAN.json')['receipt_ids']
for name in ids[1:-1]:
 receipt=HERE/(name+'-receipt.json')
 if receipt.exists():
  done=read(receipt);assert done['signature_verified'] and done['working_bodies_and_nested_index_preserved']
  continue
 with (HERE/(name+'-driver.log')).open('x') as stream:
  subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(HERE/(name+'-selection.json'))],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
 print('Completed',name,flush=True)
files=[HERE/n for n in ['commit.py','resume-first.py','finish.py','synchronize.py','SYNC-PLAN.json','CHECKPOINT.md','DRAFTS.json','RESEARCH-INVENTORY.json','INITIAL-EPOCH.json','BEFORE.json','PRE-CURRENT-EPOCH.json','PRE-ROLE.json','PRE-OWNED.json']]
for name in ids[:-1]:
 for suffix in ['-selection.json','-item.json','-message.txt','-receipt.json','-commit.log','-signature.log','-staged.patch','-EPOCH.json']:
  files.append(HERE/(name+suffix))
for group in read(HERE/'DRAFTS.json').values():
 for n,r in group['files'].items():
  q=ROOT/n;assert hashlib.sha256(q.read_bytes()).hexdigest()==r['sha256'];files.append(q)
previous=ROOT/'artifacts/css-local-signing-20261028-v26'
for name in ['commit.py','resume-first.py','finish.py','synchronize.py','CHECKPOINT.md','DRAFTS.json','INITIAL-EPOCH.json','BEFORE.json','SIGNING-STATUS.json','cycle-model-commit.log.attempt-1','cycle-model-commit.log.attempt-2','cycle-model-driver.log.attempt-1','cycle-model-retry-driver.log.attempt-2','cycle-model-selection.json','cycle-model-item.json','cycle-model-message.txt','cycle-model-staged.patch','initial-independence-selection.json','provider-observations-selection.json','provider-repair-selection.json']:
 files.append(previous/name)
pins={}
for f in files:
 assert f.is_file() and not f.is_symlink(),str(f)
 pins[str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
item={'id':'checkpoint','files':sorted(pins),'source_pins':pins,'message':'No bug - Preserve staged provider research and partial-v5 checkpoint. r?#firefox-style-system-reviewers'}
selection=HERE/'checkpoint-selection.json'
with selection.open('x') as stream:json.dump(item,stream,indent=2,sort_keys=True);stream.write('\n')
with (HERE/'checkpoint-driver.log').open('x') as stream:
 subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(selection)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
print('Completed checkpoint; synchronizing runtime epoch',flush=True)
with (HERE/'synchronize-driver.log').open('x') as stream:
 subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'synchronize.py')],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
print('All research commits and runtime synchronization complete',flush=True)
