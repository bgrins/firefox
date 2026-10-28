import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
assert hashlib.sha256(LEAN.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
assert len(sys.argv) == 2, "replay.py ABSENT_OUTPUT_DIRECTORY"
output = Path(sys.argv[1]).resolve()
assert not output.exists()
output.mkdir()
names = ["Mapping", "Audit", "CloneRandom", "CloneTree", "GenericPercentage"]
results = {}
with tempfile.TemporaryDirectory(prefix="line-height-context-lean-", dir="/private/tmp") as folder:
    work = Path(folder)
    for name in names:
        shutil.copyfile(HERE / (name + ".lean"), work / (name + ".lean"))
    env = dict(os.environ, LEAN_PATH=str(work))
    for name in names:
        command = [str(LEAN), name + ".lean"]
        if name == "Mapping":
            command += ["-o", "Mapping.olean"]
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True)
        text = result.stdout + result.stderr
        (output / (name + ".log")).write_text(text)
        results[name] = {"exit": result.returncode, "log_sha256": hashlib.sha256(text.encode()).hexdigest()}
        if name in ("Mapping", "Audit"):
            assert result.returncode == 0, text
        else:
            assert result.returncode != 0 and "Tactic `decide`" in text and "is false" in text, text
    audit = (output / "Audit.log").read_text()
    assert audit.count("LineHeightContext.") == 6
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    for group in re.findall(r"depends on axioms: \[(.*?)\]", audit):
        assert set(group.split(", ")) <= {"propext", "Quot.sound"}
    scratch = str(work)
assert not Path(scratch).exists()
(output / "CHECK.json").write_text(json.dumps({
    "compiler_sha256": hashlib.sha256(LEAN.read_bytes()).hexdigest(),
    "source_sha256": {name + ".lean": hashlib.sha256((HERE / (name + ".lean")).read_bytes()).hexdigest() for name in names},
    "results": results, "declarations_audited": 6, "false_controls_rejected": 3,
    "scratch_removed": True, "native_refinement_claim": False,
}, indent=2) + "\n")
print(json.dumps(results))
