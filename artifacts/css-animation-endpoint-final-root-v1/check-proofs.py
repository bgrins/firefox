import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PACKAGES = {
    "css-animation-endpoint-taint-proof-v1": (
        "b4e22d60e35c7864478f5e36f663a91baccd4f4bfb9ccfec9544ad287056520b",
        "089f59ac4b5b96e448603dfb0810d703e9a4d5e7e9ec8a96452e83751446e6de"),
    "css-animation-endpoint-taint-independent-v1": (
        "0e379bc6a1cd7aec21b68a75e8b1176260588265c84d1eb40af4f4f35c23497e",
        "7168ace9796da00b4779fabd6bfe5ebe8db1a14acbe582053b73e1920c777e30"),
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
        output = Path(tempfile.mkdtemp(prefix="animation-endpoint-root-", dir="/private/tmp")) / "output"
        command += ["--output", str(output)]
    else:
        command += ["--replay"]
    log = HERE / (name + ".log")
    with log.open("w") as stream:
        status = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT).returncode
    records[name] = {"freeze": freeze, "manifest": manifest, "inputs": len(inputs), "command": command, "exit": status, "log_sha256": sha(log)}
    (HERE / "PROOF-REPLAY.json").write_text(json.dumps(records, indent=2) + "\n")
    assert status == 0, name
print("Root proof and source-review replays passed")
