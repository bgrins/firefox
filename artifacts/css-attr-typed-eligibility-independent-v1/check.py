#!/usr/bin/env python3
"""Authenticate this review before executing its retained source checker."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", action="store_true")
    args = parser.parse_args()
    frozen = json.loads((ROOT / "FREEZE.json").read_text())
    assert digest(ROOT / "MANIFEST.json") == frozen["manifest_sha256"]
    entries = json.loads((ROOT / "MANIFEST.json").read_text())
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()} - {"MANIFEST.json", "FREEZE.json"}
    assert actual == set(entries), "closed file inventory mismatch"
    for name, expected in entries.items():
        path = ROOT / name
        assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
        assert digest(path) == expected, name
    package = ROOT / "producer"
    assert digest(package / "FREEZE.json") == "d4df587c369a966d2be409c431f3319e81995a42c84e2fcdbc7602ee4fb46862"
    assert digest(package / "INPUTS.json") == "a4b278e3903ae557c0e7ec0864c8d41e87d405df7aa9f72652a7dfa23ff372f6"
    for name, expected in json.loads((package / "INPUTS.json").read_text()).items():
        assert digest(package / name) == expected, name
    if args.checks:
        for name, same in json.loads((ROOT / "FINAL-CHECKS.json").read_text())["draft_comparison"].items():
            assert same and (ROOT / "draft-inputs" / name).read_bytes() == (package / name).read_bytes(), name
        subprocess.run([sys.executable, str(package / "check.py")], cwd=package, check=True)
    print(json.dumps({"status": "PASS", "authenticated": len(entries), "source_checks": args.checks, "native_browser_acceptance": "PENDING"}))

if __name__ == "__main__":
    main()
