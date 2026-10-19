import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
for f,h in json.loads((r/"MANIFEST.json").read_text())["files"].items():
 assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h,f
for f,h in json.loads((r/"SOURCE-PINS.json").read_text()).items():
 assert hashlib.sha256((r/"source"/f).read_bytes()).hexdigest()==h,f
assert "attr_tainted: self.attr_tainted" in (r/"source/servo/components/style/properties_and_values/value.rs").read_text()
assert "bool propertiesChanged = mProperties != properties;" in (r/"source/dom/animation/KeyframeEffect.cpp").read_text()
print("Authenticated bounded animation source audit and six-case proposal; browser NOT_RUN")
