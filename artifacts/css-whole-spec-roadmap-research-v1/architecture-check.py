import sys
assert sys.flags.isolated and sys.flags.no_site
import hashlib,json,os,stat
from pathlib import Path,PurePosixPath
root=Path(__file__).resolve().parent
def unique(pairs):
 result={}
 for key,value in pairs:
  assert key not in result
  result[key]=value
 return result
def read(path):return json.loads(path.read_text(),object_pairs_hook=unique)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest=read(root/'architecture-MANIFEST.json')
assert sha(root/'architecture-MANIFEST.json')==read(root/'architecture-FREEZE.json')['manifest_sha256']
actual=set();directories=set()
for item in root.iterdir():
 if item.name!='architecture.md' and not item.name.startswith('architecture-'):continue
 assert not item.is_symlink()
 if item.is_dir():
  directories.add(item.name)
  for parent,ds,fs in os.walk(item,followlinks=False):
   for name in ds+fs:
    p=Path(parent)/name;mode=p.lstat().st_mode
    assert stat.S_ISREG(mode) or stat.S_ISDIR(mode)
    if stat.S_ISREG(mode):actual.add(str(p.relative_to(root)))
    else:directories.add(str(p.relative_to(root)))
 else:
  assert stat.S_ISREG(item.lstat().st_mode)
  actual.add(item.name)
assert actual==set(manifest)|{'architecture-MANIFEST.json','architecture-FREEZE.json'}
assert directories=={str(p) for n in actual for p in PurePosixPath(n).parents if str(p)!='.'}
for name,expected in manifest.items():
 path=PurePosixPath(name);assert not path.is_absolute() and '..' not in path.parts and str(path)==name
 assert name=='architecture.md' or name.startswith('architecture-')
 assert sha(root/name)==expected,name
local=read(root/'architecture-local-receipt.json')
for item in local['representative_inputs']:
 p=root/item['retained'];assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
acceptance=local['accepted_component_receipt'];assert sha(root/acceptance['retained'])==acceptance['sha256']
roster=read(root/'architecture-module-roster.json')
assert len(roster)==local['module_count'] and sum(x['bytes'] for x in roster)==local['source_bytes']
assert len({x['path'] for x in roster})==len(roster)
specs=read(root/'architecture-spec-pins.json');assert len(specs)==8
for item in specs:
 p=root/'architecture-inputs/specs'/(item['name']+'.html')
 assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
print(json.dumps({'status':'PASS','inputs':len(manifest),'representative_sources':len(local['representative_inputs']),'inventoried_modules':len(roster),'primary_spec_snapshots':len(specs),'new_proof_or_runtime_claim':False}))
