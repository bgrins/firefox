from pathlib import Path
import hashlib,json,sys
assert sys.flags.isolated and sys.flags.no_site
r=Path(__file__).absolute().parent
assert not r.is_symlink()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(xs):
 d={}
 for k,v in xs:
  assert k not in d
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
for p in r.rglob('*'):assert not p.is_symlink() and (p.is_file() or p.is_dir())
f=read(r/'FREEZE.json');assert sha(r/'MANIFEST.json')==f['manifest_sha256'] and sha(r/'check.py')==f['checker_sha256']
m=read(r/'MANIFEST.json');expected=set(m)|{'FREEZE.json','MANIFEST.json'}
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==expected
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_dir()}=={str(q) for p in expected for q in Path(p).parents if str(q)!='.'}
for p,h in m.items():assert not Path(p).is_absolute() and '..' not in Path(p).parts and sha(r/p)==h
for p in r.rglob('*.json'):read(p)
assert read(r/'RUN.json')['replay_exit']==0
assert read(r/'fresh/REPLAY.json')['status']=='PASS'
assert read(r/'authentication/CHECK.json')['status']=='PASS'
print('AUTHENTICATED',len(m),'replay evidence files')
