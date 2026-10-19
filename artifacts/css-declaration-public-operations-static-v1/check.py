from pathlib import Path
import hashlib,json,re
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((r/'MANIFEST.json').read_text())
assert sha(r/'MANIFEST.json')==json.loads((r/'FREEZE.json').read_text())['manifest_sha256']
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for n,h in m.items():assert sha(r/n)==h,n
pins=json.loads((r/'SOURCE-PINS.json').read_text())
for n,h in pins.items():assert sha(r/'source'/n)==h,n
s=(r/'source/servo/ports/geckolib/glue.rs').read_text().splitlines();name='';rows=[]
for i,l in enumerate(s):
 match=re.match(r'(?:pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?(?:extern\s+"[^"]+"\s+)?fn\s+(\w+)',l)
 if match:name=match[1]
 if re.search(r'\b(?:decls|block)\.push\(',l):rows.append({'function':name,'line':i+1,'call':l.strip()})
record=json.loads((r/'PUSH-CALLERS.json').read_text())
assert rows==record['sites'] and len(rows)==record['count']==22
print(json.dumps({'status':'PASS','inputs':len(m),'source_files':len(pins),'glue_push_sites':len(rows),'scope':'integrity and pinned caller roster; not native execution or universal proof'}))
