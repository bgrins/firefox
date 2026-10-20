import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use python3 -I -S, without optimization")
from pathlib import Path
import hashlib, json, stat
root = Path(__file__).resolve().parent
hash_bytes = lambda data: hashlib.sha256(data).hexdigest()
def regular(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise RuntimeError("not regular: " + str(path))
for name in ("FILES.json", "FREEZE.json"):
    regular(root / name)
freeze = json.loads((root / "FREEZE.json").read_text())
if hash_bytes((root / "FILES.json").read_bytes()) != freeze["files_sha256"]:
    raise RuntimeError("manifest mismatch")
if hash_bytes(Path(__file__).read_bytes()) != freeze["checker_sha256"]:
    raise RuntimeError("checker mismatch")
files = json.loads((root / "FILES.json").read_text())
expected = set(files) | {"FILES.json", "FREEZE.json"}
dirs = set()
for name in files:
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or str(p) != name:
        raise RuntimeError("unsafe path")
    dirs.update(str(parent) for parent in p.parents if str(parent) != ".")
actual = set()
def walk(directory):
    for p in directory.iterdir():
        name = str(p.relative_to(root))
        mode = p.lstat().st_mode
        if stat.S_ISDIR(mode):
            if name not in dirs:
                raise RuntimeError("extra directory: " + name)
            walk(p)
        elif stat.S_ISREG(mode):
            actual.add(name)
        else:
            raise RuntimeError("nonregular entry: " + name)
walk(root)
if actual != expected:
    raise RuntimeError("roster mismatch")
for name, digest in files.items():
    if hash_bytes((root / name).read_bytes()) != digest:
        raise RuntimeError("input mismatch: " + name)
commands = json.loads((root / "work-final/COMMANDS.json").read_text())
if len(commands) != 59 or any(c["exit"] or c["stderr"] for c in commands):
    raise RuntimeError("failed replay receipt")
audits = json.loads((root / "AUDITS.json").read_text())
if len(audits) != 17 or len({a["name"] for a in audits}) != 17:
    raise RuntimeError("audit roster")
if any(not set(a["axioms"]) <= {"propext", "Classical.choice", "Quot.sound"} for a in audits):
    raise RuntimeError("unexpected axiom")
print(json.dumps({"status":"PASS", "files":len(files), "audits":17,
                  "scope":"integrity and retained receipts; fresh kernel replay uses compile.py"}))
