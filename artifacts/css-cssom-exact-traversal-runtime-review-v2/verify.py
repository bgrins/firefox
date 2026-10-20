import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).resolve().parent

def pairs(items):
    out = {}
    for key, value in items:
        assert key not in out
        out[key] = value
    return out

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(root, expected):
    assert digest(root / "FILES.json") == expected
    manifest = read(root / "FILES.json")
    directories = {"."}
    for name, pin in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and path.as_posix() == name and ".." not in path.parts
        assert stat.S_ISREG((root / path).lstat().st_mode) and digest(root / path) == pin, name
        directories.update(str(p) for p in path.parents)
    files = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            files.add(relative)
        else:
            assert stat.S_ISDIR(mode) and relative in directories, relative
    assert files == set(manifest) | {"FILES.json", "FREEZE.json"}
    return len(manifest)

if len(sys.argv) != 3 or sys.argv[1] != "--files-sha256":
    raise SystemExit("Usage: python3 -I -S verify.py --files-sha256 REVIEW_PIN")
count = authenticate(HERE, sys.argv[2])
freeze = read(HERE / "FREEZE.json")
assert freeze["files_sha256"] == sys.argv[2] and freeze["payload_count"] == count
runtime = HERE.parent / "css-cssom-exact-traversal-runtime-v2"
assert authenticate(runtime, "15c0026dd6c9a4c87dbe5b1abdac7788054d78714fc3c9400456c97f88f439b2") == 222
authenticate(HERE.parent / "css-cssom-exact-traversal-proposal-v2", "b553dbebc08b6e82b635c30f2e90b254558d513faab385cad3e840abb9465f8c")
assert digest(HERE.parent / "css-cssom-rectangle-standalone-runtime-v1/dom-only/RUN.json") == "6d253dab56b45d07a3808ddebd385c27ec66aa98e5eae6482161f6145a2ab517"
result = subprocess.run([sys.executable, "-I", "-S", "-B", str(HERE / "review_runtime.py"), "--check"], capture_output=True, text=True)
assert result.returncode == 0, result.stdout + result.stderr
assert read(HERE / "VERDICT.json")["status"] == "HOLD_V2_LANDING_LOCAL_PERFORMANCE"
print(json.dumps({"review_payloads": count, "runtime_payloads": 222, "raw_comparison_reproduced": True, "verdict": "HOLD_V2_LANDING_LOCAL_PERFORMANCE"}))
