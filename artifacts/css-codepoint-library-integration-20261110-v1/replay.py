#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULES = [
    "CssInput", "CssInputExamples", "CssCodePointInput", "CssCodePointInputLaws",
    "CssCodePointInputRefinement", "CssCodePointInputExamples",
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    library, lean, out = args.library.resolve(), args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    registration = json.loads((HERE / "REGISTRATION.json").read_text())
    spec = importlib.util.spec_from_file_location("canonical_check", library / "check.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    commands = {}
    inputs = [library / "check.py", library / "coverage.json", library / "tests/Audit.lean",
              library / "tests/RunExamples.lean", library / "CssSemantics.lean",
              library / "lean-toolchain"]
    inputs += sorted((library / "CssSemantics").rglob("*.lean"))

    def hashes():
        return {str(p.relative_to(library)): digest(p.read_bytes()) for p in inputs}

    before = hashes()

    def run(name, argv, cwd, success=True):
        env = dict(os.environ, LEAN_PATH=str(cwd), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([str(a) for a in argv], cwd=cwd, env=env,
                                capture_output=True, text=True)
        output = result.stdout + result.stderr
        (out / (name + ".log")).write_text(output)
        commands[name] = {"argv": [str(a) for a in argv], "exit": result.returncode,
                          "log_sha256": digest(output.encode())}
        if (result.returncode == 0) != success:
            raise RuntimeError(f"Unexpected exit for {name}: {result.returncode}\n{output}")
        if success and re.search(r"warning:|sorry|error:", output):
            raise RuntimeError(f"Unexpected diagnostic for {name}: {output}")
        if not success and "error:" not in output:
            raise RuntimeError(f"Missing Lean rejection diagnostic for {name}")
        return output

    version = run("toolchain", [lean, "--version"], out).strip()
    expected = (library / "lean-toolchain").read_text().strip().split(":v")[1]
    if f"version {expected}," not in version:
        raise RuntimeError("Unexpected Lean toolchain")
    run("coverage", [sys.executable, library / "check.py", "--coverage-only"], library)
    run("coverage-optimized", [sys.executable, "-O", library / "check.py", "--coverage-only"], library)
    expected_names, all_declarations = checker.validate_coverage()
    own = registration["theorems"]
    if not set(own) <= set(expected_names):
        raise RuntimeError("New theorem audit registrations missing")
    old = []
    for module in ["CssInput", "CssInputExamples"]:
        old += ["CssSemantics." + module + "." + n for n in re.findall(
            r"^theorem (\S+)", (library / "CssSemantics" / (module + ".lean")).read_text(), re.M)]
    if not set(old) <= set(expected_names):
        raise RuntimeError("Scalar audit registrations missing")
    audit_names = old + own
    runner = (library / "tests/RunExamples.lean").read_text()
    registered_loop = '  for (name, accepted) in CodePointInputExamples.checks do\n    IO.println s!"PASS {name}: {accepted}"\n'
    if runner.count(registered_loop) != 1:
        raise RuntimeError("New runner registration differs")
    for module in registration["modules"]:
        if (library / "CssSemantics.lean").read_text().count("import CssSemantics." + module + "\n") != 1:
            raise RuntimeError("Aggregator registration missing or duplicated")
    new_expected = [(n, v) for n, v in checker.EXECUTABLE_CASES if n in registration["cases"]]
    if [n for n, _ in new_expected] != registration["cases"] or any(v is not True for _, v in new_expected):
        raise RuntimeError("New ordered executable registrations differ")
    old_case_names = re.findall(r'\("([^"]+)",', (library / "CssSemantics/CssInputExamples.lean").read_text())
    old_expected = [(n, v) for n, v in checker.EXECUTABLE_CASES if n in old_case_names]
    if len(old_expected) != 24:
        raise RuntimeError("Scalar regression case vector changed")
    observations = old_expected + new_expected
    with tempfile.TemporaryDirectory(prefix="source-replay-", dir=out) as tmp:
        work = Path(tmp)
        (work / "CssSemantics").mkdir()
        for module in MODULES:
            rel = "CssSemantics/" + module + ".lean"
            (work / rel).write_bytes((library / rel).read_bytes())
            run("build-" + module, [lean, "-o", rel.replace(".lean", ".olean"), rel], work)
        (work / "Audit.lean").write_text(
            "import CssSemantics.CssInputExamples\nimport CssSemantics.CssCodePointInputExamples\n" +
            "".join("#print axioms " + n + "\n" for n in audit_names))
        audit = checker.parse_axiom_audit(run("axioms", [lean, "Audit.lean"], work))
        if set(audit) != set(audit_names):
            raise RuntimeError("Scoped axiom audit mismatch")
        (work / "Run.lean").write_text(
            "import CssSemantics.CssInputExamples\nimport CssSemantics.CssCodePointInputExamples\n"
            "open CssSemantics\ndef main : IO Unit := do\n"
            '  for (name, accepted) in CssInputExamples.checks do\n    IO.println s!"PASS {name}: {accepted}"\n' +
            registered_loop)
        results = run("examples", [lean, "--run", "Run.lean"], work)
        if results.splitlines() != [f"PASS {n}: {str(v).lower()}" for n, v in observations]:
            raise RuntimeError("Scoped executable observations differ")
        controls = {}
        feature = next(f for f in json.loads((library / "coverage.json").read_text())["features"]
                       if f["id"] == registration["feature"])
        source_coverage = json.loads((library / "coverage.json").read_text())
        fixture = work / "metadata"
        (fixture / "CssSemantics").mkdir(parents=True)
        (fixture / "tests").mkdir()
        for module in registration["modules"]:
            (fixture / "CssSemantics" / (module + ".lean")).write_bytes(
                (library / "CssSemantics" / (module + ".lean")).read_bytes())
        fixture_coverage = {"specifications": source_coverage["specifications"], "features": [feature]}
        audit_text = "".join("#print axioms " + n + "\n" for n in own)

        def fixture_check(audit_source, coverage):
            (fixture / "tests/Audit.lean").write_text(audit_source)
            (fixture / "coverage.json").write_text(json.dumps(coverage))
            checker.ROOT = fixture
            try:
                return checker.validate_coverage()
            finally:
                checker.ROOT = library

        fixture_check(audit_text, fixture_coverage)
        for name, mutation, prefix in [
            ("missing-audit", "audit-missing", "Axiom audit does not cover"),
            ("duplicate-audit", "audit-duplicate", "Duplicate axiom audit declaration"),
            ("unknown-module", "modules", "Unknown coverage module"),
            ("unknown-theorem", "theorems", "Unknown coverage theorem"),
            ("unknown-specification", "specifications", "Unknown coverage specification"),
        ]:
            altered = json.loads(json.dumps(fixture_coverage))
            altered_audit = audit_text
            if mutation == "audit-missing":
                altered_audit = "\n".join(audit_text.splitlines()[1:]) + "\n"
            elif mutation == "audit-duplicate":
                altered_audit += audit_text.splitlines()[0] + "\n"
            else:
                altered["features"][0][mutation].append("missing")
            try:
                fixture_check(altered_audit, altered)
            except RuntimeError as error:
                if not str(error).startswith(prefix):
                    raise
                controls[name] = str(error)
            else:
                raise RuntimeError(f"Metadata mutation accepted: {name}")
        original = (library / "CssSemantics/CssCodePointInput.lean").read_text()
        for name, before_text, after_text, witness in [
            ("surrogate-not-replaced", "else if p.val = 0 ∨ Surrogate p then", "else if p.val = 0 then",
             "filterValues [0xd800] = some ['�']"),
            ("CRLF-not-collapsed", "then '\\n' :: preprocess rest", "then '\\n' :: preprocess (q :: rest)",
             "filterValues [0x0d, 0x0a] = some ['\\n']"),
        ]:
            if original.count(before_text) != 1:
                raise RuntimeError("Mutation anchor changed: " + name)
            mutant = work / name
            (mutant / "CssSemantics").mkdir(parents=True)
            (mutant / "CssSemantics/CssCodePointInput.lean").write_text(original.replace(before_text, after_text))
            run(name + "-typecheck", [lean, "-o", "CssSemantics/CssCodePointInput.olean",
                                     "CssSemantics/CssCodePointInput.lean"], mutant)
            (mutant / "CssSemantics/CssCodePointInputLaws.lean").write_bytes(
                (library / "CssSemantics/CssCodePointInputLaws.lean").read_bytes())
            run(name + "-correspondence", [lean, "CssSemantics/CssCodePointInputLaws.lean"], mutant, False)
            (mutant / "Witness.lean").write_text(
                "import CssSemantics.CssCodePointInput\nopen CssSemantics.CodePointInput\nexample : " +
                witness + " := by decide\n")
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, False)
            if not re.fullmatch(
                r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n"
                r"(?:  [^\n]*\n)+is false\n", failure):
                raise RuntimeError("Unexpected semantic witness diagnostic: " + failure)
            controls[name] = "type-correct executable mutation; correspondence and concrete witness rejected"
    if hashes() != before:
        raise RuntimeError("Canonical input changed during verification")
    (out / "inputs.json").write_text(json.dumps(before, indent=2) + "\n")
    report = {"status": "pass", "lean": version, "new_declarations": len(own),
              "compiled_modules": MODULES,
              "new_cases": len(new_expected), "scalar_regression_cases": len(old_expected),
              "scoped_axioms": audit, "global_static_declarations": len(all_declarations),
              "controls": controls, "commands": commands, "temporary_builds_removed": True,
              "full_library_build_run": False, "browser_run": False,
              "spec_translation_mechanically_proved": False,
              "input_manifest_sha256": digest((out / "inputs.json").read_bytes())}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(own)} new declarations; {len(new_expected)} new + {len(old_expected)} scalar cases; {len(controls)} controls")


if __name__ == "__main__":
    main()
