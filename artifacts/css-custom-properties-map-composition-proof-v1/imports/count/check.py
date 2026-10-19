#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
LEAN_SHA = "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lean", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    freeze = json.loads((ROOT / "FREEZE.json").read_text())
    assert sha(ROOT / "MANIFEST.json") == freeze["manifest_sha256"], "manifest authentication"
    for relative, digest in manifest["files"].items():
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT), "escaping input"
        assert sha(path) == digest, "input authentication: " + relative
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()}
    assert actual == set(manifest["files"]) | {"MANIFEST.json", "FREEZE.json"}, "closed input roster"
    lean = args.lean.resolve()
    assert sha(lean) == LEAN_SHA, "Lean executable identity"
    out = args.output.resolve()
    assert not out.exists(), "output must be new"
    out.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("LEAN_")}
    env["LEAN_PATH"] = str(out)
    commands = []
    def run(arguments, label, expected=0, cwd=out):
        result = subprocess.run([str(lean), *arguments], cwd=cwd, env=env,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out / (label + ".log")).write_text(result.stdout)
        commands.append({"label": label, "returncode": result.returncode})
        assert (result.returncode == 0) == (expected == 0), label + " unexpected exit"
        if expected != 0:
            assert "Tactic `decide` proved that the proposition" in result.stdout, label + " nonsemantic rejection"
            assert "is false" in result.stdout, label + " missing false proposition"
        return result.stdout
    pins = json.loads((ROOT / "SOURCE-PINS.json").read_text())
    for variant, digest in pins["sha256"].items():
        assert sha(ROOT / "source" / (variant + ".rs")) == digest
    bindings = json.loads((ROOT / "BINDINGS.json").read_text())
    for record in bindings:
        source = (ROOT / "source" / (record["variant"] + ".rs")).read_text()
        start = source.index(record["signature"], source.index(record["owner"]))
        end = source.index("\n    }", start) + 6
        body = source[start:end] + "\n"
        assert body == (ROOT / record["path"]).read_text(), record["name"]
        assert hashlib.sha256(body.encode()).hexdigest() == record["sha256"]
    source = (ROOT / "source/count-only.rs").read_text()
    assert "match (self.get(name).is_some(), value.is_some())" in source
    assert "(false, true) => self.len += 1," in source
    assert "(true, false) => self.len -= 1," in source
    assert ".filter(|(_, value)| value.is_some())" in source
    assert "parent: None,\n        len: 0,\n        ancestor_count: 0," in source
    combined = (ROOT / "source/combined.rs").read_text()
    restored = combined.replace("'properties: loop {", "loop {").replace("continue 'properties;", "continue;")
    assert restored == source, "combined delta exceeds raw iterator labels"
    inventory = json.loads((ROOT / "AUDITS.json").read_text())
    names = []
    for module, expected in inventory.items():
        text = (ROOT / "lean" / (module + ".lean")).read_text()
        assert re.findall(r"^theorem\s+(\w+)", text, re.M) == expected
        assert not re.search(r"\b(sorry|admit|axiom|native_decide)\b", text)
        names.extend("LiveCount." + name for name in expected)
        shutil.copyfile(ROOT / "lean" / (module + ".lean"), out / (module + ".lean"))
        run(["-o", module + ".olean", module + ".lean"], module)
    audit = (ROOT / "lean/Audit.lean").read_text()
    assert re.findall(r"#print axioms (\S+)", audit) == names
    shutil.copyfile(ROOT / "lean/Audit.lean", out / "Audit.lean")
    log = run(["Audit.lean"], "axioms")
    observed = re.findall(r"'([^']+)' (?:depends on axioms:|does not depend on any axioms)", log)
    assert observed == names, "exact audit inventory"
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    for group in re.findall(r"depends on axioms: \[([^]]*)\]", log):
        assert set(x.strip() for x in group.split(",") if x.strip()) <= allowed
    mutation_rows = []
    for record in json.loads((ROOT / "MUTATIONS.json").read_text()):
        label = record["name"]
        folder = out / label
        folder.mkdir()
        for name in ["Baseline", "Mutant", "BaselineGate", "MutantGate"]:
            shutil.copyfile(ROOT / "mutants" / label / (name + ".lean"), folder / (name + ".lean"))
        previous = env["LEAN_PATH"]
        env["LEAN_PATH"] = str(folder) + os.pathsep + previous
        run(["-o", "Baseline.olean", "Baseline.lean"], label + "-baseline-definition", cwd=folder)
        run(["BaselineGate.lean"], label + "-baseline-gate", cwd=folder)
        run(["-o", "Mutant.olean", "Mutant.lean"], label + "-mutant-definition", cwd=folder)
        run(["MutantGate.lean"], label + "-mutant-gate", expected=1, cwd=folder)
        env["LEAN_PATH"] = previous
        mutation_rows.append({"name": label, "definition_compiled": True, "semantic_rejection": True})
    result = {"inputs": len(manifest["files"]), "modules": len(inventory),
              "audited_theorems": len(names), "source_bindings": len(bindings),
              "mutations": mutation_rows, "commands": commands,
              "native_build": "NOT_RUN", "raw_iterator_refinement": "CONDITIONAL"}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
