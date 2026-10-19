from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
m=json.loads((r/'MANIFEST.json').read_text())
for name,digest in m.items():
 p=r/name
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
pins=json.loads((r/'SOURCE-PINS.json').read_text())
for name,digest in pins.items():
 assert hashlib.sha256((r/'source'/name).read_bytes()).hexdigest()==digest,name
s=(r/'source/servo/components/style/values/specified/number.rs').read_text()
assert 'self.0.is_nan() && other.0.is_nan()' in s
s=(r/'source/servo/components/style/values/specified/calc.rs').read_text()
assert 'Leaf::Time(one) => *one = NoCalcTime::from_seconds(op(one.seconds()))' in s
s=(r/'source/servo/components/style/values/specified/time.rs').read_text()
assert 'pub struct NoCalcTime' in s and 'PartialEq' in s
print(json.dumps({'status':'PASS','authenticated_inputs':len(m),'source_files':len(pins),'scope':'integrity and selected source anchors only'}))
