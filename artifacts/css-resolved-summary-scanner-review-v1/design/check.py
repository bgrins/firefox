#!/usr/bin/env python3
"""Authenticate the source-design package; this is not a native/model replay."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
freeze = json.loads((root / "FREEZE.json").read_text())
assert digest(root / "INPUTS.json") == freeze["inputs_sha256"]
inputs = json.loads((root / "INPUTS.json").read_text())
for name, expected in inputs.items():
    assert digest(root / name) == expected, name
parent = root / "inputs"
parent_freeze = json.loads((parent / "FREEZE.json").read_text())
assert digest(parent / "INPUTS.json") == parent_freeze["inputs_sha256"]
parent_inputs = json.loads((parent / "INPUTS.json").read_text())
for path in (parent / "sources").rglob("*.rs"):
    name = str(path.relative_to(parent))
    assert digest(path) == parent_inputs[name], name
for record in json.loads((parent / "spec/FETCH.json").read_text()):
    path = parent / "spec" / (record["name"] + ".html")
    if path.exists():
        assert digest(path) == record["sha256"], path
print(json.dumps({"status": "PASS", "entries": len(inputs),
                  "scope": "source design and proposed mathematical contract",
                  "native_patch": "NONE", "implemented_theorem": "NONE",
                  "browser_execution": "NOT RUN"}, indent=2))
