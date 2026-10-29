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
output = HERE / sys.argv[1]
assert output.parent == HERE and not output.exists()
output.mkdir()
records = []
with tempfile.TemporaryDirectory(prefix="shadow-move-context-") as temporary:
    scratch = Path(temporary)
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    for name in ("Context", "Audit", "FalseFlag", "FalseOuterRoot"):
        args = ["-o", "Context.olean", "Context.lean"] if name == "Context" else [name + ".lean"]
        result = subprocess.run([str(LEAN), *args], cwd=scratch,
            env=dict(os.environ, LEAN_PATH=str(scratch)), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=30)
        (output / (name + ".log")).write_bytes(result.stdout)
        records.append({"name": name, "exit": result.returncode})
        assert (result.returncode == 0) == (not name.startswith("False")), name
        if name.startswith("False"):
            assert b"Tactic `decide` proved that the proposition" in result.stdout and b"is false" in result.stdout
    audit = (output / "Audit.log").read_text()
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    assert audit.count("ShadowMove.") == 8
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({"claims": 8, "false_controls_rejected": 2,
    "scratch_removed": True, "canonical_coverage_increment": 0,
    "source_sha256": hashlib.sha256((HERE / "Context.lean").read_bytes()).hexdigest(),
    "commands": records}, indent=2) + "\n")
print("Eight claims checked, two false controls rejected, scratch removed")
