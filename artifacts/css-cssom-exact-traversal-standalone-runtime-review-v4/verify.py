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
capture=HERE.parent/'css-cssom-exact-traversal-standalone-postprocess-v4'
assert authenticate(capture,'ae43eed36c8cf69e3c47aa96bd4ee91ff5355bc5a8d97bdde4be12e7b936870f')==124
authenticate(HERE.parent/'css-cssom-exact-traversal-proposal-v4','9cb90bc4e1739c482b2b20785389b002cfeb297bc958b42684e58d37fa4e4770')
assert digest(HERE.parent/'css-cssom-rectangle-standalone-runtime-v1/integer-only/RUN.json')=='2226f1e77d99d9f566ff977f10aa89fd5bbf3538934656a1721104a26d64a0c0'
r=subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'review_runtime.py'),'--check'],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
assert read(HERE/'VERDICT.json')['status']=='PASS_STANDALONE_WITHOUT_FIX102_RUNTIME'
assert read(HERE/'CAPTURE-AUTHENTICATION.json')['count']==115
print(json.dumps({'review_payloads':count,'runtime_capture_payloads':124,'raw_rows':74,'raw_ends':23,'wpt_exit':1,'verdict':'PASS_STANDALONE_WITHOUT_FIX102_RUNTIME'}))
