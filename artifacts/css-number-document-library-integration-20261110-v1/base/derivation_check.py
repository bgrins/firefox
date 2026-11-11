import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
RESEARCH = ROOT / "research/derivation"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore_imports(data, inverse):
    return "".join(
        "import " + inverse.get(line[7:].strip(), line[7:].strip()) + "\n"
        if line.startswith("import ") else line
        for line in data.decode().splitlines(keepends=True)
    ).encode()


def facade_sources(root):
    expected = json.loads((root / "research/derivation/FACADE.json").read_text())
    visiting, visited, ordered = set(), set(), []

    def visit(module):
        name = module.replace(".", "/") + ".lean"
        if module in visiting:
            raise ValueError("Cyclic facade dependency: " + module)
        if module in visited:
            return
        path = root / name
        if not path.is_file():
            raise ValueError("Missing facade dependency: " + name)
        data = path.read_bytes()
        if name not in expected or digest(data) != expected[name]:
            raise ValueError("Changed or unregistered facade dependency: " + name)
        visiting.add(module)
        for raw in data.decode().splitlines():
            line = raw.strip()
            if line.startswith("--"):
                continue
            if re.search(r"\bimport\b", line):
                match = re.fullmatch(r"import ([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)", line)
                if not match:
                    raise ValueError("Unsupported facade import form: " + name + ": " + line)
                dependency = match[1]
                prefix = dependency.split(".")[0]
                if prefix in {"CssDerivation", "CssSemantics"}:
                    visit(dependency)
                elif prefix not in {"Lean", "Init", "Std"}:
                    raise ValueError("Unsupported facade import module: " + dependency)
            elif line == "prelude" or line == "module" or line.startswith("module "):
                raise ValueError("Unsupported facade module header: " + name)
        visiting.remove(module)
        visited.add(module)
        ordered.append(name)

    visit("CssDerivation")
    if set(ordered) != set(expected):
        raise ValueError("Facade registry is not the exact dependency closure")
    return ordered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    transport = json.loads((RESEARCH / "TRANSPORT.json").read_text())
    original = json.loads((RESEARCH / "origin/SOURCE-ONLY.json").read_text())
    records = transport["records"]
    if {r["source"]: r["source_sha256"] for r in records} != original:
        raise ValueError("Transport does not cover exact accepted source roster")
    inverse = {new: old for old, new in transport["module_map"].items()}
    if len(inverse) != len(transport["module_map"]):
        raise ValueError("Noninjective module relocation")
    facade = facade_sources(ROOT)
    inputs = {}
    restored = {}
    for record in records:
        name = record["installed"]
        data = (ROOT / name).read_bytes()
        inputs[name] = digest(data)
        if inputs[name] != record["installed_sha256"]:
            raise ValueError("Installed source changed: " + name)
        raw = restore_imports(data, inverse) if name.endswith(".lean") else data
        if digest(raw) != record["source_sha256"]:
            raise ValueError("Relocation changed more than module imports: " + name)
        restored[record["source"]] = raw
    for name in ["derivation_check.py", "CssDerivation.lean", "lakefile.lean", "lean-toolchain",
                 "research/derivation/TRANSPORT.json", "research/derivation/origin/SOURCE-ONLY.json",
                 "research/derivation/FACADE.json"] + facade:
        inputs[name] = digest((ROOT / name).read_bytes())
    commands = {}

    def run(label, argv, work):
        process = subprocess.run([str(x) for x in argv], cwd=work,
                                 env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE="1"),
                                 capture_output=True, text=True)
        output = process.stdout + process.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"exit": process.returncode, "sha256": digest(output.encode())}
        if process.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError("Unexpected result: " + label + "\n" + output)
        return output

    with tempfile.TemporaryDirectory(prefix="css-derivation-", dir=out) as directory:
        temp = Path(directory)
        accepted = temp / "accepted"
        accepted.mkdir()
        for name, data in restored.items():
            destination = accepted / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        run("accepted-regression", [sys.executable, "-B", accepted / "check.py", "--lean", lean,
                                    "--out", out / "accepted-regression"], accepted)
        spec = importlib.util.spec_from_file_location("accepted_check", accepted / "check.py")
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        preserved = json.loads((accepted / "PRESERVED.json").read_text())
        old_modules = preserved["modules"] + helper.OWN
        modules = [transport["module_map"].get(m, m) for m in old_modules]
        work = temp / "relocated"
        work.mkdir()
        for name in [r["installed"] for r in records if r["installed"].endswith(".lean")] + [
                "CssDerivation.lean", "lakefile.lean", "lean-toolchain"] + facade:
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        names = []
        for module in modules:
            path = module.replace(".", "/")
            run("build-" + module, [lean, "-o", path + ".olean", path + ".lean"], work)
            names += helper.declarations(work / (path + ".lean"))
        compiled = {m.replace(".", "/") + ".lean" for m in modules}
        for name in facade:
            if name not in compiled:
                run("build-facade-" + name.replace("/", "-"), [lean, "-o", name[:-5] + ".olean", name], work)
        (work / "Audit.lean").write_text("import CssDerivation.Tests.JsonCases\n" + "".join(
            "#print axioms " + name + "\n" for name in names))
        output = run("axioms", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError("Unexpected axiom record: " + line)
            axioms = set(match[3].split(", ")) if match[3] else set()
            if not axioms <= {"propext", "Classical.choice", "Quot.sound"} or match[1] in audits:
                raise ValueError("Bad axiom dependency record")
            audits[match[1]] = sorted(axioms)
        regression = json.loads((out / "accepted-regression/report.json").read_text())
        if len(names) != len(set(names)) or set(audits) != set(names) or audits != regression["audits"]:
            raise ValueError("Relocation altered theorem inventory or axiom dependencies")
        expected = json.loads((accepted / "EXPECTED.json").read_text())
        for runner in ["Runner", "RoundtripRunner", "ReferenceRunner"]:
            path = transport["module_map"][runner].replace(".", "/") + ".lean"
            output = run(runner, [lean, "--run", path, accepted / "escape.json"] +
                         [row["input"] for row in expected], work)
            if [json.loads(line) for line in output.splitlines()] != expected:
                raise ValueError("Relocated runner changed execution")
        run("lake-target", [lean.parent / "lake", "build", "CssDerivation"], work)
    if inputs != {name: digest((ROOT / name).read_bytes()) for name in inputs}:
        raise ValueError("Integration sources changed during verification")
    report = {"status": "pass", "source_sha256": inputs, "transported_inputs": len(records),
              "facade_sources": {name: inputs[name] for name in facade},
              "declaration_axioms": audits, "execution_rows_per_runner": len(expected),
              "semantic_controls": regression["controls"], "commands": commands,
              "import_only_transport_authenticated": True, "temporary_builds_removed": True,
              "css_feature_coverage_added": False, "json_text_parser_proved": False,
              "mechanical_prose_derivation": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} relocated audits, {len(expected)} rows per runner, "
          f"{len(regression['controls'])} accepted controls, and opt-in Lake target")


if __name__ == "__main__":
    main()
