#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(root):
    files = {str(path.relative_to(root)): sha(path) for path in sorted(root.rglob("*"))
             if path.is_file() and path.name not in {"FILES.json", "FREEZE.json"}}
    (root / "FILES.json").write_text(json.dumps(files, indent=2) + "\n")
    (root / "FREEZE.json").write_text(json.dumps({"files_sha256": sha(root / "FILES.json")}) + "\n")


def check(root, expected):
    result = subprocess.run([sys.executable, str(root / "verify.py")], cwd=root,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if expected is None:
        assert result.returncode == 0, result.stdout
    else:
        assert result.returncode != 0 and expected in result.stdout, result.stdout
    return {"expected_gate": expected, "exit": result.returncode, "output": result.stdout}


def main():
    receipts = []
    with tempfile.TemporaryDirectory(prefix="css-overflow-integrity-") as name:
        root = Path(name) / "capsule"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("FILES.json", "FREEZE.json"))
        seal(root)
        receipts.append({"name": "valid", **check(root, None)})
        extra = root / "unexpected.txt"
        extra.write_bytes(b"cache")
        receipts.append({"name": "extra-file", **check(root, "closed roster")})
        extra.unlink()
        extra = root / ".lake/build/cache/unexpected.olean"
        extra.parent.mkdir(parents=True)
        extra.write_bytes(b"cache")
        seal(root)
        receipts.append({"name": "resealed-extra-cache", **check(root, "cache rejected")})
        shutil.rmtree(root / ".lake")
        seal(root)
        source = root / "SourceGeometry.lean"
        original = source.read_bytes()
        source.write_bytes(original + b"\n-- changed\n")
        receipts.append({"name": "changed-source", **check(root, "payload hash")})
        source.write_bytes(original)
        candidate = root / "candidate-nsContainerFrame.cpp"
        candidate.write_bytes((root / "sources/nsContainerFrame.cpp").read_bytes())
        seal(root)
        receipts.append({"name": "resealed-role-substitution", **check(root, "source role identity")})
    print(json.dumps({"controls": receipts, "temporary_products_removed": True}, indent=2))


if __name__ == "__main__":
    main()
