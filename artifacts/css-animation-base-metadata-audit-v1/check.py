import sys
assert sys.flags.isolated and sys.flags.no_site
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
def pairs(xs):
 d={}
 for k,v in xs:
  assert k not in d
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=read(R/'FREEZE.json');assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=read(R/'MANIFEST.json');files=set(m)|{'MANIFEST.json','FREEZE.json'};dirs=set()
for n in files:
 p=Path(n);assert not p.is_absolute() and n==p.as_posix() and '..' not in p.parts
 dirs.update(str(a) for a in p.parents if str(a)!='.')
actual=set();actualdirs=set()
for p in R.rglob('*'):
 assert not p.is_symlink()
 if p.is_dir():actualdirs.add(p.relative_to(R).as_posix())
 else:assert p.is_file();actual.add(p.relative_to(R).as_posix())
assert actual==files and actualdirs==dirs
for n,h in m.items():assert sha(R/n)==h,n
for n,h in read(R/'SOURCE-PINS.json').items():assert sha(R/'source'/n)==h
assert read(R/'SYNTAX.json')['exit']==0
print(json.dumps({'status':'PASS','inputs':len(m),'browser':'UNEXECUTED','hypothesis':'UNCONFIRMED'}))
