import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def closed(root, expected, seals):
    if sha(root / "FILES.json") != expected:
        raise SystemExit("external manifest mismatch")
    entries = json.loads((root / "FILES.json").read_text())
    dirs = set()
    for name in entries:
        p = Path(name)
        if p.is_absolute() or str(p) != name or ".." in p.parts:
            raise SystemExit("unsafe path")
        dirs.update(str(x) for x in p.parents if str(x) != ".")
    actual, actual_dirs = set(), set()
    for p in root.rglob("*"):
        mode = p.lstat().st_mode
        rel = p.relative_to(root).as_posix()
        if stat.S_ISDIR(mode):
            actual_dirs.add(rel)
        elif stat.S_ISREG(mode):
            actual.add(rel)
        else:
            raise SystemExit("nonregular input")
    if actual != set(entries) | seals or actual_dirs != dirs:
        raise SystemExit("closed roster mismatch")
    for name, digest in entries.items():
        if sha(root / name) != digest:
            raise SystemExit("changed input: " + name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files-sha256", required=True)
    args = parser.parse_args()
    closed(ROOT, args.files_sha256, {"FILES.json", "FREEZE.json"})
    closed(ROOT / "capsule", "a8f1cc52b53fafc9156b0d7c8a8911e4f57c54def8b5a2b608d92fcc6883a33c", {"FILES.json"})
    result = json.loads((ROOT / "replay/RESULT.json").read_text())
    challenge = json.loads((ROOT / "challenges/RESULT.json").read_text())
    if (result["status"], result["audits"], result["bindings"], challenge["status"], challenge["audits"]) != (
        "PASS", 26, 11, "PASS", 11):
        raise SystemExit("receipt mismatch")
    guards = json.loads((ROOT / "GUARDS.json").read_text())
    if len(guards) != 8 or any(g["returncode"] == 0 or g.get("output_created", False) for g in guards):
        raise SystemExit("guard receipt mismatch")
    print(json.dumps({"status": "PASS", "verdict": "BOUNDED_COMPONENT_ACCEPTED",
        "full_F1_F12": "OPEN", "producer_audits": 26, "independent_audits": 11}))

if __name__ == "__main__":
    main()
