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
assert hashlib.sha256(LEAN.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
output = Path(sys.argv[1]).resolve()
assert output.parent == HERE and not output.exists()
output.mkdir()
records = []
with tempfile.TemporaryDirectory(prefix="move-notification-") as temporary:
    scratch = Path(temporary)
    predecessor = ROOT / "artifacts/css-move-notification-coverage-model-v1/Coverage.lean"
    assert hashlib.sha256(predecessor.read_bytes()).hexdigest() == '5098535452580644191248d32510c93fd75f0ef829801fbe437ef924482dcc84'
    shutil.copyfile(predecessor, scratch / "Coverage.lean")
    parent = ROOT / "artifacts/css-move-parent-coverage-model-v1/Parent.lean"
    assert hashlib.sha256(parent.read_bytes()).hexdigest() == "a536cc705a150b7d9b2fd25d1c1f26890c1aad5d4fa73452973eac973ffdd9a0"
    shutil.copyfile(parent, scratch / "Parent.lean")
    reorder = ROOT / "artifacts/css-move-reorder-coverage-model-v1/Reorder.lean"
    assert hashlib.sha256(reorder.read_bytes()).hexdigest() == "c30a57296da0b9a69318c2aa8abce896364022bd39e5d0e3fb32f09c5354606e"
    shutil.copyfile(reorder, scratch / "Reorder.lean")
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    for name in ("Coverage", "Parent", "Reorder", "Gap", "Audit", "FalseRight", "FalseLeft"):
        args = ["-o", name + ".olean", name + ".lean"] if name in ("Coverage", "Parent", "Reorder", "Gap") else [name + ".lean"]
        run = subprocess.run([str(LEAN), *args], cwd=scratch,
            env=dict(os.environ, LEAN_PATH=str(scratch)), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=30)
        (output / (name + ".log")).write_bytes(run.stdout)
        records.append({"name": name, "exit": run.returncode})
        assert (run.returncode == 0) == (not name.startswith("False")), name
        if name.startswith("False"):
            assert b"Tactic `decide` proved that the proposition" in run.stdout and b"is false" in run.stdout
    audit = (output / "Audit.log").read_text()
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    assert audit.count("GapCoverage.") == 10
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({"claims": 10, "false_controls_rejected": 2,
    "scratch_removed": True, "canonical_coverage_increment": 0,
    "source_sha256": hashlib.sha256((HERE / "Gap.lean").read_bytes()).hexdigest(),
    "commands": records}, indent=2) + "\n")
print("Same-parent reorder claims checked; two false controls rejected; scratch removed")
