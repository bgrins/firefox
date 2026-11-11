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
RESEARCH = ROOT / "research/derivation/number"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore_imports(data, inverse):
    return "".join("import " + inverse.get(line[7:].strip(), line[7:].strip()) + "\n"
        if line.startswith("import ") else line for line in data.decode().splitlines(keepends=True)).encode()


def load_helper(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    transport = json.loads((RESEARCH / "TRANSPORT.json").read_text())
    original_bytes = (RESEARCH / "origin/SOURCE-ONLY.json").read_bytes()
    original = json.loads(original_bytes)
    if digest(original_bytes) != transport["source_manifest_sha256"]:
        raise ValueError("Accepted manifest changed")
    records = transport["records"]
    if {r["source"]: r["source_sha256"] for r in records} != original:
        raise ValueError("Transport does not cover the exact accepted source roster")
    inverse = {new: old for old, new in transport["module_map"].items()}
    if len(inverse) != len(transport["module_map"]):
        raise ValueError("Noninjective module relocation")
    compatibility = json.loads((RESEARCH / "COMPATIBILITY.json").read_text())
    for name, expected in compatibility.items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise ValueError("Earlier API/input changed: " + name)
    legacy = load_helper(ROOT / "derivation_check.py", "installed_derivation_check")
    facade = legacy.facade_sources(ROOT)
    if any("/Tools/" in name or "/Tests/" in name for name in facade):
        raise ValueError("CLI or tests entered the public facade")
    inputs, restored = dict(compatibility), {}
    for record in records:
        data = (ROOT / record["installed"]).read_bytes()
        inputs[record["installed"]] = digest(data)
        if digest(data) != record["installed_sha256"]:
            raise ValueError("Installed source changed: " + record["installed"])
        raw = restore_imports(data, inverse) if record["installed"].endswith(".lean") else data
        if digest(raw) != record["source_sha256"]:
            raise ValueError("Relocation changed more than imports: " + record["installed"])
        restored[record["source"]] = raw
    review = transport["review_boundary"]
    review_data = (ROOT / review["installed"]).read_bytes()
    if digest(review_data) != review["installed_sha256"] or digest(restore_imports(review_data, inverse)) != review["source_sha256"]:
        raise ValueError("Independent review source transport changed")
    inputs[review["installed"]] = digest(review_data)
    if digest((RESEARCH / "origin/REVIEW-REPORT.md").read_bytes()) != review["report_sha256"]:
        raise ValueError("Independent review attribution changed")
    for name in facade + ["number_check.py", "derivation_check.py", "document_check.py", "lakefile.lean", "lean-toolchain",
        "research/derivation/FACADE.json", "research/derivation/number/TRANSPORT.json",
        "research/derivation/number/COMPATIBILITY.json", "research/derivation/number/origin/SOURCE-ONLY.json",
        "research/derivation/number/origin/REVIEW-REPORT.md"]:
        inputs[name] = digest((ROOT / name).read_bytes())
    commands = {}

    def run(label, argv, work):
        result = subprocess.run([str(x) for x in argv], cwd=work,
            env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE="1"), capture_output=True, text=True)
        output = result.stdout + result.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"exit": result.returncode, "sha256": digest(output.encode())}
        if result.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError(label + "\n" + output)
        return output

    with tempfile.TemporaryDirectory(prefix="installed-number-", dir=out) as directory:
        temp = Path(directory)
        accepted = temp / "accepted"
        accepted.mkdir()
        for name, data in restored.items():
            target = accepted / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (accepted / "SOURCE-ONLY.json").write_bytes(original_bytes)
        run("accepted-regression", [sys.executable, "-B", accepted / "check.py", "--lean", lean,
            "--out", out / "accepted-regression"], accepted)
        helper = load_helper(accepted / "check.py", "accepted_number_check")
        preserved = json.loads((accepted / "PRESERVED.json").read_text())
        originals = preserved["modules"] + [n + ".lean" for n in helper.OWN]
        mapped = {r["source"]: r["installed"] for r in records}
        modules = [mapped[n] for n in originals]
        work = temp / "relocated"
        work.mkdir()
        for name in modules + [review["installed"], "lakefile.lean", "lean-toolchain",
            "research/derivation/FACADE.json"] + facade:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        names, review_names = [], helper.declarations(work / review["installed"])
        if review_names != review["theorems"]:
            raise ValueError("Independent review theorem roster changed")
        for name in modules + [review["installed"]]:
            run("build-" + name.replace("/", "-"), [lean, "-o", name[:-5] + ".olean", name], work)
            names += helper.declarations(work / name)
        compiled = set(modules + [review["installed"]])
        for name in facade:
            if name not in compiled:
                run("facade-" + name.replace("/", "-"), [lean, "-o", name[:-5] + ".olean", name], work)
        (work / "Audit.lean").write_text("import CssDerivation.Tests.NumberDocumentCases\n"
            "import CssDerivation.Tests.NumberDocumentBoundary\n" +
            "".join("#print axioms " + n + "\n" for n in names))
        output = run("axioms", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError("Unexpected axiom record: " + line)
            axioms = set(match[3].split(", ")) if match[3] else set()
            if not axioms <= {"propext", "Classical.choice", "Quot.sound"} or match[1] in audits:
                raise ValueError("Invalid axiom inventory")
            audits[match[1]] = sorted(axioms)
        regression = json.loads((out / "accepted-regression/report.json").read_text())
        if len(names) != len(set(names)) or set(audits) != set(names):
            raise ValueError("Incomplete relocated axiom inventory")
        if {n: a for n, a in audits.items() if n not in review_names} != regression["audits"]:
            raise ValueError("Relocation altered accepted theorem axioms")
        for name, rows in regression["runtime"].items():
            output = run("runtime-" + name, [lean, "--run", mapped["Runner.lean"], accepted / (name + ".json")], work)
            if [json.loads(line) for line in output.splitlines()] != rows:
                raise ValueError("Relocated actual-file execution changed")
        run("lake-target", [lean.parent / "lake", "build", "CssDerivation"], work)
        controls = {}
        dependency = "CssDerivation/Parser/Syntax.lean"
        original_data = (work / dependency).read_bytes()
        for label in ["missing-parser-dependency", "changed-parser-dependency"]:
            if label == "missing-parser-dependency":
                (work / dependency).unlink()
                expected = "Missing facade dependency: " + dependency
            else:
                (work / dependency).write_bytes(original_data + b"\n")
                expected = "Changed or unregistered facade dependency: " + dependency
            try:
                legacy.facade_sources(work)
            except ValueError as error:
                if str(error) != expected: raise
                controls[label] = expected
            else:
                raise ValueError("Facade control did not reject: " + label)
            (work / dependency).write_bytes(original_data)
    if any(digest((ROOT / name).read_bytes()) != expected for name, expected in inputs.items()):
        raise ValueError("Installed input changed during replay")
    report = {"status": "pass", "installed_inputs": inputs, "commands": commands, "audits": audits,
        "review_theorems": review_names, "review_credit": review["report_sha256"],
        "accepted_audits": len(regression["audits"]), "transferred_review_audits": len(review_names),
        "runtime_rows": sum(map(len, regression["runtime"].values())), "facade_sources": facade,
        "registration_controls": controls, "compatibility_inputs": compatibility,
        "earlier_semantic_suites_repeated": False, "default_css_target_built": False,
        "temporary_builds_removed": True}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} relocated audits ({len(regression['audits'])} accepted + "
        f"{len(review_names)} transferred review), {report['runtime_rows']} installed rows, "
        f"{len(facade)} facade sources, fresh opt-in Lake build")


if __name__ == "__main__":
    main()
