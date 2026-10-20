import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--lean", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
lean = args.lean.resolve(strict=True)
expected_lean = "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if sha(lean) != expected_lean:
    raise RuntimeError("Unexpected Lean executable")
args.output.mkdir(parents=True, exist_ok=False)
roster = json.loads((HERE / "AUDIT-ROSTER.json").read_text())
modules = ["MaskedSticky", "StickyComposition"]
names = []
inputs = {}
for module in modules:
    source = HERE / "lean" / (module + ".lean")
    inputs[module] = sha(source)
    names.extend(module + "." + name for name in re.findall(r"^theorem (\w+)", source.read_text(), re.M))
if names != roster["declarations"] or len(names) != len(set(names)):
    raise RuntimeError("Theorem roster differs")
allowed = {"propext", "Classical.choice", "Quot.sound"}
if set(roster["allowed_axioms"]) != allowed:
    raise RuntimeError("Unexpected axiom policy")
commands = []
with tempfile.TemporaryDirectory(prefix="sticky-lean-") as temporary:
    work = Path(temporary)
    env = {k: v for k, v in os.environ.items() if not k.startswith("LEAN_")}
    env["LEAN_PATH"] = str(work)
    for module in modules:
        (work / (module + ".lean")).write_bytes((HERE / "lean" / (module + ".lean")).read_bytes())
    (work / "Audit.lean").write_text("import StickyComposition\n" + "\n".join("#print axioms " + n for n in names) + "\n")
    for module in modules + ["Audit"]:
        command = [str(lean), "-o", str(work / (module + ".olean")), str(work / (module + ".lean"))]
        with (args.output / (module + ".log")).open("w") as log:
            result = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
        commands.append({"module": module, "command": command, "exit": result.returncode})
        if result.returncode:
            (args.output / "FAILED.json").write_text(json.dumps(commands, indent=2) + "\n")
            raise RuntimeError("Lean failed: " + module)
    entries = {}
    audit = (args.output / "Audit.log").read_text()
    for line in audit.splitlines():
        match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
        if match:
            name, content = match.groups()
            axioms = [] if not content else content.split(", ")
        else:
            match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
            if not match:
                raise RuntimeError("Unexpected audit output: " + line)
            name, axioms = match.group(1), []
        if name in entries or not set(axioms) <= allowed:
            raise RuntimeError("Duplicate declaration or unsupported axiom")
        entries[name] = axioms
    if list(entries) != names:
        raise RuntimeError("Incomplete axiom audit")
for module in modules:
    if sha(HERE / "lean" / (module + ".lean")) != inputs[module]:
        raise RuntimeError("Source changed during compilation")
receipt = {
    "status": "LEAN_MODEL_CHECKPOINT_ONLY",
    "source_sha256": inputs,
    "lean_sha256": expected_lean,
    "commands": commands,
    "audits": entries,
    "temporary_compiler_products_removed": True,
    "scope": "Kernel-checked model theorems. Native source bridge, calibration and independent review are separate required gates.",
    "trust": "The selected Lean executable, its installed toolchain libraries, kernel and operating environment are trusted.",
}
(args.output / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"status": receipt["status"], "audits": len(entries), "compiler_products_removed": True}))
