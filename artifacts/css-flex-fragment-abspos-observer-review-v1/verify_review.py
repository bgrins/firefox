#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PINS = {
    "standalone-overflow-proposal/base.cpp": "3a7fe90d495e15b1b92a0cb59cb3a993996891b9faddebbe99ed4c8baa4e88b6",
    "standalone-overflow-proposal/candidate.cpp": "bb2886bfb6acd682e364fd25c26de867eb79e31b7646fb8d38dd724e4696b07e",
    "standalone-overflow-proposal/proposal.patch": "2ba97b6795398271be0aa4868680190c45b975f7f13da6fa573d997e43840e01",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root):
    files = json.loads((root / "FILES.json").read_text())
    freeze = json.loads((root / "FREEZE.json").read_text())
    assert sha(root / "FILES.json") == freeze["files_sha256"], "freeze identity"
    actual = set()
    for path in root.rglob("*"):
        assert not path.is_symlink(), "symlink rejected"
        relative = path.relative_to(root)
        assert not {".lake", "__pycache__", "target"}.intersection(relative.parts), "cache rejected"
        assert path.suffix not in {".olean", ".ilean", ".o", ".pyc", ".exe", ".dylib"}, "compiler product rejected"
        if path.is_file():
            actual.add(str(relative))
    assert actual == set(files) | {"FILES.json", "FREEZE.json"}, "closed roster"
    for name, expected in files.items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts, "manifest path"
        assert sha(root / name) == expected, "payload hash: " + name
    for name, expected in PINS.items():
        assert sha(root / name) == expected, "source role identity: " + name
    roles = json.loads((root / "standalone-overflow-proposal/SOURCE.json").read_text())
    assert roles["base_sha256"] == PINS["standalone-overflow-proposal/base.cpp"], "base role"
    assert roles["candidate_sha256"] == PINS["standalone-overflow-proposal/candidate.cpp"], "candidate role"
    assert roles["base_revision"] == "92a6fddf18e5828b17d7491a34663a0d5a9c12ad", "base revision"
    return len(files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    count = check(ROOT)
    if args.replay:
        with tempfile.TemporaryDirectory(prefix="css-overflow-relocated-") as name:
            target = Path(name) / "capsule"
            target.mkdir()
            for relative in [*json.loads((ROOT / "FILES.json").read_text()), "FILES.json", "FREEZE.json"]:
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, path)
            check(target)
            result = subprocess.run([sys.executable, str(target / "run_checks.py")],
                                    cwd=target, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            assert result.returncode == 0, result.stdout
            receipt = json.loads(result.stdout)
            print(json.dumps({"payload_files": count, "relocated_replay": receipt}, indent=2))
    else:
        print(json.dumps({"payload_files": count, "closed_roster": True}))


if __name__ == "__main__":
    main()
