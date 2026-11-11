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
RESEARCH = ROOT / "research/derivation/document"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore_imports(data, inverse):
    return "".join("import " + inverse.get(line[7:].strip(), line[7:].strip()) + "\n"
                   if line.startswith("import ") else line
                   for line in data.decode().splitlines(keepends=True)).encode()


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
    original = json.loads((RESEARCH / "origin/SOURCE-ONLY.json").read_text())
    records = transport["records"]
    if {r["source"]: r["source_sha256"] for r in records} != original:
        raise ValueError("Transport does not cover the exact accepted source roster")
    inverse = {new: old for old, new in transport["module_map"].items()}
    if len(inverse) != len(transport["module_map"]):
        raise ValueError("Noninjective module relocation")
    legacy = load_helper(ROOT / "derivation_check.py", "installed_derivation_check")
    facade = legacy.facade_sources(ROOT)
    if any("/Tools/" in name or "/Tests/" in name for name in facade):
        raise ValueError("CLI or tests entered the public facade")
    inputs, restored = {}, {}
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
    for name in facade + ["document_check.py", "derivation_check.py", "lakefile.lean", "lean-toolchain",
                         "research/derivation/FACADE.json", "research/derivation/document/TRANSPORT.json",
                         "research/derivation/document/origin/SOURCE-ONLY.json",
                         "research/derivation/document/origin/REVIEW-REPORT.md"]:
        inputs[name] = digest((ROOT / name).read_bytes())
    commands = {}

    def run(label, argv, work):
        p = subprocess.run([str(x) for x in argv], cwd=work,
                           env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE="1"),
                           capture_output=True, text=True)
        output = p.stdout + p.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"exit": p.returncode, "sha256": digest(output.encode())}
        if p.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError(label + "\n" + output)
        return output

    with tempfile.TemporaryDirectory(prefix="installed-document-", dir=out) as directory:
        temp = Path(directory)
        accepted = temp / "accepted"
        accepted.mkdir()
        for name, data in restored.items():
            target = accepted / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (accepted / "SOURCE-ONLY.json").write_text(json.dumps(original, indent=2) + "\n")
        run("accepted-regression", [sys.executable, "-B", accepted / "check.py", "--lean", lean,
                                    "--out", out / "accepted-regression"], accepted)
        helper = load_helper(accepted / "check.py", "accepted_document_check")
        preserved = json.loads((accepted / "PRESERVED.json").read_text())
        originals = preserved["canonical_modules"] + ["Model.lean", "Prototype.lean"] + [n + ".lean" for n in helper.OWN]
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
        if len(review_names) != 4:
            raise ValueError("Independent review theorem roster changed")
        for name in modules + [review["installed"]]:
            run("build-" + name.replace("/", "-"), [lean, "-o", name[:-5] + ".olean", name], work)
            names += helper.declarations(work / name)
        compiled = set(modules + [review["installed"]])
        for name in facade:
            if name not in compiled:
                run("facade-" + name.replace("/", "-"), [lean, "-o", name[:-5] + ".olean", name], work)
        (work / "Audit.lean").write_text("import CssDerivation.Tests.DocumentCases\n"
                                        "import CssDerivation.Tests.DocumentBoundary\n" +
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
        for name, profile in regression["runtime_profiles"].items():
            rows = profile["rows"]
            output = run("runtime-" + name, [lean, "--run", mapped["Runner.lean"], profile["profile"],
                         accepted / (name + ".json")] + [row["input"] for row in rows], work)
            if [json.loads(line) for line in output.splitlines()] != rows:
                raise ValueError("Relocated actual-file execution changed")
        run("lake-target", [lean.parent / "lake", "build", "CssDerivation"], work)
        controls = {}
        dependency = "CssDerivation/FirstOrder/Weakening.lean"
        original_data = (work / dependency).read_bytes()
        registry_path = work / "research/derivation/FACADE.json"
        original_registry = registry_path.read_bytes()
        facade_data = (work / "CssDerivation.lean").read_bytes()
        for label in ["missing-dependency", "changed-dependency", "unsupported-import", "extra-registry-entry"]:
            if label == "missing-dependency":
                (work / dependency).unlink()
                expected = "Missing facade dependency: " + dependency
            elif label == "changed-dependency":
                (work / dependency).write_bytes(original_data + b"\n")
                expected = "Changed or unregistered facade dependency: " + dependency
            elif label == "unsupported-import":
                bad = facade_data + b"import CssDerivation.FirstOrder CssDerivation.Lowering\n"
                (work / "CssDerivation.lean").write_bytes(bad)
                registry = json.loads(original_registry)
                registry["CssDerivation.lean"] = digest(bad)
                registry_path.write_text(json.dumps(registry))
                expected = "Unsupported facade import form: CssDerivation.lean: import CssDerivation.FirstOrder CssDerivation.Lowering"
            else:
                registry = json.loads(original_registry)
                registry["CssDerivation/Unreachable.lean"] = "0" * 64
                registry_path.write_text(json.dumps(registry))
                expected = "Facade registry is not the exact dependency closure"
            try:
                legacy.facade_sources(work)
            except ValueError as error:
                if str(error) != expected:
                    raise
                controls[label] = expected
            else:
                raise ValueError("Facade control did not reject: " + label)
            (work / dependency).write_bytes(original_data)
            (work / "CssDerivation.lean").write_bytes(facade_data)
            registry_path.write_bytes(original_registry)
        if legacy.facade_sources(work) != facade:
            raise ValueError("Facade was not restored after controls")
    if inputs != {name: digest((ROOT / name).read_bytes()) for name in inputs}:
        raise ValueError("Sources changed during verification")
    report = {"status": "pass", "source_sha256": inputs, "declaration_axioms": audits,
              "accepted_declaration_count": len(regression["audits"]),
              "transferred_review_declarations": review_names,
              "facade_sources": {name: inputs[name] for name in facade},
              "facade_controls": controls, "accepted_controls": regression["controls"],
              "runtime_profiles": regression["runtime_profiles"], "commands": commands,
              "import_only_lean_transport": True, "checker_adjustment_is_new_code": True,
              "temporary_builds_removed": True, "default_css_target_built": False,
              "css_feature_coverage_added": False, "json_text_parser_proved": False,
              "arbitrary_alias_document_converse": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} relocated audits ({len(review_names)} transferred review), "
          f"{len(facade)} facade sources, {len(controls)} facade controls, and actual-file/Lake checks")


if __name__ == "__main__":
    main()
