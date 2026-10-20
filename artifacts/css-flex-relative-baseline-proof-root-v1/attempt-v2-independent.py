import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "css-flex-relative-baseline-proof-v1"
config = json.loads((SOURCE / "TOOLCHAIN.json").read_text())
lean = Path(config["lean"])
assert hashlib.sha256(lean.read_bytes()).hexdigest() == config["lean_sha256"]
env = {k: v for k, v in os.environ.items() if not k.startswith(("LEAN_", "PYTHON"))}
env["LEAN_PATH"] = str(ROOT / "replay/proof")
commands = []


def run(path):
    command = [str(lean), str(path)]
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    record = {"command": command, "exit": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    commands.append(record)
    (ROOT / "INDEPENDENT-COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
    return result


positive = run(ROOT / "Independent.lean")
assert positive.returncode == 0 and not positive.stderr, positive.stdout + positive.stderr
audits = re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", positive.stdout)
assert len(audits) == 8
assert all({a.strip() for a in axioms.split(",")} <= {"", "propext", "Quot.sound", "Classical.choice"}
           for _, _, axioms in audits)
claims = {
    "missing-property-is-ready": "PropertyReady exampleFrame",
    "stale-property-matches-reference": "correctedDistance false .horizontal ⟨160,80⟩ { exampleFrame with normalProperty := some ⟨0,100⟩ } = referenceDistance false .horizontal ⟨160,80⟩ exampleFrame",
    "normal-property-prevents-sentinel": "correctedDistance false .verticalRL ⟨0,80⟩ { exampleFrame with actual := ⟨0,0⟩, expectedNormal := ⟨0,0⟩, size := ⟨1073741823,50⟩, firstAscent := 0 } ≠ unset",
}
for name, claim in claims.items():
    path = ROOT / (name + ".lean")
    path.write_text("import RelativeBaseline\nopen FlexRelativeBaseline\nexample : " + claim + " := by\n  unfold PropertyReady\n  decide +kernel\n" if name == "missing-property-is-ready" else
                    "import RelativeBaseline\nopen FlexRelativeBaseline\nexample : " + claim + " := by decide +kernel\n")
    result = run(path)
    assert result.returncode != 0 and "error:" in result.stdout and "proposition" in result.stdout, result.stdout
(ROOT / "INDEPENDENT.json").write_text(json.dumps({
    "accepted": True, "kernel_audits": [name for name, _, _ in audits],
    "rejected_false_claims": list(claims),
    "scope": "Independent conditional projection/selection/readiness checks; no normal-property lifecycle or browser reachability of sentinel witness."
}, indent=2) + "\n")
print("PASS: eight independent kernel checks and three rejected false claims")
