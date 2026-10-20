import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "css-scroll-baseline-provider-proof-v2"
parser = argparse.ArgumentParser()
parser.add_argument("--proof-dir", type=Path, default=ROOT / "replay/proof")
parser.add_argument("--output", type=Path, default=ROOT)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
proof = args.proof_dir.resolve()
config = json.loads((SOURCE / "TOOLCHAIN.json").read_text())
lean = Path(config["lean"])
assert hashlib.sha256(lean.read_bytes()).hexdigest() == config["lean_sha256"]
env = {k: v for k, v in os.environ.items() if not k.startswith(("LEAN_", "PYTHON"))}
env["LEAN_PATH"] = str(proof)
commands = []
names = []
for name, count in [("ReviewedKernel", 12), ("Join", 5)]:
    command = [str(lean), "--root=" + str(ROOT), "-o", str(proof / (name + ".olean")), str(ROOT / (name + ".lean"))]
    result = subprocess.run(command, cwd=output, env=env, text=True, capture_output=True)
    commands.append({"command": command, "exit": result.returncode,
                     "stdout": result.stdout, "stderr": result.stderr})
    (output / "INDEPENDENT-COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
    assert result.returncode == 0 and not result.stderr, result.stdout + result.stderr
    audits = re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", result.stdout)
    assert len(audits) == count
    for declaration, _, axioms in audits:
        assert {a.strip() for a in axioms.split(",")} <= {"", "propext", "Quot.sound", "Classical.choice"}
        names.append(declaration)
(output / "INDEPENDENT.json").write_text(json.dumps({
    "accepted": True, "kernel_audits": names,
    "scope": "Fresh replay of twelve independent reviewer results and five root projection/dispatch boundary joins. Native geometry and provider lifecycle remain premises."
}, indent=2) + "\n")
print("PASS: twelve independent reviewer audits and five root joins")
