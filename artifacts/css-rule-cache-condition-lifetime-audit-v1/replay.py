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
with tempfile.TemporaryDirectory(prefix="rule-cache-conditions-") as temporary:
    scratch = Path(temporary)
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    for name in ("Accumulation", "Audit", "FalseClear", "FalseBoundary"):
        args = ["-o", name + ".olean", name + ".lean"] if name == "Accumulation" else [name + ".lean"]
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
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({"claims": 5, "false_controls_rejected": 2,
    "scratch_removed": True, "canonical_coverage_increment": 0,
    "source_sha256": hashlib.sha256((HERE / "Accumulation.lean").read_bytes()).hexdigest(),
    "commands": records}, indent=2) + "\n")
print("Five accumulation claims checked; two false controls rejected; scratch removed")
