import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
CAPSULE = HERE.parent / "css-sticky-sentinel-source-v1/capsule"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    require = lambda condition, message: None if condition else fail(message)
    require(sha(lean) == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf", "Lean identity")
    pins = json.loads((args.calibration / "INPUTS.json").read_text())
    for module in ["MaskedSticky", "StickyComposition", "StickyLifecycle", "Calibration"]:
        require(sha(HERE / "lean" / (module + ".lean")) == pins[module], "calibrated source drift")
    require(sha(CAPSULE / "CASES.json") == pins["cases"], "calibrated corpus drift")
    expected = [json.loads(x) for x in (args.calibration / "new.jsonl").read_text().splitlines()]
    require(len(expected) == 856, "calibration count")
    source = (HERE / "lean/StickyLifecycle.lean").read_text()
    definitions = re.sub(r"^theorem [\s\S]*?(?=^theorem |^def |^end StickyLifecycle)", "", source, flags=re.M)
    require("theorem " not in definitions, "theorem stripping")
    mutations = {
        "skip-recomputed-offsets": ("    if reflow then\n", "    if false then\n"),
        "noncanonical-translation": ("  let first ← canonical i\n", "  let first := i\n"),
        "omit-overflow-notifications": ("    if parent != subtree then\n", "    if false then\n"),
        "assign-translation-as-position": ("    setPosition i (plus n delta)\n", "    setPosition i delta\n"),
        "ignore-missing-normal-guard": ("  if f.hadNormal then\n", "  if true then\n"),
    }
    args.output.mkdir(parents=True, exist_ok=False)
    commands = []
    records = {}
    with tempfile.TemporaryDirectory(prefix="sticky-lifecycle-mutants-") as temporary:
        work = Path(temporary)
        env = {k: v for k, v in os.environ.items() if not k.startswith("LEAN_")}
        env["LEAN_PATH"] = str(work)
        for name in ["MaskedSticky", "StickyComposition", "Calibration"]:
            (work / (name + ".lean")).write_bytes((HERE / "lean" / (name + ".lean")).read_bytes())

        def compile(name, label):
            command = [str(lean), "-o", str(work / (name + ".olean")), str(work / (name + ".lean"))]
            with (args.output / (label + ".log")).open("w") as log:
                process = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
            commands.append({"name": label, "command": command, "exit": process.returncode})
            (args.output / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
            require(process.returncode == 0, "compile " + label)

        for name in ["MaskedSticky", "StickyComposition"]:
            compile(name, name)
        for label, mutation in [("stripped-positive-control", None), *mutations.items()]:
            text = definitions
            if mutation:
                old, new = mutation
                require(text.count(old) == 1, "mutation site " + label)
                text = text.replace(old, new)
            (work / "StickyLifecycle.lean").write_text(text)
            (args.output / (label + ".lean")).write_text(text)
            compile("StickyLifecycle", label)
            compile("Calibration", label + "-driver")
            command = [str(lean), "--run", str(work / "Calibration.lean"), "new"]
            process = subprocess.run(command, cwd=work, env=env, input=(CAPSULE / "CASES.json").read_text(),
                                     text=True, capture_output=True)
            (args.output / (label + ".jsonl")).write_text(process.stdout)
            (args.output / (label + ".stderr")).write_text(process.stderr)
            commands.append({"name": label + "-run", "command": command, "exit": process.returncode})
            (args.output / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
            require(process.returncode == 0 and not process.stderr, "mutant execution " + label)
            rows = [json.loads(x) for x in process.stdout.splitlines()]
            require(len(rows) == 856, "mutant row count " + label)
            differences = [i for i, (a, b) in enumerate(zip(rows, expected)) if a != b]
            values = [i for i, (a, b) in enumerate(zip(rows, expected))
                      if (a["value"], a["frames"]) != (b["value"], b["frames"])]
            require(bool(differences) == bool(mutation), "mutant discrimination " + label)
            records[label] = {"observation_differences": len(differences),
                              "value_or_position_differences": len(values),
                              "first_index": differences[0] if differences else None}
    result = {"status": "pass", "records": records, "compiler_products_removed": True,
              "scope": "Executable model mutations with proofs removed. Positive control proves stripping preserves calibrated observations; compiler failure is never counted as mutation evidence. Native mutation evidence is separate."}
    (args.output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


def fail(message):
    raise RuntimeError(message)


if __name__ == "__main__":
    main()
