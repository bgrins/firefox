import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
if sys.flags.optimize:raise RuntimeError("Assertions required")
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);a=p.parse_args()
assert hashlib.sha256((root/"FILES.json").read_bytes()).hexdigest()==a.manifest_sha
rows=json.loads((root/"FILES.json").read_text())
expected={r["path"] for r in rows}|{"FILES.json","FREEZE.json"}
actual={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() or p.is_symlink()}
assert actual==expected,(sorted(actual-expected),sorted(expected-actual))
assert not any(p.is_symlink() for p in root.rglob("*"))
for row in rows:assert hashlib.sha256((root/row["path"]).read_bytes()).hexdigest()==row["sha256"],row["path"]
freeze=json.loads((root/"FREEZE.json").read_text());assert freeze["manifest_sha256"]==a.manifest_sha and freeze["files"]==len(rows)
checks=runpy.run_path(str(root/"check.py"));checks["authenticate"]();checks["authenticate_providers"]()
print(json.dumps({"outerAndNestedRosters":True,"files":len(rows),"status":freeze["status"]}))
