#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

manifest = json.loads((ROOT / "SOURCES.json").read_text())
for name, expected in manifest["files"].items():
    data = (ROOT / "source" / name).read_bytes()
    assert digest(data) == expected, name
    pinned = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", f"{manifest['revision']}:{name}"], cwd=REPO)
    assert data == pinned, name
prior = json.loads((ROOT / "PRIOR-WORK.json").read_text())
for name, record in prior.items():
    assert digest((ROOT / "prior-work" / name).read_bytes()) == record["sha256"], name
    assert digest((REPO / name).read_bytes()) == record["sha256"], f"prior work changed: {name}"
    present = subprocess.run(["git", "-c", "core.fsmonitor=false", "cat-file", "-e", f"{manifest['revision']}:{name}"], cwd=REPO, capture_output=True).returncode == 0
    assert present == record["tracked_at_basis"], name
assert (ROOT / "REPORT.md").is_file()
assert (ROOT / "CONTROLS.md").is_file()
print(json.dumps({"result": "PASS", "pinned_native_files": len(manifest["files"]), "preserved_prior_files": len(prior), "scope": "source identity and prior-work preservation only"}, indent=2))
