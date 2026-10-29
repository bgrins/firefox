import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(LEAN) == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
inputs = json.loads((HERE / "INPUTS.json").read_text())
for name, pin in inputs.items():
    assert sha(ROOT / name) == pin
output = HERE / sys.argv[1]
assert output.parent == HERE and not output.exists()
output.mkdir()
records = []
with tempfile.TemporaryDirectory(prefix="css-hypot-lean-") as temporary:
    scratch = Path(temporary)
    env = dict(os.environ, LEAN_PATH=str(scratch))
    modules = []
    for name in inputs:
        relative = Path(name).relative_to("artifacts/css-spec-lean")
        target = scratch / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        modules.append(relative.with_suffix("").as_posix())
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    cases = [(name, True) for name in modules + ["HypotScale", "Audit"]]
    cases += [(name, False) for name in ["TinyZero", "TinySquareRetained", "LargeSquareFinite",
                                        "PairFitsBinary32", "SquareFits24Bits"]]
    for name, expected in cases:
        args = [str(LEAN), "-o", name + ".olean", name + ".lean"]
        result = subprocess.run(args, cwd=scratch, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=60)
        (output / (Path(name).name + ".log")).write_bytes(result.stdout)
        records.append({"module": name, "exit": result.returncode, "expected_success": expected})
        (output / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
        assert (result.returncode == 0) == expected, name
        if not expected:
            assert b"Tactic `decide` proved that the proposition" in result.stdout
            assert b"is false" in result.stdout
    audit = (output / "Audit.log").read_text()
    assert audit.count("depends on axioms:") + audit.count("does not depend on any axioms") == 18
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    axioms = {name.strip() for group in re.findall(r"axioms: \[(.*?)\]", audit)
              for name in group.split(",") if name.strip()}
    assert axioms <= {"propext", "Quot.sound", "Classical.choice"}, axioms
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({
    "success": True, "audited_declarations": 18, "false_controls_rejected": 5,
    "source_sha256": sha(HERE / "HypotScale.lean"), "lean_sha256": sha(LEAN),
    "dependencies": inputs, "scratch_removed": True,
    "native_refinement_proved": False, "canonical_coverage_increment": 0
}, indent=2, sort_keys=True) + "\n")
print("18 declarations audited; five false controls rejected; scratch removed")
