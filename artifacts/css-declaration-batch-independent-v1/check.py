import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, os, stat, subprocess
from pathlib import Path, PurePosixPath

R = Path(__file__).resolve().parent

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

def authenticate(root):
    manifest = read(root / "MANIFEST.json")
    freeze = read(root / "FREEZE.json")
    assert freeze["manifest_sha256"] == digest(root / "MANIFEST.json")
    allowed = set(manifest) | {"MANIFEST.json", "FREEZE.json"}
    actual = set()
    directories = set()
    for path in root.rglob("*"):
        mode = path.lstat().st_mode
        assert not stat.S_ISLNK(mode)
        if stat.S_ISDIR(mode):
            directories.add(path.relative_to(root).as_posix())
        else:
            assert stat.S_ISREG(mode)
            actual.add(path.relative_to(root).as_posix())
    assert actual == allowed
    expected_directories = set()
    for name in allowed:
        rel = PurePosixPath(name)
        assert not rel.is_absolute() and ".." not in rel.parts and rel.as_posix() == name
        expected_directories.update(str(p) for p in rel.parents if str(p) != ".")
    assert directories == expected_directories
    for name, expected in manifest.items():
        assert digest(root / name) == expected, name
    return len(manifest)

p = argparse.ArgumentParser()
p.add_argument("--producer", type=Path)
p.add_argument("--replay-output", type=Path)
a = p.parse_args()
count = authenticate(R)
pins = read(R / "EXTERNAL-PINS.json")
producer = (a.producer or (R.parent.parent / pins["producer"])).resolve()
for name, expected in pins["pins"].items():
    assert digest(producer / name) == expected, name
external = authenticate(producer)
assert external == 209
n = {"__file__": str(R / "independent_checks.py"), "__name__": "authenticated_independent_checks"}
exec(compile((R / "independent_checks.py").read_text(), n["__file__"], "exec"), n)
result = n["run"](producer, R / "fresh-replay")
assert result == read(R / "INDEPENDENT-CHECKS.json")
if a.replay_output:
    output = a.replay_output.resolve()
    assert not output.exists() and not output.is_relative_to(R) and not output.is_relative_to(producer)
    subprocess.run([sys.executable, "-I", "-S", str(producer / "check.py"), "--output", str(output)], check=True)
print(json.dumps({"review_inputs": count, "producer_inputs": external, "independent_checks": "PASS"}))
