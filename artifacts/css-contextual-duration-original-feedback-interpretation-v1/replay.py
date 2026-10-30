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
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(LEAN) == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
assert len(sys.argv) == 2 and Path(sys.argv[1]).name == sys.argv[1]
output = HERE / sys.argv[1]
output.mkdir()
names = re.findall(r"^theorem (\w+)", (HERE / "ObservedBoundary.lean").read_text(), re.M)
false_cases = {
    "ObservedIsCycleEntry": "observed = low",
}
records = []
(output / "TOOLCHAIN.txt").write_bytes(subprocess.check_output([str(LEAN), "--version"]))
with tempfile.TemporaryDirectory(prefix="css-duration-observed-boundary-") as temporary:
    scratch = Path(temporary)
    (output / "SCRATCH.json").write_text(json.dumps({"path": str(scratch)}) + "\n")
    env = dict(os.environ, LEAN_PATH=str(scratch))
    prior = ROOT / "artifacts/css-contextual-duration-scheduling-model-v1"
    assert sha(prior / "FILES.json") == "2bbd795ad374783462a6485207fc760b98a9d2fe7094897f0d43c27af91cb9b2"
    assert sha(prior / "DurationScheduling.lean") == "605539072ca03005853091551ce23022e2ecfa1c192087328e112d11382dce6d"
    shutil.copyfile(prior / "DurationScheduling.lean", scratch / "DurationScheduling.lean")
    feedback = ROOT / "artifacts/css-contextual-duration-feedback-model-v1"
    assert sha(feedback / "FILES.json") == "d743accb467060a7d0d0b79608cce3634797ab1e9aabd15ca61d5a43be5c4ec7"
    assert sha(feedback / "DurationFeedback.lean") == "d0cd6119efb786c6f6c247e84bd9307a962bff4aff88445554afdf1fc6585f50"
    shutil.copyfile(feedback / "DurationFeedback.lean", scratch / "DurationFeedback.lean")
    shutil.copyfile(HERE / "ObservedBoundary.lean", scratch / "ObservedBoundary.lean")
    shutil.copyfile(HERE / "ObservedBoundary.lean", output / "ObservedBoundary.lean")
    (scratch / "Audit.lean").write_text("import ObservedBoundary\n" + "".join(
        "#print axioms ObservedBoundary." + name + "\n" for name in names))
    for name, claim in false_cases.items():
        (scratch / (name + ".lean")).write_text(
            "import ObservedBoundary\nopen ObservedBoundary DurationFeedback\nexample : " + claim + " := by decide\n")
    for source in scratch.glob("*.lean"):
        shutil.copyfile(source, output / source.name)
    for name, expected in [("DurationScheduling", True), ("DurationFeedback", True), ("ObservedBoundary", True), ("Audit", True)] + [(n, False) for n in false_cases]:
        result = subprocess.run([str(LEAN), "-o", name + ".olean", name + ".lean"],
                                cwd=scratch, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=60)
        (output / (name + ".log")).write_bytes(result.stdout)
        records.append({"module": name, "command": [str(LEAN), "-o", name + ".olean", name + ".lean"], "exit": result.returncode, "expected_success": expected})
        (output / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
        assert (result.returncode == 0) == expected, name
        if not expected:
            assert b"Tactic `decide` proved that the proposition" in result.stdout
            assert b"is false" in result.stdout
    audit = (output / "Audit.log").read_text()
    assert audit.count("depends on axioms:") + audit.count("does not depend on any axioms") == len(names)
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    axioms = {n.strip() for group in re.findall(r"axioms: \[(.*?)\]", audit)
              for n in group.split(",") if n.strip()}
    assert axioms <= {"propext", "Quot.sound", "Classical.choice"}
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({
    "success": True, "audited_theorems": names, "false_controls_rejected": len(false_cases),
    "source_sha256": sha(HERE / "ObservedBoundary.lean"), "lean_sha256": sha(LEAN),
    "scratch_removed": True, "canonical_coverage_increment": 0,
    "native_refinement_proved": False, "native_scheduling_refinement_proved": False,
}, indent=2, sort_keys=True) + "\n")
print(f"{len(names)} theorems audited; {len(false_cases)} false controls rejected")
