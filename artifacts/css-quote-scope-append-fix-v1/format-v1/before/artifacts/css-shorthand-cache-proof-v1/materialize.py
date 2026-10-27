import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PARENT = "0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1"
out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else BASE
out.mkdir(parents=True, exist_ok=True)
record = json.loads((BASE / "SOURCE-v1.json").read_text())
for path, entry in record["files"].items():
    for kind in ("old", "current"):
        data = (
            subprocess.check_output(["git", "show", f"{PARENT}:{path}"], cwd=ROOT)
            if kind == "old"
            else (ROOT / path).read_bytes()
        )
        if hashlib.sha256(data).hexdigest() != entry[f"{kind}_sha256"]:
            raise RuntimeError(f"Source identity mismatch: {kind} {path}")
        target = out / entry[f"{kind}_snapshot"]
        if target.exists() and target.read_bytes() != data:
            raise RuntimeError(f"Refusing to replace different snapshot: {target}")
        target.write_bytes(data)
print("Materialized eight authenticated native snapshots.")
