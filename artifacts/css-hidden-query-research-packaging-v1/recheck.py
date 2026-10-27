import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires python3 -I -S without optimization")

import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parent.parent
rows = json.loads((here / "SAFE-PATHS.json").read_text())
seen = set()
total = 0
for row in rows:
    name = row["path"]
    if name in seen or not name.startswith("artifacts/") or ".." in Path(name).parts:
        raise SystemExit(f"invalid path: {name}")
    seen.add(name)
    path = root / name
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"not a regular payload: {name}")
    data = path.read_bytes()
    if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
        raise SystemExit(f"payload changed: {name}")
    total += len(data)
print(json.dumps({"result": "PASS", "files": len(rows), "bytes": total}))
