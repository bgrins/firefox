import argparse
import copy
import datetime
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


def verify(root, files):
    for name, expected in files.items():
        if sha(root / name) != expected:
            raise ValueError("Frozen or pinned file changed: " + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    args = parser.parse_args()
    lean = str(args.lean.resolve())
    (HERE / "RESULT.json").unlink(missing_ok=True)
    frozen = json.loads((HERE / "FREEZE.json").read_text())
    verify(HERE, frozen["files"])
    manifests = {name: json.loads((HERE / name).read_text()) for name in ["SOURCE.json", "INFRA.json"]}
    for source in manifests.values():
        verify(HERE, {source["file"]: source["sha256"]})
    library = json.loads((HERE / "LIBRARY.json").read_text())
    verify(HERE, library["files"])
    build = HERE / "build"
    if build.exists():
        shutil.rmtree(build)
    (build / "CssSemantics").mkdir(parents=True)
    (HERE / "logs").mkdir(exist_ok=True)
    env = dict(os.environ, LEAN_PATH=str(build))
    commands, controls = [], []

    def run(name, argv, expected=0, environment=None):
        process = subprocess.run(argv, env=environment or env, capture_output=True, text=True)
        log = process.stdout + process.stderr
        path = HERE / "logs" / (name + ".log")
        path.write_text(log)
        commands.append({"name": name, "argv": argv, "returncode": process.returncode, "log_sha256": sha(path)})
        if process.returncode != expected:
            raise ValueError(f"Unexpected exit for {name}: {process.returncode}; see {path}")
        return log

    def compile(name, source, module_root, output, environment=None):
        return run(name, [lean, "-R", str(module_root), "-o", str(output), str(source)], environment=environment)

    version = run("lean-version", [lean, "--version"]).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version; review toolchain change explicitly")
    run("extract", [sys.executable, "-I", "-B", str(HERE / "translate.py"),
        "consume-escaped-code-point", "--output", str(HERE / "generated")])
    for name in library["build_order"]:
        compile(name, HERE / "library/CssSemantics" / (name + ".lean"), HERE / "library", build / "CssSemantics" / (name + ".olean"))
    compile("ir", HERE / "StatefulIR.lean", HERE, build / "StatefulIR.olean")
    compile("generated", HERE / "generated/GeneratedEscape.lean", HERE / "generated", build / "GeneratedEscape.olean")
    bridge = compile("bridge", HERE / "Bridge.lean", HERE, build / "Bridge.olean")
    expected = [f"'CssDerivation.{name}' depends on axioms: [propext]" for name in
        ["scan_equivalent", "escape_equivalent", "escape_spec", "eof_exactly", "valid_call"]]
    expected.append("'CssDerivation.preprocessing_boundary' depends on axioms: [propext, Quot.sound]")
    if bridge.strip().splitlines() != expected:
        raise ValueError("Unexpected axiom audit; no sorry/custom axioms or warnings admitted")
    if run("examples", [lean, str(HERE / "Examples.lean")]).strip():
        raise ValueError("Unexpected example diagnostics")
    for name in ["StatefulIR.lean", "generated/GeneratedEscape.lean"]:
        if "CssSemantics" in (HERE / name).read_text():
            raise ValueError("Derived implementation must not depend on reference library")

    spec = importlib.util.spec_from_file_location("stateful_translate", HERE / "translate.py")
    translator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(translator)
    css, infra = [(HERE / manifests[name]["file"]).read_text() for name in ["SOURCE.json", "INFRA.json"]]
    held = run("held-out", [sys.executable, "-I", "-B", str(HERE / "translate.py"),
        "consume-number", "--output", str(build / "held-out")], expected=1)
    if "Unsupported algorithm interface" not in held or (build / "held-out").exists():
        raise ValueError("Unexpected held-out outcome")
    begin, _, end = translator.section(css, "consume-number")
    (HERE / "held-out.bs").write_text(css[begin:end])
    (HERE / "HELD-OUT.json").write_text(json.dumps({
        "status": "rejected", "first_unsupported": "Numeric value/type/sign result interface",
        "generated_lean": False, "correspondence_proved": False,
        "freeze_sha256": sha(HERE / "FREEZE.json"),
        "evaluated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_bytes": translator.span(css, begin, end),
    }, indent=2) + "\n")

    ir = json.loads((HERE / "generated/algorithm.json").read_text())
    mutations = [
        ("seventh-hex-digit", "hex_additional_limit", 6, '"0000417".toList', "⟨'A', ['7'], false⟩"),
        ("second-terminator", "terminator_limit", 2, '"41  Z".toList', "⟨'A', [' ', 'Z'], false⟩"),
        ("zero-not-replaced", "zero_is_invalid", False, '"0!".toList', "⟨'�', ['!'], false⟩"),
        ("surrogate-not-replaced", "surrogate_is_invalid", False, '"d800!".toList', "⟨'�', ['!'], false⟩"),
        ("maximum-rejected", "maximum_is_inclusive", False, '"10ffff!".toList', "⟨Char.ofNat 0x10ffff, ['!'], false⟩"),
        ("eof-error-lost", "eof_error", False, "[]", "⟨'�', [], true⟩"),
        ("read-does-not-advance", None, None, '"z!".toList', "⟨'z', ['!'], false⟩"),
    ]
    for name, key, value, input_term, output_term in mutations:
        folder = build / name
        folder.mkdir()
        mutant_env = dict(env, LEAN_PATH=str(folder) + os.pathsep + str(build))
        mutated = copy.deepcopy(ir)
        if key is None:
            interpreter = (HERE / "StatefulIR.lean").read_text()
            needle = "(some c, { state with input := rest })"
            if interpreter.count(needle) != 1:
                raise ValueError("Ambiguous read mutation")
            (folder / "StatefulIR.lean").write_text(interpreter.replace(needle, "(some c, state)"))
            compile(name + "-ir", folder / "StatefulIR.lean", folder, folder / "StatefulIR.olean", mutant_env)
        else:
            mutated["program"][key] = value
        (folder / "GeneratedEscape.lean").write_text(translator.generate(mutated))
        compile(name + "-generated", folder / "GeneratedEscape.lean", folder, folder / "GeneratedEscape.olean", mutant_env)
        proof_failure = run(name + "-bridge", [lean, str(HERE / "Bridge.lean")], expected=1, environment=mutant_env)
        if "error:" not in proof_failure:
            raise ValueError("No theorem diagnostic for mutation " + name)
        witness = "import GeneratedEscape\nopen CssDerivation\nexample : execute escape " + input_term + " = " + output_term + " := by decide\n"
        (folder / "Witness.lean").write_text(witness)
        witness_failure = run(name + "-witness", [lean, str(folder / "Witness.lean")], expected=1, environment=mutant_env)
        if "Tactic `decide` proved that the proposition" not in witness_failure or "is false" not in witness_failure:
            raise ValueError("No concrete semantic counterexample for " + name)
        controls.append({"name": name, "result": "mutated implementation typechecks; bridge fails; independent concrete witness is false"})

    begin, _, end = translator.section(css, "consume-escaped-code-point")
    for name, old, new in [
        ("extra-operation", "Consume the <a>next input code point</a>.", "Consume the <a>next input code point</a>. Advance the stream again."),
        ("unreviewed-metadata", "1-6 hex digits", "1-7 hex digits"),
    ]:
        body = css[begin:end]
        if body.count(old) != 1:
            raise ValueError("Ambiguous refusal mutation")
        altered = css[:begin] + body.replace(old, new) + css[end:]
        try:
            translator.extract(altered, infra, "consume-escaped-code-point")
        except ValueError as error:
            controls.append({"name": name, "result": "refused", "reason": str(error)})
        else:
            raise ValueError("Unsupported source accepted")

    for modified in manifests:
        folder = build / modified.removesuffix(".json")
        (folder / "inputs").mkdir(parents=True)
        for name in ["translate.py", *manifests, *(m["file"] for m in manifests.values())]:
            shutil.copyfile(HERE / name, folder / name)
        target = folder / manifests[modified]["file"]
        target.write_bytes(target.read_bytes() + b"\n")
        failure = run(modified + "-drift", [sys.executable, "-I", "-B", str(folder / "translate.py"),
            "consume-escaped-code-point", "--output", str(folder / "output")], expected=1)
        if "Pinned source changed" not in failure or (folder / "output").exists():
            raise ValueError("Unexpected source-drift result")
        controls.append({"name": modified + "-drift", "result": "actual command refuses changed source before generation"})
    changed = build / "changed-rule"
    changed.mkdir()
    (changed / "StatefulIR.lean").write_bytes((HERE / "StatefulIR.lean").read_bytes() + b"\n")
    try:
        verify(changed, {"StatefulIR.lean": frozen["files"]["StatefulIR.lean"]})
    except ValueError:
        controls.append({"name": "frozen-rule-drift", "result": "changed interpreter bytes rejected against frozen digest"})
    else:
        raise ValueError("Frozen-rule check failed")
    verify(HERE, frozen["files"])
    result = {
        "passed": True, "development_generated": 1, "development_correspondence_proved": 1,
        "held_out_generated": 0, "held_out_status": "unsupported interface", "examples": 18,
        "lean_version": version, "freeze_sha256": sha(HERE / "FREEZE.json"),
        "controls": controls, "commands": commands,
        "files": {name: sha(HERE / name) for name in ["translate.py", "StatefulIR.lean", "Bridge.lean", "Examples.lean", "check.py", "GRAMMAR.md", "FREEZE.json", "generated/GeneratedEscape.lean", "generated/algorithm.json"]},
        "prose_refinement_proved": False, "native_browser_run": False,
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    shutil.rmtree(build)
    print(json.dumps({"passed": True, "development": "1/1", "held_out": "0/1; unsupported return interface", "controls": controls, "temporary_build_removed": True}, indent=2))


if __name__ == "__main__":
    main()
