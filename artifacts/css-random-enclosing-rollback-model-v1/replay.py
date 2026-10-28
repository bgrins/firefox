import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
assert hashlib.sha256(LEAN.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
output = HERE / "validation"
output.mkdir(exist_ok=False)
results = {}
with tempfile.TemporaryDirectory(prefix="random-enclosing-model-", dir="/private/tmp") as work:
    work = Path(work)
    for name in ("Rollback", "Enclosing", "Audit", "TypedOnly", "ResetZero", "ResetSuccess"):
        shutil.copyfile(HERE / (name + ".lean"), work / (name + ".lean"))
    env = dict(os.environ, LEAN_PATH=str(work))
    for name in ("Rollback", "Enclosing", "Audit", "TypedOnly", "ResetZero", "ResetSuccess"):
        command = [str(LEAN), name + ".lean"]
        if name in ("Rollback", "Enclosing"):
            command += ["-o", name + ".olean"]
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True)
        text = result.stdout + result.stderr
        (output / (name + ".log")).write_text(text)
        results[name] = {"exit": result.returncode, "log_sha256": hashlib.sha256(text.encode()).hexdigest()}
        if name in ("TypedOnly", "ResetZero", "ResetSuccess"):
            assert result.returncode != 0 and "is false" in text and "Tactic `decide`" in text
        else:
            assert result.returncode == 0, text
    assert "sorryAx" not in (output / "Audit.log").read_text()
    scratch = str(work)
assert not Path(scratch).exists()
(output / "CHECK.json").write_text(json.dumps({"results": results, "scratch_removed": True, "native_equivalence_claim": False}, indent=2) + "\n")
print(json.dumps(results))
