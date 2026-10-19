import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/"MANIFEST.json").read_text())
f=json.loads((p/"FREEZE.json").read_text())
assert hashlib.sha256((p/"MANIFEST.json").read_bytes()).hexdigest()==f["manifest_sha256"]
for name,digest in m["files"].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
assert json.loads((p/"canonical/RESULT.json").read_text())==json.loads((p/"relocated/RESULT.json").read_text())
assert all(x["returncode"] != 0 and not x["output_created"] for x in json.loads((p/"TAMPER.json").read_text()))
print("Receipt integrity and exact replay comparison passed")
