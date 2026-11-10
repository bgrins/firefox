import argparse
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
TRAINING = [
    ("escape", "starts-with-a-valid-escape", "validEscape", "GeneratedValidEscape"),
    ("number", "starts-with-a-number", "numberStart", "GeneratedNumberStart"),
]


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
    source_manifest = json.loads((HERE / "SOURCE.json").read_text())
    verify(HERE, {source_manifest["file"]: source_manifest["sha256"]})
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
            raise ValueError(f"Unexpected exit code for {name}: {process.returncode}; see {path}")
        return log

    version = run("lean-version", [lean, "--version"]).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version; explicit toolchain review required")
    for folder, anchor, name, module in TRAINING:
        run("extract-" + folder, [sys.executable, "-I", "-B", str(HERE / "translate.py"), anchor,
            "--name", name, "--output", str(HERE / "generated" / folder)])
    for name in library["build_order"]:
        run(name, [lean, "-R", str(HERE / "library"), "-o", str(build / "CssSemantics" / (name + ".olean")),
            str(HERE / "library/CssSemantics" / (name + ".lean"))])
    for folder, anchor, name, module in TRAINING:
        run(module, [lean, "-R", str(HERE / "generated" / folder), "-o", str(build / (module + ".olean")),
            str(HERE / "generated" / folder / (module + ".lean"))])
    bridge = run("bridge", [lean, str(HERE / "Bridge.lean")])
    expected_audits = [
        f"'CssDerivation.{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
        for name in ["escape_equivalent", "escape_spec", "number_equivalent", "number_spec"]
    ] + [f"'CssDerivation.{name}' does not depend on any axioms" for name in ["escape_preserves", "number_preserves"]]
    if bridge.strip().splitlines() != expected_audits:
        raise ValueError("Unexpected proof audit; no sorry/custom axioms or warnings admitted")

    spec = importlib.util.spec_from_file_location("benchmark_translate", HERE / "translate.py")
    translator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(translator)
    source = (HERE / source_manifest["file"]).read_text()

    held_out = run("held-out", [sys.executable, "-I", "-B", str(HERE / "translate.py"),
        "consume-escaped-code-point", "--name", "consumeEscape", "--output", str(build / "held-out")], expected=1)
    if "Unsupported input effect" not in held_out or (build / "held-out").exists():
        raise ValueError("Unexpected held-out outcome")
    begin, _, end = translator.section(source, "consume-escaped-code-point")
    (HERE / "held-out.bs").write_text(source[begin:end])
    held_record = {
        "status": "rejected", "first_unsupported_operation": "Consume the next input code point.",
        "generated_lean": False, "correspondence_proved": False,
        "freeze_sha256": sha(HERE / "FREEZE.json"),
        "evaluated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_bytes": translator.span(source, begin, end),
    }
    (HERE / "HELD-OUT.json").write_text(json.dumps(held_record, indent=2) + "\n")

    def refusal(name, old, replacement):
        begin, _, end = translator.section(source, "starts-with-a-valid-escape")
        body = source[begin:end]
        if body.count(old) != 1:
            raise ValueError("Ambiguous mutation target")
        mutated = source[:begin] + body.replace(old, replacement) + source[end:]
        try:
            translator.extract(mutated, "starts-with-a-valid-escape")
        except ValueError as error:
            controls.append({"name": name, "result": "rejected", "reason": str(error)})
        else:
            raise ValueError("Unsupported prose accepted: " + name)

    refusal("unknown-condition", "If the first", "Only if the first")
    refusal("extra-operation", "Otherwise, return true.", "Otherwise, return true. Advance the input stream.")
    refusal("changed-effect", "will not consume any additional", "will consume one additional")

    def mutant(name, module, lean_text, required_marker):
        folder = build / name
        folder.mkdir()
        (folder / (module + ".lean")).write_text(lean_text)
        mutant_env = dict(env, LEAN_PATH=str(folder) + os.pathsep + str(build))
        run(name + "-compile", [lean, "-R", str(folder), "-o", str(folder / (module + ".olean")),
            str(folder / (module + ".lean"))], environment=mutant_env)
        failure = run(name + "-bridge", [lean, str(HERE / "Bridge.lean")], expected=1, environment=mutant_env)
        if required_marker not in failure or "Tactic `decide` proved that the proposition" not in failure:
            raise ValueError("Mutation failed for an unexpected reason: " + name)
        controls.append({"name": name, "result": "generated Lean typechecks; correspondence/state proof and concrete witness fail"})

    escape_ir = json.loads((HERE / "generated/escape/algorithm.json").read_text())
    escape_ir["tree"]["nodes"][1]["return"] = True
    mutant("newline-accepted", "GeneratedValidEscape", translator.generate(escape_ir, "validEscape"), "Tactic `rfl` failed")
    boundary_source = source.replace("U+0030 DIGIT ZERO (0) and U+0039", "U+0031 DIGIT ONE (1) and U+0039", 1)
    boundary_ir = translator.extract(boundary_source, "starts-with-a-number")
    mutant("digit-zero-excluded", "GeneratedNumberStart", translator.generate(boundary_ir, "numberStart"), "error:")
    number_text = (HERE / "generated/number/GeneratedNumberStart.lean").read_text()
    if number_text.count(", source)") != 1:
        raise ValueError("Ambiguous state mutation target")
    mutant("input-advanced", "GeneratedNumberStart", number_text.replace(", source)", ", source.tail)"), "Not a definitional equality")

    drift = build / "source-drift"
    (drift / "inputs").mkdir(parents=True)
    for name in ["translate.py", "SOURCE.json"]:
        shutil.copyfile(HERE / name, drift / name)
    (drift / source_manifest["file"]).write_bytes((HERE / source_manifest["file"]).read_bytes() + b"\n")
    failure = run("source-drift", [sys.executable, "-I", "-B", str(drift / "translate.py"),
        "starts-with-a-number", "--name", "numberStart", "--output", str(drift / "output")], expected=1)
    if "Pinned source changed" not in failure or (drift / "output").exists():
        raise ValueError("Unexpected source-drift outcome")
    controls.append({"name": "source-drift", "result": "actual command rejects changed source before generation"})
    (drift / "translate.py").write_bytes((drift / "translate.py").read_bytes() + b"\n")
    try:
        verify(drift, {"translate.py": frozen["files"]["translate.py"]})
    except ValueError:
        controls.append({"name": "freeze-integrity", "result": "changed translator bytes rejected against frozen digest"})
    else:
        raise ValueError("Freeze check did not reject drift")
    verify(HERE, frozen["files"])
    result = {
        "passed": True, "training_generated": 2, "training_correspondence_proved": 2,
        "held_out_generated": 0, "held_out_status": "rejected", "lean_version": version,
        "source_sha256": source_manifest["sha256"], "freeze_sha256": sha(HERE / "FREEZE.json"),
        "controls": controls, "commands": commands,
        "files": {name: sha(HERE / name) for name in ["translate.py", "Bridge.lean", "check.py", "GRAMMAR.md", "FREEZE.json", "LIBRARY.json", "SOURCE.json"]},
        "prose_refinement_proved": False, "native_browser_run": False,
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    shutil.rmtree(build)
    print(json.dumps({"passed": True, "training": "2/2", "held_out": "0/1; unsupported state effects", "controls": controls, "temporary_build_removed": True}, indent=2))


if __name__ == "__main__":
    main()
