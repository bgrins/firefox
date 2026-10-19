import hashlib,json,re
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/"MANIFEST.json").read_text())
f=json.loads((p/"FREEZE.json").read_text())
assert hashlib.sha256((p/"MANIFEST.json").read_bytes()).hexdigest()==f["manifest_sha256"]
for name,digest in m["files"].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
for row in json.loads((p/"SOURCE-PINS.json").read_text()):
 assert hashlib.sha256((p/"source"/row["path"]).read_bytes()).hexdigest()==row["sha256"]
html=(p/"map-taint-equality.html").read_text()
assert html.split("<script>")[1].split("</script>")[0]==(p/"map-taint-equality.js").read_text()
assert re.findall(r'^checkCase\("([^"]+)"',html,re.M)==json.loads((p/"EXPECTED-IDENTITIES.json").read_text())
assert len(json.loads((p/"EXPECTED-IDENTITIES.json").read_text()))==9
print("Source, proposal and identity authentication passed; no browser execution")
