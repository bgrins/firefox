import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--freeze-sha", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
repo = here.parents[1]
source = here.parent / "css-worker-font-removal-proof-v1"
assert digest(source / "FREEZE-v2.json") == args.freeze_sha
freeze = json.loads((source / "FREEZE-v2.json").read_text())
assert digest(source / "check.py") == freeze["checker_sha256"]
assert digest(source / "MANIFEST.json") == freeze["manifest_sha256"]
manifest = json.loads((source / "MANIFEST.json").read_text())
output = Path(args.output).resolve()
output.mkdir(exist_ok=False)
with tempfile.TemporaryDirectory(prefix="worker-removal-root-", dir="/private/tmp") as tmp:
    capsule = Path(tmp) / "capsule"
    capsule.mkdir()
    for name in set(manifest["files"]) | {"check.py", "MANIFEST.json", "FREEZE-v2.json"}:
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        target = capsule / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    lean = repo / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
    command = ["python3", "-I", "-S", "-B", str(capsule / "check.py"),
               "--manifest-sha", freeze["manifest_sha256"], "--lean", str(lean)]
    with (output / "replay.log").open("w") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    record = {"exit_code": result.returncode, "freeze_sha256": args.freeze_sha,
              "manifest_sha256": freeze["manifest_sha256"],
              "checker_sha256": freeze["checker_sha256"],
              "fresh_relocated_source_only": True, "command": command,
              "replay_log_sha256": digest(output / "replay.log")}
    (output / "RESULT.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    raise SystemExit(result.returncode)
