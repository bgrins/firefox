import hashlib, json, os, shutil, subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
inventory = root / 'artifacts/css-completed-target-inventory-v3'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
assert sha(inventory / 'FREEZE.json') == '16494d2232f087c7402d351056395538686dff6f800759cc5a1fb39f1a97015a'
manifest = read(inventory / 'MANIFEST.json')
assert sha(inventory / 'MANIFEST.json') == '359df679e7b4511dd77876d0fc6b472bbaa466d31b91d5ebfaed1fcc9a17852c'
for name, pin in manifest.items(): assert sha(inventory / name) == pin
proposal = read(inventory / 'PROPOSED.json'); assert len(proposal) == 1
proposal = proposal[0]; target = Path(proposal['path'])
assert target == root / 'artifacts/css-parser-public-history-admission-development-v1/relocated/output'
assert target.resolve() == target and target.is_dir()
rows = read(inventory / 'OUTPUT-INVENTORY.json')
assert {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()} == {r['relative_path'] for r in rows}
assert not any(p.is_symlink() for p in target.rglob('*'))
for row in rows:
 p = target / row['relative_path']; assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes']
 if 'retained' in row: assert sha(Path(row['retained'])) == row['sha256']
retained = {}
for directory in proposal['retain_roots']:
 for p in Path(directory).rglob('*'):
  if p.is_file(): retained[str(p)] = sha(p)
assert retained
assert not subprocess.check_output(['git','-c','core.fsmonitor=false','ls-files','--',str(target)],cwd=root)
ps = subprocess.run(['ps','-axo','pid=,command='],capture_output=True,text=True,check=True)
matching = [line for line in ps.stdout.splitlines() if str(target.parent.parent) in line]
assert not matching, matching
lsof = subprocess.run(['lsof','+D',str(target)],capture_output=True,text=True)
assert lsof.returncode == 1 and not lsof.stdout.strip() and not lsof.stderr.strip(), (lsof.returncode,lsof.stdout,lsof.stderr)
allocated = subprocess.check_output(['du','-sk',str(target)],text=True).split()[0]
(out/'PREDELETE.json').write_text(json.dumps({'target':str(target),'files':len(rows),'logical_bytes':sum(r['bytes'] for r in rows),'allocated_KiB':int(allocated),'matching_processes':matching,'lsof_exit':lsof.returncode,'retained_files':len(retained)},indent=2)+'\n')
(out/'RETAINED-PINS.json').write_text(json.dumps(retained,indent=2)+'\n')
shutil.rmtree(target)
assert not target.exists()
for name,pin in retained.items(): assert sha(Path(name)) == pin
record = {'removed':str(target),'files':len(rows),'logical_bytes':sum(r['bytes'] for r in rows),'allocated_KiB':int(allocated),'retained_files':len(retained),'retained_unchanged':True,'source_and_evidence_kept':True}
(out/'RESULT.json').write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps(record))
