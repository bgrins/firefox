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
with tempfile.TemporaryDirectory(prefix="easing-dependency-lean-") as temporary:
    scratch = Path(temporary)
    for source in HERE.glob("*.lean"):
        shutil.copyfile(source, scratch / source.name)
    env = dict(os.environ, LEAN_PATH=str(scratch))
    cases = [("Dependency", ["-o", "Dependency.olean", "Dependency.lean"], True),
             ("Audit", ["Audit.lean"], True)]
    cases += [(name, [name + ".lean"], False) for name in
              ("MissingSecond", "ParentOnly", "IndexOnly", "RefreshActive", "SameSupport")]
    for name, args, expected in cases:
        completed = subprocess.run([str(LEAN), *args], cwd=scratch, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        (output / (name + ".log")).write_bytes(completed.stdout)
        records.append({"name": name, "exit": completed.returncode,
                        "expected_success": expected})
        assert (completed.returncode == 0) == expected, name
        if not expected:
            assert b"Tactic `decide` proved that the proposition" in completed.stdout and b"is false" in completed.stdout, name
    audit = (output / "Audit.log").read_text()
    assert audit.count("depends on axioms:") + audit.count("does not depend on any axioms") == 12
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
assert not scratch.exists()
(output / "CHECK.json").write_text(json.dumps({
    "success": True, "claims_audited": 12, "false_controls_rejected": 5,
    "scratch_removed": True, "canonical_coverage_increment": 0,
    "source_sha256": hashlib.sha256((HERE / "Dependency.lean").read_bytes()).hexdigest(),
    "lean_sha256": hashlib.sha256(LEAN.read_bytes()).hexdigest(), "commands": records
}, indent=2) + "\n")
print("12 standalone declarations checked; five false controls rejected; scratch removed")
