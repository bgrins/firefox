import hashlib,json,sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site
r=Path(__file__).resolve().parent
def read(p):
 def unique(items):
  d={}
  for k,v in items:
   assert k not in d
   d[k]=v
  return d
 return json.loads(p.read_text(),object_pairs_hook=unique)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not any(p.is_symlink() for p in r.rglob('*'))
m=read(r/'MANIFEST.json');assert sha(r/'MANIFEST.json')==read(r/'FREEZE.json')['manifest_sha256']
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,h in m.items():
 assert not Path(n).is_absolute() and '..' not in Path(n).parts
 assert sha(r/n)==h,n
result=read(r/'replay/RESULT.json');assert len(result['theorems'])==14 and result['source_bindings']==13 and len(result['semantic_mutants_rejected'])==4
assert len(read(r/'GUARDS.json'))==4
print(json.dumps({'review_integrity':'PASS','inputs':len(m),'formal_scope':'conditional selected-value and marker; otherFlags history is model-only frame','runtime':'3FAIL41PASS to44PASS;5OK'}))
