import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PACKAGES = {
    "css-animation-base-metadata-proof-v1": (
        "7f490b3ff2435668b86148ee0cecb29d2ce65bbda107d6abab1c1fd2ef118daf",
        "9db7eab2cd4a1fca9dd8768530736b616aef5e6062f070343b9c4a9f6b215290"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(items):
    result = {}
    for key, value in items:
        assert key not in result
        result[key] = value
    return result


records = {}
env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "LEAN_"))}
for name, (freeze, manifest) in PACKAGES.items():
    source = ROOT / "artifacts" / name
    assert sha(source / "FREEZE.json") == freeze
    assert sha(source / "MANIFEST.json") == manifest
    inputs = json.loads((source / "MANIFEST.json").read_text(), object_pairs_hook=unique)
    assert {str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()} == set(inputs) | {"FREEZE.json", "MANIFEST.json"}
    for path, digest in inputs.items():
        assert not Path(path).is_absolute() and ".." not in Path(path).parts
        assert not (source / path).is_symlink() and sha(source / path) == digest
    command = ["python3", "-I", "-S", str(source / "check.py")]
    if name.endswith("proof-v1"):
        output = Path(tempfile.mkdtemp(prefix="animation-base-root-", dir="/private/tmp")) / "output"
        command += ["--output", str(output)]
    else:
        command += ["--replay"]
    log = HERE / (name + ".log")
    with log.open("w") as stream:
        status = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT).returncode
    records[name] = {"freeze": freeze, "manifest": manifest, "inputs": len(inputs), "command": command, "exit": status, "log_sha256": sha(log)}
    (HERE / "PROOF-REPLAY.json").write_text(json.dumps(records, indent=2) + "\n")
    assert status == 0, name
print("Root base metadata proof replay passed")
