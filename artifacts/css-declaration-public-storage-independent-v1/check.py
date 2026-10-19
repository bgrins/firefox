from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((r/'MANIFEST.json').read_text())
assert sha(r/'MANIFEST.json')==json.loads((r/'FREEZE.json').read_text())['manifest_sha256']
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,h in m.items():assert sha(r/n)==h,n
c=json.loads((r/'checkpoint/CHECKPOINT.json').read_text())
for n,h in c['sources'].items():assert sha(r/'checkpoint'/n)==h,n
assert len(c['theorems'])==35 and json.loads((r/'RESULT.json').read_text())['theorem_audits']==35
assert json.loads((r/'REPLAY.json').read_text())['exit']==0
print(json.dumps({'status':'PASS','inputs':len(m),'audits':35,'scope':'selected model checkpoint, native composition pending'}))
