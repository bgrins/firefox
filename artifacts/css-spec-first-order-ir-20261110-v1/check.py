import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    args = parser.parse_args()
    lean = str(args.lean.resolve())
    (HERE / "RESULT.json").unlink(missing_ok=True)
    prior = json.loads((HERE / "PRIOR.json").read_text())
    for name, expected in prior["files"].items():
        if sha(HERE / name) != expected:
            raise ValueError("Pinned prior source changed: " + name)
    build = HERE / "build"
    if build.exists():
        shutil.rmtree(build)
    (build / "CssSemantics").mkdir(parents=True)
    (HERE / "logs").mkdir(exist_ok=True)
    env = dict(os.environ, LEAN_PATH=str(build))
    commands, controls = [], []

    def run(name, argv, expected=0, environment=None):
        process = subprocess.run(argv, env=environment or env, capture_output=True, text=True)
        output = process.stdout + process.stderr
        log = HERE / "logs" / (name + ".log")
        log.write_text(output)
        commands.append({"name": name, "argv": argv, "returncode": process.returncode, "log_sha256": sha(log)})
        if process.returncode != expected:
            raise ValueError(f"Unexpected exit for {name}: {process.returncode}; see {log}")
        return output

    def compile(name, module, root, output_root, environment=None):
        return run(name, [lean, "-R", str(root), "-o", str(output_root / (module + ".olean")), str(root / (module + ".lean"))], environment=environment)

    def audit(text, names, axioms):
        expected = [f"'CssDerivation.FirstOrder.{name}' depends on axioms: [{axioms}]" for name in names]
        if text.strip().splitlines() != expected:
            raise ValueError("Unexpected proof audit; no sorry/custom axioms or warnings admitted")

    version = run("lean-version", [lean, "--version"]).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Review toolchain change explicitly")
    run("generate", [sys.executable, "-I", "-B", str(HERE / "generate.py")])
    compile("StatefulIR", "StatefulIR", HERE / "prior", build)
    compile("FirstOrder", "FirstOrder", HERE, build)
    audit(compile("Lowering", "Lowering", HERE, build), ["lowering_correct"], "propext")
    for module in ["CssSemantics/CssEscape", "CssSemantics/CssInput"]:
        compile(Path(module).name, module, HERE / "prior/library", build)
    compile("GeneratedEscape", "GeneratedEscape", HERE / "prior/generated", build)
    reference = compile("prior-bridge", "Bridge", HERE / "prior", build)
    reference_expected = [f"'CssDerivation.{name}' depends on axioms: [propext]" for name in
        ["scan_equivalent", "escape_equivalent", "escape_spec", "eof_exactly", "valid_call"]]
    reference_expected.append("'CssDerivation.preprocessing_boundary' depends on axioms: [propext, Quot.sound]")
    if reference.strip().splitlines() != reference_expected:
        raise ValueError("Unexpected prior proof audit")
    compile("GeneratedFirstOrder", "GeneratedFirstOrder", HERE / "generated", build)
    bridge_names = ["escape_matches_prior", "lowered_escape_matches_prior", "escape_relation", "ready_escape"]
    audit(compile("FOBridge", "FOBridge", HERE, build), bridge_names, "propext, Quot.sound")
    for module in ["Reusable", "Examples"]:
        if compile(module, module, HERE, build).strip():
            raise ValueError("Unexpected example diagnostics")

    spec = importlib.util.spec_from_file_location("fo_generate", HERE / "generate.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    ast = json.loads((HERE / "generated/escape.json").read_text())
    if json.loads(json.dumps(ast)) != ast or generator.emit(ast) != (HERE / "generated/GeneratedFirstOrder.lean").read_text():
        raise ValueError("Data serialization/emission mismatch")
    if "fun " in generator.emit(ast) or "CssSemantics" in generator.emit(ast):
        raise ValueError("Generated data must not embed functions/reference calls")

    def failed_witness(name, folder, text, mutant_env):
        (folder / "Witness.lean").write_text(text)
        failure = run(name + "-witness", [lean, str(folder / "Witness.lean")], expected=1, environment=mutant_env)
        if "Tactic `decide` proved that the proposition" not in failure or "is false" not in failure:
            raise ValueError("No concrete semantic failure for " + name)

    def escape_witness(input_term, result_term):
        return "import GeneratedFirstOrder\nopen CssDerivation CssDerivation.FirstOrder\nexample : FirstOrder.execute escapeTree " + input_term + " = " + result_term + " := by decide\n"

    ast_mutations = []
    alias = copy.deepcopy(ast)
    alias["program"]["args"][1]["args"][1]["args"][2]["args"][2]["args"][0]["args"][1]["args"][0] = 0
    ast_mutations.append(("wrong-local-same-type", alias, '"41!".toList', "⟨'A', ['!'], false⟩"))
    budget = copy.deepcopy(ast)
    budget["program"]["args"][1]["args"][1]["args"][0] = 6
    ast_mutations.append(("seventh-hex-digit", budget, '"0000417".toList', "⟨'A', ['7'], false⟩"))
    error = copy.deepcopy(ast)
    error["program"]["args"][0] = error["program"]["args"][0]["args"][0]
    ast_mutations.append(("ast-eof-error-lost", error, "[]", "⟨'�', [], true⟩"))
    maximum = copy.deepcopy(ast)
    maximum["definitions"]["decodeExpr"]["args"][0]["args"][1]["op"] = "leNat"
    ast_mutations.append(("maximum-rejected", maximum, '"10ffff!".toList', "⟨Char.ofNat 0x10ffff, ['!'], false⟩"))
    for name, changed, input_term, result_term in ast_mutations:
        folder = build / name
        folder.mkdir()
        mutant_env = dict(env, LEAN_PATH=str(folder) + os.pathsep + str(build))
        (folder / "GeneratedFirstOrder.lean").write_text(generator.emit(changed))
        compile(name + "-data", "GeneratedFirstOrder", folder, folder, mutant_env)
        failure = run(name + "-bridge", [lean, str(HERE / "FOBridge.lean")], expected=1, environment=mutant_env)
        if "error:" not in failure:
            raise ValueError("No correspondence failure for " + name)
        failed_witness(name, folder, escape_witness(input_term, result_term), mutant_env)
        controls.append({"name": name, "result": "well-typed AST; escape correspondence and concrete witness fail"})

    first_order = (HERE / "FirstOrder.lean").read_text()
    for name, old, new, witness in [
        ("lower-read-lost", "| .read eof present, env => .bind .read fun value =>", "| .read eof present, env => .bind (.pure (none : Option Char)) fun value =>",
            "import FirstOrder\nopen CssDerivation CssDerivation.FirstOrder\ndef p : Stmt [] .nat := .read (.ret (.nat 0)) (.ret (.code (.var .here)))\nexample : run (lower p .nil) ⟨['z'], false⟩ = interpret p .nil ⟨['z'], false⟩ := by decide\n"),
        ("lower-error-lost", "| .raiseError next, env => .bind .raiseError fun _ =>", "| .raiseError next, env => .bind (.pure ()) fun _ =>",
            "import FirstOrder\nopen CssDerivation CssDerivation.FirstOrder\ndef p : Stmt [] .unit := .raiseError (.ret .unit)\nexample : run (lower p .nil) ⟨[], false⟩ = interpret p .nil ⟨[], false⟩ := by decide\n"),
    ]:
        if first_order.count(old) != 1:
            raise ValueError("Ambiguous lowering mutation")
        folder = build / name
        folder.mkdir()
        mutant_env = dict(env, LEAN_PATH=str(folder) + os.pathsep + str(build))
        (folder / "FirstOrder.lean").write_text(first_order.replace(old, new))
        compile(name + "-implementation", "FirstOrder", folder, folder, mutant_env)
        failure = run(name + "-proof", [lean, str(HERE / "Lowering.lean")], expected=1, environment=mutant_env)
        if "error:" not in failure:
            raise ValueError("No generic theorem failure")
        failed_witness(name, folder, witness, mutant_env)
        controls.append({"name": name, "result": "type-correct lowering; universal theorem and concrete witness fail"})

    name = "shared-multiplication-defect"
    folder = build / name
    folder.mkdir()
    mutant_env = dict(env, LEAN_PATH=str(folder) + os.pathsep + str(build))
    if first_order.count("eval left env * eval right env") != 1:
        raise ValueError("Ambiguous multiplication mutation")
    (folder / "FirstOrder.lean").write_text(first_order.replace("eval left env * eval right env", "eval left env + eval right env"))
    compile(name + "-implementation", "FirstOrder", folder, folder, mutant_env)
    audit(compile(name + "-lowering", "Lowering", HERE, folder, mutant_env), ["lowering_correct"], "propext")
    compile(name + "-data", "GeneratedFirstOrder", HERE / "generated", folder, mutant_env)
    failure = run(name + "-bridge", [lean, str(HERE / "FOBridge.lean")], expected=1, environment=mutant_env)
    if "error:" not in failure:
        raise ValueError("Shared primitive defect unexpectedly agrees with CSS model")
    failed_witness(name, folder, escape_witness('"41!".toList', "⟨'A', ['!'], false⟩"), mutant_env)
    controls.append({"name": name, "result": "universal lowering theorem still passes; independent escape bridge and concrete witness fail"})

    for name, bad in [
        ("ill-scoped-local", generator.node("ret", generator.node("var", 0))),
        ("wrong-result-type", generator.node("ret", generator.node("nat", 0))),
    ]:
        changed = copy.deepcopy(ast)
        changed["program"] = bad
        folder = build / name
        folder.mkdir()
        (folder / "GeneratedFirstOrder.lean").write_text(generator.emit(changed))
        failure = run(name, [lean, str(folder / "GeneratedFirstOrder.lean")], expected=1)
        if "error" not in failure:
            raise ValueError("Malformed typed AST not rejected")
        controls.append({"name": name, "result": "Lean rejects the ill-typed data construction"})
    for name, malformed in [("unknown-constructor", {"op": "executeLean", "args": ["arbitrary text"]}),
        ("extra-payload", {"op": "nat", "args": [0], "lean": "arbitrary text"})]:
        try:
            generator.emit_expr(malformed)
        except ValueError as error:
            controls.append({"name": name, "result": "emitter refuses data outside its constructor schema", "reason": str(error)})
        else:
            raise ValueError("Unrecognized AST payload accepted")
    drift = build / "source-drift"
    drift.mkdir()
    shutil.copyfile(HERE / "generate.py", drift / "generate.py")
    shutil.copyfile(HERE / "PRIOR.json", drift / "PRIOR.json")
    for path in prior["files"]:
        (drift / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / path, drift / path)
    source = drift / "prior/inputs/css-syntax-3.bs"
    source.write_bytes(source.read_bytes() + b"\n")
    failure = run("source-drift", [sys.executable, "-I", "-B", str(drift / "generate.py")], expected=1)
    if "Pinned prior source changed" not in failure or (drift / "generated").exists():
        raise ValueError("Unexpected source-drift outcome")
    controls.append({"name": "source-drift", "result": "changed pinned source refused before generation"})
    names = ["FirstOrder.lean", "Lowering.lean", "FOBridge.lean", "Reusable.lean", "Examples.lean", "generate.py", "check.py", "PRIOR.json", "generated/escape.json", "generated/GeneratedFirstOrder.lean"]
    result = {"passed": True, "lean_version": version, "universal_lowering_checked": True,
        "escape_full_result_correspondence_checked": True, "prose_refinement_proved": False,
        "json_emitter_correctness_proved": False, "native_browser_run": False,
        "controls": controls, "commands": commands, "files": {name: sha(HERE / name) for name in names}}
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    shutil.rmtree(build)
    print(json.dumps({"passed": True, "controls": controls, "temporary_build_removed": True}, indent=2))


if __name__ == "__main__":
    main()
