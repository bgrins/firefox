import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require isolated nonoptimized Python with no site")
import hashlib
import json
from pathlib import Path
p=Path(__file__).resolve().parent
if len(sys.argv)!=3 or sys.argv[1]!="--files-sha256":
    raise SystemExit("usage: verify.py --files-sha256 PIN")
raw=(p/"FILES.json").read_bytes()
assert hashlib.sha256(raw).hexdigest()==sys.argv[2]
files=json.loads(raw)
paths=list(p.rglob("*"))
assert not any(f.is_symlink() for f in paths)
assert sorted(files)==sorted(str(f.relative_to(p)) for f in paths if f.is_file() and f.name not in {"FILES.json","FREEZE.json"})
for name,pin in files.items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==pin,name
freeze=json.loads((p/"FREEZE.json").read_text())
assert freeze["files_sha256"]==sys.argv[2] and freeze["payload_count"]==len(files)
checks=json.loads((p/"SOURCE-CHECKS.json").read_text())
assert all(checks["source_checks"].values())
assert checks["compiler_runs"]==checks["browser_runs"]==0
for name,pin in checks["source_pins"].items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==pin
print(json.dumps({"payload_count":len(files),"status":"SOURCE_ONLY_RECOMMENDATION_NO_PERFORMANCE_CLAIM"}))
