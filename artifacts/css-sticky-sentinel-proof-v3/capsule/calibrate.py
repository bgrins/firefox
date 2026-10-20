import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parent
CAPSULE = ARTIFACTS / "css-sticky-sentinel-source-v1/capsule"
NATIVE = ARTIFACTS / "css-sticky-sentinel-proof-v1/native-replay-v1"
MANIFEST = "9c0ec1eab8320b7c046957cebbe8899aa513b1c70a44ecd6a510828a67a22450"
LEAN = "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-capsule", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    options = parser.parse_args()
    global CAPSULE, NATIVE
    CAPSULE = options.source_capsule.resolve(strict=True)
    NATIVE = options.native.resolve(strict=True)
    lean = options.lean.resolve(strict=True)
    require(sha(lean) == LEAN, "Lean executable identity")
    require(sha(CAPSULE / "FILES.json") == MANIFEST, "source manifest identity")
    entries = json.loads((CAPSULE / "FILES.json").read_text())["files"]
    for entry in entries:
        require(sha(CAPSULE / entry["path"]) == entry["sha256"], entry["path"])
    native_result = json.loads((NATIVE / "RESULT.json").read_text())
    require(native_result["complete"] and native_result["cases"] == 856
            and native_result["source_manifest"] == MANIFEST, "native replay identity")
    commands_native = json.loads((NATIVE / "COMMANDS.json").read_text())
    native = {}
    for item in commands_native:
        path = NATIVE / item["name"] / "raw.jsonl"
        require(item["compile_exit"] == item["run_exit"] == 0, "native execution")
        require(sha(path) == item["output_sha256"], "native output pin")
        native[item["name"]] = [json.loads(line) for line in path.read_text().splitlines()]
    require(len(native) == 11, "native variant roster")
    options.output.mkdir(parents=True, exist_ok=False)
    source_names = ["MaskedSticky", "StickyComposition", "StickyLifecycle", "Calibration"]
    inputs = {name: sha(HERE / "lean" / (name + ".lean")) for name in source_names}
    inputs["cases"] = sha(CAPSULE / "CASES.json")
    inputs["native_result"] = sha(NATIVE / "RESULT.json")
    inputs["native_commands"] = sha(NATIVE / "COMMANDS.json")
    write(options.output / "INPUTS.json", inputs)
    commands = []
    outputs = {}
    with tempfile.TemporaryDirectory(prefix="sticky-calibration-") as temporary:
        work = Path(temporary)
        env = {k: v for k, v in os.environ.items() if not k.startswith("LEAN_")}
        env["LEAN_PATH"] = str(work)
        for name in source_names:
            (work / (name + ".lean")).write_bytes((HERE / "lean" / (name + ".lean")).read_bytes())
        for name in source_names:
            command = [str(lean), "-o", str(work / (name + ".olean")), str(work / (name + ".lean"))]
            with (options.output / (name + ".log")).open("w") as log:
                result = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
            commands.append({"name": name, "command": command, "exit": result.returncode})
            write(options.output / "COMMANDS.json", commands)
            require(result.returncode == 0, "compile " + name)
        for variant in ["old", "new", "reference"]:
            command = [str(lean), "--run", str(work / "Calibration.lean"), variant]
            result = subprocess.run(command, cwd=work, env=env, input=(CAPSULE / "CASES.json").read_text(),
                                    text=True, capture_output=True)
            (options.output / (variant + ".jsonl")).write_text(result.stdout)
            (options.output / (variant + ".stderr")).write_text(result.stderr)
            commands.append({"name": variant, "command": command, "exit": result.returncode})
            write(options.output / "COMMANDS.json", commands)
            require(result.returncode == 0 and not result.stderr, "run " + variant)
            outputs[variant] = [json.loads(line) for line in result.stdout.splitlines()]
            require(len(outputs[variant]) == 856, "Lean row count " + variant)
            native_variant = "old" if variant == "old" else "new"
            for mode in ["debug", "release"]:
                expected = native[native_variant + "-" + mode]
                differences = [i for i, (a, b) in enumerate(zip(outputs[variant], expected)) if a != b]
                write(options.output / (variant + "-" + mode + "-differences.json"), differences)
                require(not differences, "Lean/native complete observation mismatch " + variant + " " + mode)
    require(outputs["new"] == outputs["reference"], "projection refinement calibration")
    mutants = {}
    for name, rows in native.items():
        if name.startswith(("old-", "new-")):
            continue
        differences = [i for i, (a, b) in enumerate(zip(rows, outputs["new"]))
                       if (a["value"], a["frames"]) != (b["value"], b["frames"])]
        require(differences, "native mutant undetected " + name)
        mutants[name] = {"changed_cases": len(differences), "first_index": differences[0]}
    for name in source_names:
        require(sha(HERE / "lean" / (name + ".lean")) == inputs[name], "Lean source drift")
    require(sha(lean) == LEAN, "Lean executable drift")
    write(options.output / "RESULT.json", {
        "status": "SOURCE_MODEL_CALIBRATION_CHECKPOINT",
        "cases": 856, "lean_variants": 3, "native_modes": 2,
        "full_observation_comparisons": 5136,
        "observation_fields": ["value", "frames", "trace"],
        "source_manifest": MANIFEST, "lean_sha256": LEAN,
        "mutants": mutants, "temporary_compiler_products_removed": True,
        "scope": "Finite old/new/reference lifecycle calibration. Universal projection substitution is proved; native lifecycle transcription, graph termination and provider correspondence require review.",
    })
    print((options.output / "RESULT.json").read_text())


if __name__ == "__main__":
    main()
