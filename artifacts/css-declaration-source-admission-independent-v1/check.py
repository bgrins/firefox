import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((r/'MANIFEST.json').read_text())
assert sha(r/'MANIFEST.json')==json.loads((r/'FREEZE.json').read_text())['manifest_sha256']
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,h in m.items():assert sha(r/n)==h,n
d=json.loads((r/'DEPENDENCY.json').read_text());p=r.parent/d['directory']
assert sha(p/'FREEZE.json')==d['freeze_sha256']
assert sha(p/'MANIFEST.json')==d['manifest_sha256']
pm=json.loads((p/'MANIFEST.json').read_text())
assert {str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}==set(pm)|{'MANIFEST.json','FREEZE.json'}
for n,h in pm.items():assert sha(p/n)==h,n
assert json.loads((r/'REPLAY.json').read_text())['exit']==0
assert json.loads((r/'RESULT.json').read_text())['theorem_audits']==5
print(json.dumps({'own_inputs':len(m),'producer_inputs':len(pm),'status':'PASS','scope':'limited helper and source-audit review'}))
