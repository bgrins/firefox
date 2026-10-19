import hashlib,json,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/"MANIFEST.json").read_text())
f=json.loads((p/"FREEZE.json").read_text())
assert hashlib.sha256((p/"MANIFEST.json").read_bytes()).hexdigest()==f["manifest_sha256"]
for name,digest in m["files"].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
result=subprocess.run(["node",str(p/"collect-identities.js"),str(p/"attr-security.html")],check=True,capture_output=True,text=True)
assert json.loads(result.stdout)==json.loads((p/"IDENTITIES.json").read_text())
assert json.loads(result.stdout)["count"]==32
print("32 static test registrations reproduced; no browser assertions executed")
