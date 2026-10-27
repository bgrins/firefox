#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inputs = json.loads((HERE / "INPUTS.json").read_text())
for name, expected in inputs["references"].items():
    path = ROOT / name
    assert digest(path) == expected, name
    if path.name == "FILES.json":
        manifest = json.loads(path.read_text())
        for child, value in manifest.get("files", manifest).items():
            assert digest(path.parent / child) == value, (name, child)
lean = ROOT / inputs["lean"]["path"]
assert digest(lean) == inputs["lean"]["sha256"]
source = HERE / "Rounding.lean"
before = digest(source)
names = re.findall(r"^theorem (\w+)", source.read_text(), re.M)
assert len(names) == len(set(names))
assert not re.search(r"\b(sorry|axiom|native_decide)\b", source.read_text())
start = time.monotonic()
with (HERE / "lean.log").open("w") as log:
    result = subprocess.run([str(lean), str(source)], cwd=ROOT,
                            stdout=log, stderr=subprocess.STDOUT, timeout=60)
elapsed = time.monotonic() - start
assert result.returncode == 0, "Lean failed; see lean.log"
assert digest(source) == before
lines = (HERE / "lean.log").read_text().splitlines()
assert len(lines) == len(names), "Unexpected compiler output"
audits = {}
for name, line in zip(names, lines):
    prefix = "'CSSOMRounding." + name + "' "
    assert line.startswith(prefix), (name, line)
    suffix = line[len(prefix):]
    if suffix == "does not depend on any axioms":
        axioms = []
    else:
        match = re.fullmatch(r"depends on axioms: \[(.*)\]", suffix)
        assert match, line
        axioms = match[1].split(", ")
        assert set(axioms) <= {"propext", "Classical.choice", "Quot.sound"}, line
    audits[name] = axioms
assert not any(HERE.rglob("*.olean"))
assert not any(HERE.rglob("*.ilean"))
receipt = {"source_sha256": before, "lean_sha256": digest(lean),
           "exit_code": result.returncode, "elapsed_seconds": elapsed,
           "log_sha256": digest(HERE / "lean.log"), "theorems": audits,
           "reference_payloads_authenticated": True,
           "no_generated_compiler_products": True}
(HERE / "CHECK.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"passed": len(audits), "source_sha256": before}))
