import hashlib,json,stat,sys
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/"FILES.json").read_text())
actual={str(x.relative_to(p)) for x in p.rglob("*") if not x.is_dir()}-{ "FILES.json", "FREEZE.json" }
if actual!=set(m): raise SystemExit("roster mismatch")
for n,h in m.items():
 f=p/n
 if f.is_symlink() or not stat.S_ISREG(f.stat().st_mode) or hashlib.sha256(f.read_bytes()).hexdigest()!=h: raise SystemExit("mismatch: "+n)
print("PASS",len(m),"payloads")
