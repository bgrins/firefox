#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
LEAN_SHA = "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
DESIGN_SEAL = "497c6e57a81acfa51468a4ed4c00046c32bbda5e77a380a7dbeca0799ed189a2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    frozen = json.loads((ROOT / "FREEZE.json").read_text())
    assert sha(ROOT / "INPUTS.json") == frozen["inputs_sha256"]
    for name, expected in json.loads((ROOT / "INPUTS.json").read_text()).items():
        assert sha(ROOT / name) == expected, name
    assert sha(ROOT / "source/FREEZE.json") == DESIGN_SEAL
    design = json.loads((ROOT / "source/FREEZE.json").read_text())
    assert sha(ROOT / "source/INPUTS.json") == design["inputs_sha256"]
    inputs = json.loads((ROOT / "source/INPUTS.json").read_text())
    for path in (ROOT / "source").rglob("*.rs"):
        assert sha(path) == inputs[str(path.relative_to(ROOT / "source"))]
    assert sha(ROOT / "source/DESIGN.md") == inputs["DESIGN.md"]
    for path in ROOT.glob("*.lean"):
        assert not re.search(r"\b(sorry|admit|axiom|native_decide)\b", path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify()
    lean = args.lean.resolve()
    assert sha(lean) == LEAN_SHA
    output = args.output.resolve()
    assert not output.exists()
    output.mkdir(parents=True)
    manifest = json.loads((ROOT / "MODULES.json").read_text())
    modules = manifest["order"]
    logs = []
    mutations = []
    with tempfile.TemporaryDirectory(prefix="resolved-summary-lean-") as tmp:
        work = Path(tmp)
        env = dict(os.environ, LEAN_PATH=str(work))
        for source in ROOT.glob("*.lean"):
            shutil.copyfile(source, work / source.name)
        for module in modules:
            result = subprocess.run([str(lean), "-o", module + ".olean", module + ".lean"],
                                    cwd=work, env=env, text=True, capture_output=True)
            (output / (module + ".log")).write_text(result.stdout + result.stderr)
            assert result.returncode == 0, (module, result.stdout, result.stderr)
            logs.append(dict(module=module, exit_code=result.returncode))
        audit = (output / "Audit.log").read_text()
        found = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$", audit, re.M)
        assert [name for name, _ in found] == manifest["audits"]
        for name, axioms in found:
            assert set(filter(None, axioms.split(", "))) <= {"propext", "Quot.sound"}, (name, axioms)
        for mutation in json.loads((ROOT / "MUTATIONS.json").read_text()):
            module = mutation["module"]
            original = (ROOT / (module + ".lean")).read_text()
            assert original.count(mutation["old"]) == 1
            altered = original.replace(mutation["old"], mutation["new"])
            (work / (module + ".lean")).write_text(altered)
            result = subprocess.run([str(lean), module + ".lean"], cwd=work, env=env,
                                    text=True, capture_output=True)
            (output / (mutation["name"] + ".log")).write_text(result.stdout + result.stderr)
            assert result.returncode != 0 and "error:" in result.stdout + result.stderr, mutation["name"]
            mutations.append(dict(name=mutation["name"], exit_code=result.returncode,
                                  altered_source_sha256=hashlib.sha256(altered.encode()).hexdigest()))
            (work / (module + ".lean")).write_text(original)
    result = dict(status="PASS", modules=logs, audited_declarations=len(manifest["audits"]),
                  allowed_axioms=["propext", "Quot.sound"], mutations=mutations,
                  native_tokenizer_admission="OPEN", serialization_bridge="CONDITIONAL",
                  native_scanner="NOT IMPLEMENTED", scc_correctness="OPEN")
    (output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
