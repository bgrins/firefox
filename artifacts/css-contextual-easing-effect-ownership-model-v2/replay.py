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
BASE = ROOT / "artifacts/css-contextual-easing-dependency-cache-model-v1/Dependency.lean"
assert hashlib.sha256(LEAN.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
references = json.loads((HERE / "REFERENCES.json").read_text())
for name, digest in references.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
output = HERE / sys.argv[1]
assert output.parent == HERE and not output.exists()
output.mkdir()
records = []
with tempfile.TemporaryDirectory(prefix="easing-effect-v2-lean-") as temporary:
    scratch = Path(temporary)
    shutil.copyfile(BASE, scratch / "Dependency.lean")
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    env = dict(os.environ, LEAN_PATH=str(scratch))
    cases = [("Dependency", ["-o", "Dependency.olean", "Dependency.lean"], True),
             ("Ownership", ["-o", "Ownership.olean", "Ownership.lean"], True),
             ("Audit", ["Audit.lean"], True)]
    cases += [(name, [name + ".lean"], False) for name in
              ("FalseRefresh", "FalseRejected", "FalseTransition", "FalseRootContext")]
    for name, args, expected in cases:
        result = subprocess.run([str(LEAN), *args], cwd=scratch, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        (output / (name + ".log")).write_bytes(result.stdout)
        records.append({"name": name, "exit": result.returncode, "expected_success": expected})
        assert (result.returncode == 0) == expected, name
        if not expected:
            assert b"Tactic `decide` proved that the proposition" in result.stdout and b"is false" in result.stdout
    audit = (output / "Audit.log").read_text()
    assert audit.count("depends on axioms:") + audit.count("does not depend on any axioms") == 10
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({"success": True, "claims_audited": 10,
    "false_controls_rejected": 4, "scratch_removed": True, "canonical_coverage_increment": 0,
    "source_sha256": hashlib.sha256((HERE / "Ownership.lean").read_bytes()).hexdigest(),
    "lean_sha256": hashlib.sha256(LEAN.read_bytes()).hexdigest(), "commands": records}, indent=2) + "\n")
print("Ten correction/transfer declarations checked; four false controls rejected; scratch removed")
