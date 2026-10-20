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

ROOT = Path(__file__).resolve().parent
MODULES = ["MaskedSticky", "StickyComposition", "StickyLifecycle", "StickyIndexed",
           "StickyMachineLifecycle", "StickyUpdate", "StickyJoined", "StickyAdmission",
           "ReviewChallenges", "StickyJoinedChallenges"]
CHALLENGES = {"cycle": False, "subtraction": False, "ordinary": True,
              "addition": False, "y-addition": False, "missing-normal": True,
              "unused-hazard": True, "later-frame": True, "fallback": True,
              "reflow": True, "overflow-cycle": False, "overflow-root": True}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(text):
    def unique(items):
        obj = {}
        for key, value in items:
            require(key not in obj, "duplicate field")
            obj[key] = value
        return obj
    return json.loads(text, object_pairs_hook=unique)


def point(value, optional=False):
    if optional and value is None:
        return
    require(type(value) is list and len(value) == 2 and
            all(type(v) is int for v in value), "point")


def observation(value):
    require(type(value) is dict and set(value) == {"value", "frames", "trace"}, "observation fields")
    point(value["value"], True)
    require(type(value["frames"]) is list and type(value["trace"]) is list, "observation lists")
    for p in value["frames"]:
        point(p)
    require(all(type(v) is str for v in value["trace"]), "trace strings")


def rows(text, challenge=False):
    values = [decode(line) for line in text.splitlines()]
    roster = list(CHALLENGES) if challenge else list(range(856))
    require(len(values) == len(roster), "row count")
    key = "name" if challenge else "id"
    for expected, row in zip(roster, values):
        require(type(row) is dict and set(row) == {key, "admitted", "exhausted", "machine",
                "mathematical", "independent_value", "independent_frames"}, "row fields")
        require(type(row[key]) is type(expected) and row[key] == expected, "ordered case identity")
        require(type(row["admitted"]) is bool and type(row["exhausted"]) is bool, "boolean fields")
        observation(row["machine"])
        observation(row["mathematical"])
        point(row["independent_value"], True)
        require(type(row["independent_frames"]) is list, "reference frames")
        for p in row["independent_frames"]:
            point(p)
    return values


def validate_reference(values):
    for row in values:
        if row["admitted"]:
            require(not row["exhausted"], "admitted fuel exhaustion")
            require(row["machine"] == row["mathematical"], "machine/math observation")
            require(row["machine"]["value"] == row["independent_value"] and
                    row["machine"]["frames"] == row["independent_frames"], "independent reference")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    require(sha(lean) == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf", "Lean identity")
    out = args.output.resolve()
    require(not out.exists() and ROOT not in out.parents, "new external output")
    out.mkdir(parents=True)
    original = (ROOT / "lean/Calibration.lean").read_text()
    original_decoder = original[original.index("structure RawNode"):original.index("def main")]
    for name in ["JoinedCalibration", "JoinedChallengeCalibration"]:
        source = (ROOT / "lean" / (name + ".lean")).read_text()
        require(source[source.index("structure RawNode"):source.index("def " +
                ("main" if name == "JoinedCalibration" else "challengeInputs"))] == original_decoder,
                "unchanged actual corpus decoder")
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / "lean").glob("*.lean")}
    inputs["native-source/CASES.json"] = sha(ROOT / "native-source/CASES.json")
    (out / "INPUTS.json").write_text(json.dumps(inputs, indent=2) + "\n")
    commands = []

    def command(label, argv, work, env, stdin=None):
        result = subprocess.run(argv, cwd=work, env=env, input=stdin, text=True, capture_output=True)
        (out / (label + ".stdout")).write_text(result.stdout)
        (out / (label + ".stderr")).write_text(result.stderr)
        commands.append({"label": label, "argv": argv, "exit": result.returncode})
        (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        require(result.returncode == 0, "command failed " + label)
        return result.stdout

    mutations = {
        "skip-continuation-tail": ("StickyMachineLifecycle", "    machineMoveChain d fuel (← next i)", "    pure ()"),
        "mix-addition-coordinates": ("StickyMachineLifecycle", "signed32 (signed32 a.y + signed32 b.y)",
                                     "signed32 (signed32 a.y + signed32 b.x)"),
        "omit-y-loop-domain": ("StickyMachineLifecycle", "    PointSafe (plus (observedNormal w.nodes[i]!) d)",
                               "    Representable (plus (observedNormal w.nodes[i]!) d).x"),
        "eager-missing-normal-domain": ("StickyMachineLifecycle", "  w.nodes[i]!.hadNormal = true →",
                                       "  True →"),
        "omit-continuation-chain-domain": ("StickyJoined",
            "  | 3 => Chain w.nodes (some input.target) (chains input.target) ∧",
            "  | 3 => True ∧"),
    }
    records = {}
    with tempfile.TemporaryDirectory(prefix="sticky-joined-") as temporary:
        work = Path(temporary)
        env = {k: v for k, v in os.environ.items() if not k.startswith("LEAN_")}
        env["LEAN_PATH"] = str(work)
        for module in MODULES + ["JoinedCalibration", "JoinedChallengeCalibration"]:
            (work / (module + ".lean")).write_bytes((ROOT / "lean" / (module + ".lean")).read_bytes())
            command("compile-" + module, [str(lean), "-o", str(work / (module + ".olean")),
                                          str(work / (module + ".lean"))], work, env)
        corpus = command("corpus", [str(lean), "--run", str(work / "JoinedCalibration.lean")], work, env,
                         (ROOT / "native-source/CASES.json").read_text())
        values = rows(corpus)
        require(all(row["admitted"] for row in values), "retained corpus domain")
        validate_reference(values)
        native_counts = {}
        for mode in ["debug", "release"]:
            native = [decode(line) for line in (args.native / ("new-" + mode) / "raw.jsonl").read_text().splitlines()]
            require(len(native) == len(values), "native row count")
            for native_row, row in zip(native, values):
                observation(native_row)
                require(native_row == row["machine"], "actual complete native caller " + mode)
            native_counts[mode] = len(native)
        challenge_text = command("challenges", [str(lean), "--run", str(work / "JoinedChallengeCalibration.lean")], work, env)
        challenges = rows(challenge_text, True)
        require({row["name"]: row["admitted"] for row in challenges} == CHALLENGES, "challenge admissions")
        validate_reference(challenges)
        for label, mutation in [("stripped-positive", None), *mutations.items()]:
            for module in MODULES:
                source = (ROOT / "lean" / (module + ".lean")).read_text()
                source = re.sub(r"^theorem [\s\S]*?(?=^theorem |^def |^instance |^structure |^inductive |^abbrev |^end )", "", source, flags=re.M)
                require("theorem " not in source, "proof stripping")
                if mutation and module == mutation[0]:
                    require(source.count(mutation[1]) == 1, "mutation anchor " + label)
                    source = source.replace(mutation[1], mutation[2])
                (work / (module + ".lean")).write_text(source)
                if mutation and module == mutation[0]:
                    (out / (label + ".lean")).write_text(source)
                command(label + "-" + module, [str(lean), "-o", str(work / (module + ".olean")),
                                              str(work / (module + ".lean"))], work, env)
            command(label + "-driver", [str(lean), "-o", str(work / "JoinedChallengeCalibration.olean"),
                                        str(work / "JoinedChallengeCalibration.lean")], work, env)
            text = command(label + "-run", [str(lean), "--run", str(work / "JoinedChallengeCalibration.lean")], work, env)
            changed = rows(text, True)
            diffs = [a["name"] for a, b in zip(changed, challenges) if a != b]
            require(bool(diffs) == bool(mutation), "semantic mutant witness " + label)
            records[label] = {"compiled_and_ran": True, "changed_cases": diffs}
    for name, digest in inputs.items():
        require(sha(ROOT / name) == digest, "source drift")
    result = {"status": "pass", "cases": 856, "machine_native_comparisons": 1712,
              "independent_value_position_comparisons": 856, "native_modes": native_counts,
              "challenge_cases": CHALLENGES, "mutations": records,
              "scope": "Conditional full indexed and machine caller model; finite actual native comparison, not C++ source translation or geometry-provider proof.",
              "temporary_compiler_products_removed": True}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
