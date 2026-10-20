import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("use Python -I -S")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def reseal(p):
    files = {x.relative_to(p).as_posix(): digest(x) for x in sorted(p.rglob("*"))
             if x.is_file() and x.relative_to(p).as_posix() not in ("FILES.json", "FREEZE.json")}
    (p / "FILES.json").write_text(json.dumps({"algorithm": "sha256", "files": files}, indent=2) + "\n")
    (p / "FREEZE.json").write_text(json.dumps({"manifest_sha256": digest(p / "FILES.json")}) + "\n")

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
source = Path(args.source).resolve()
output = Path(args.output).resolve()
if output.exists() or output == source or source in output.parents:
    raise ValueError("new external output required")
output.mkdir(parents=True)
records = []
for name in ["outer-extra", "nested-cache", "nested-cache-outer-resealed", "nested-empty-dir-outer-resealed",
             "nested-source-outer-resealed", "nested-seals-outer-resealed", "outer-symlink", "outer-duplicate-json", "optimized"]:
    clone = output / "temporary-source"
    shutil.copytree(source, clone)
    flags = ["-I", "-S"]
    resealed = False
    if name == "outer-extra":
        (clone / "extra").write_text("extra")
    elif name in ["nested-cache", "nested-cache-outer-resealed"]:
        cache = clone / "capsule/native/__pycache__"
        cache.mkdir()
        (cache / "oracle.cpython-313.pyc").write_bytes(b"not accepted even when outer manifest permits it")
    elif name == "nested-empty-dir-outer-resealed":
        (clone / "capsule/extra-empty").mkdir()
    elif name == "nested-source-outer-resealed":
        with (clone / "capsule/native/oracle.py").open("a") as f:
            f.write("\nraise RuntimeError('tampered')\n")
    elif name == "nested-seals-outer-resealed":
        cache = clone / "capsule/native/__pycache__"
        cache.mkdir()
        (cache / "oracle.cpython-313.pyc").write_bytes(b"resealed nested closure still violates external pins")
        reseal(clone / "capsule")
    elif name == "outer-symlink":
        (clone / "linked").symlink_to(clone / "check.py")
    elif name == "outer-duplicate-json":
        f = clone / "FILES.json"
        f.write_text(f.read_text().replace('"algorithm": "sha256"', '"algorithm": "sha256", "algorithm": "sha256"', 1))
        (clone / "FREEZE.json").write_text(json.dumps({"manifest_sha256": digest(f)}))
    elif name == "optimized":
        flags.append("-O")
    if name.endswith("outer-resealed"):
        reseal(clone)
        resealed = True
    run = subprocess.run([sys.executable, *flags, str(clone / "check.py"), "--authenticate-only"], text=True, capture_output=True)
    log = run.stdout + run.stderr
    (output / (name + ".log")).write_text(log)
    expected = "nested pin" if name == "nested-seals-outer-resealed" else "closed directory roster" if name == "nested-empty-dir-outer-resealed" else "file digest: native/oracle.py" if name == "nested-source-outer-resealed" else "nonregular entry" if name == "outer-symlink" else "duplicate JSON key" if name == "outer-duplicate-json" else "use Python" if name == "optimized" else "closed file roster"
    if run.returncode == 0 or expected not in log:
        raise ValueError("guard failed: " + name + "\n" + log)
    records.append({"name": name, "exit": run.returncode, "outer_resealed": resealed, "expected_error": expected})
    shutil.rmtree(clone)
(output / "RESULT.json").write_text(json.dumps({"status": "pass", "guards": records}, indent=2) + "\n")
print(json.dumps({"status": "pass", "guards": len(records)}))
