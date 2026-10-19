import ast,hashlib,json,re
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/"MANIFEST.json").read_text())
f=json.loads((p/"FREEZE.json").read_text())
assert hashlib.sha256((p/"MANIFEST.json").read_bytes()).hexdigest()==f["manifest_sha256"]
for name,digest in m["files"].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
ast.parse((p/"run.py").read_text())
assert re.findall(r'^checkCase\("([^"]+)"',(p/"map-taint-equality.html").read_text(),re.M)==json.loads((p/"EXPECTED-IDENTITIES.json").read_text())
print("Runner source/identities authenticated; AST valid; browser NOT_RUN")
