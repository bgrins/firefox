from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((r/'MANIFEST.json').read_text())
assert h(r/'MANIFEST.json')==json.loads((r/'FREEZE.json').read_text())['manifest_sha256']
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,v in m.items():assert h(r/n)==v,n
print(json.dumps({'status':'PASS','inputs':len(m),'scope':'static source identity only'}))
