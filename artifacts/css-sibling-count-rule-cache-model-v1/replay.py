import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
SOURCE = ROOT / "artifacts/css-contextual-easing-dependency-cache-model-v1/Dependency.lean"
assert hashlib.sha256(LEAN.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "d49c2f91465f95ba9051d517acb805b32c19612abe8d76e219574fac1862add6"
output = Path(sys.argv[1]).resolve()
assert output.parent == HERE and not output.exists()
output.mkdir()
records = []
with tempfile.TemporaryDirectory(prefix="sibling-count-lean-") as temporary:
    scratch = Path(temporary)
    shutil.copyfile(SOURCE, scratch / "Dependency.lean")
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    for name in ("Dependency", "Witness", "Audit", "FalseReuse"):
        args = ["-o", name + ".olean", name + ".lean"] if name in ("Dependency", "Witness") else [name + ".lean"]
        run = subprocess.run([str(LEAN), *args], cwd=scratch, env=dict(os.environ, LEAN_PATH=str(scratch)),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        (output / (name + ".log")).write_bytes(run.stdout)
        records.append({"name": name, "exit": run.returncode})
        assert (run.returncode == 0) == (name != "FalseReuse"), name
        if name == "FalseReuse":
            assert b"Tactic `decide` proved that the proposition" in run.stdout and b"is false" in run.stdout
    audit = (output / "Audit.log").read_text()
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({"success": True, "claims": 1,
    "false_controls_rejected": 1, "scratch_removed": True, "canonical_coverage_increment": 0,
    "witness_sha256": hashlib.sha256((HERE / "Witness.lean").read_bytes()).hexdigest(),
    "dependency_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "commands": records}, indent=2) + "\n")
print("One equal-font cache-alias witness checked; false reuse rejected; scratch removed")
