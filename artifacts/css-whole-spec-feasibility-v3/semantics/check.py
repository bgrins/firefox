import hashlib,json,sys
from pathlib import Path
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use isolated Python without optimization')
p=Path(__file__).resolve().parent
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def read(n):return json.loads((p/n).read_text())
s=read('FREEZE.json');m=read('MANIFEST.json')
assert h(p/'MANIFEST.json')==s['manifest_sha256']
assert all(not f.is_symlink() for f in p.rglob('*'))
assert {str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,v in m.items():assert h(p/n)==v,n
for r in read('spec/FETCH.json'):
    assert r['status']==200 and h(p/'spec'/r['file'])==r['sha256']
for r in read('LOCAL.json'):assert h(p/r['retained'])==r['sha256']
for r in read('ANCHORS.json'):
    assert 'id="'+r['anchor']+'"' in (p/'spec'/(r['spec']+'.html')).read_text()
print('PASS',len(m),'research inputs; 8 primary snapshots;',len(read('ANCHORS.json')),'anchors; no proof claim')
