from pathlib import Path
import sys,json,hashlib
assert sys.flags.isolated and sys.flags.no_site
r=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 def unique(xs):
  d={}
  for k,v in xs:
   assert k not in d
   d[k]=v
  return d
 return json.loads(p.read_text(),object_pairs_hook=unique)
assert not any(p.is_symlink() for p in r.rglob('*'))
m=read(r/'MANIFEST.json');assert sha(r/'MANIFEST.json')==read(r/'FREEZE.json')['manifest_sha256']
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,h in m.items():
 assert not Path(n).is_absolute() and '..' not in Path(n).parts
 assert sha(r/n)==h,n
for x in read(r/'LOCAL.json'):assert sha(r/'local'/x['path'])==x['sha256']
for x in read(r/'spec/FETCH.json'):assert x['status']==200 and sha(r/'spec'/(x['name']+'.html'))==x['sha256']
assert all(x['exists'] for x in read(r/'ANCHORS.json'))
print(json.dumps({'evidence_integrity':'PASS','inputs':len(m),'compiled_or_proved':False,'scope':'research proposal only'}))
