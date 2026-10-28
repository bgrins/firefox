#!/usr/bin/env python3
"""Exact source transport and Rust syntax/format checks; not a typecheck."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
roles = json.loads((ROOT / "SOURCE-ROLES.json").read_text())
assert len(roles) == 6
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for path, role in roles.items():
    assert sha(ROOT / "base" / path) == role["original"]
    assert sha(ROOT / "candidate" / path) == role["candidate"]
with tempfile.TemporaryDirectory(prefix="registered-value-collector-") as temporary:
    scratch = Path(temporary)
    for path in roles:
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "base" / path, target)
    subprocess.run(["git", "apply", "--check", str(ROOT / "native.patch")], cwd=scratch, check=True)
    subprocess.run(["git", "apply", str(ROOT / "native.patch")], cwd=scratch, check=True)
    assert all(sha(scratch / p) == v["candidate"] for p, v in roles.items())
    subprocess.run(["git", "apply", "--reverse", str(ROOT / "native.patch")], cwd=scratch, check=True)
    assert all(sha(scratch / p) == v["original"] for p, v in roles.items())
subprocess.run(["rustfmt", "--check", "--config-path", str(ROOT / "rustfmt.toml"),
                *[str(ROOT / "candidate" / p) for p in roles]], check=True)
result = {"status": "PASS", "paths": 6, "forward_reverse_exact": True,
          "rustfmt_check": True, "native_typecheck": False, "browser_test": False,
          "temporary_outputs_removed": True}
(ROOT / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
