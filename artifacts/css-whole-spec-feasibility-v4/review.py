import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


pins = {
    "semantics": ("a0bcdaab3c89d4c1d3975a1ecbbc6e2e94a7a4e447fdb331cd9bc42251cb16a5", "69bb56b4d9a1282bcf20582f85d476ab000837fe66d19778d825f648ec5c8a70"),
    "validation": ("7006991eac81c65ad20764e184c8173d153b26fdb9de80254e28da9a360229af", "0016dcc949eeb37a4458ed37c63551e9c2599483292dfdd306cea41d10bfdea8"),
}
for name, (freeze, manifest) in pins.items():
    directory = ROOT / name
    assert sha(directory / "FREEZE.json") == freeze
    assert sha(directory / "MANIFEST.json") == manifest
    inputs = json.loads((directory / "MANIFEST.json").read_text())
    if "files" in inputs:
        inputs = inputs["files"]
    for path, digest in inputs.items():
        assert not Path(path).is_absolute() and ".." not in Path(path).parts
        assert not (directory / path).is_symlink() and sha(directory / path) == digest
inventory = ROOT / "inventory"
assert sha(inventory / "FILES.sha256") == "2a3d72da10d088c862981ca5bfdc8c8a3d0eb53ce6fb8236f1624025974681e4"
for line in (inventory / "FILES.sha256").read_text().splitlines():
    digest, path = line.split("  ", 1)
    assert not Path(path).is_absolute() and ".." not in Path(path).parts
    assert sha(inventory / path) == digest
env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTHON", "LEAN_"))}
scratch = Path(tempfile.mkdtemp(prefix="css-v4-root-", dir="/private/tmp")) / "output"
commands = [
    ("inventory", ["python3", "-I", "-S", str(inventory / "demo.py")]),
    ("semantics-integrity", ["python3", "-I", "-S", str(ROOT / "semantics/check.py")]),
    ("validation", ["python3", "-I", "-S", str(ROOT / "validation/check.py")]),
    ("semantics-replay", ["python3", "-I", "-S", str(ROOT / "semantics/replay.py"), "--output", str(scratch)]),
]
records = []
for name, command in commands:
    log = ROOT / (name + "-root.log")
    with log.open("w") as stream:
        result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
    records.append({"name": name, "command": command, "exit": result.returncode, "log_sha256": sha(log)})
    (ROOT / "ROOT-REVIEW.json").write_text(json.dumps({"pins": pins, "commands": records, "scope": "Root read reports and prototypes; structural demo and bounded Lean replay only, not whole CSS coverage."}, indent=2) + "\n")
    assert result.returncode == 0, name
assert json.loads((ROOT / "inventory-root.log").read_text()) == json.loads((inventory / "RESULT.json").read_text())
print("All three research packages authenticated; inventory and Lean prototypes replayed")
