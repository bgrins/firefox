import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
import hashlib
import itertools
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "artifacts/css-hidden-geometry-measure-trace-v2"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)

def vector(value, length):
    assert isinstance(value, list) and len(value) == length
    assert all(type(x) in (int, float) and math.isfinite(x) for x in value)

def reconstruct(observation, shrink):
    assert set(observation) == {"rows", "userAgent"}
    assert isinstance(observation["userAgent"], str)
    keys = (["nested", "insertion", "mode", "hidden", "api"] if shrink
            else ["columns", "flex", "initiallyHidden", "api"])
    roster = set(itertools.product(
        [False, True], ["append", "prepend"], ["shrink", "no-shrink", "zero-sibling"],
        [False, True], ["bounding", "offset"])) if shrink else set(itertools.product(
            [False, True], [False, True], [False, True], ["bounding", "rects", "offset", "scroll"]))
    phases = (["warm", "visibility", "insert", "remove", "show"] if shrink
              else ["initial", "hide", "append", "append-again", "show"])
    rows = observation["rows"]
    assert len(rows) == len(roster)
    seen, bad, repeated, calibration = set(), [], [], []
    for row in rows:
        assert set(row) == set(keys) | {"stages"}
        for name in (["nested", "hidden"] if shrink else ["columns", "flex", "initiallyHidden"]):
            assert type(row[name]) is bool
        key = tuple(row[k] for k in keys)
        assert key in roster and key not in seen
        seen.add(key)
        assert [s["phase"] for s in row["stages"]] == phases
        for stage in row["stages"]:
            assert set(stage) == {"phase", "outer", "first", "second", "third"} | ({"visible", "expected"} if shrink else set())
            vector(stage["outer"], 3)
            expected = [50 if stage["phase"] == "insert" and row.get("mode") == "shrink" else 100, 32] if shrink else [24, 32]
            if row["api"] == "rects":
                expected = [expected]
            for name in ["first", "second", "third"]:
                value = stage[name]
                if row["api"] == "rects":
                    assert isinstance(value, list)
                    for rect in value:
                        vector(rect, 2)
                else:
                    vector(value, 2)
            record = {"configuration": key, "phase": stage["phase"], "observed": stage["first"], "expected": expected}
            if shrink:
                vector(stage["expected"], 2)
                vector(stage["visible"], 2)
                assert stage["expected"] == expected
                if stage["visible"] != expected:
                    calibration.append(record)
            if any(stage[name] != expected for name in ["first", "second", "third"]):
                bad.append(record)
            if not stage["first"] == stage["second"] == stage["third"]:
                repeated.append(record)
    assert seen == roster
    return {"rows": len(rows), "stages": 5 * len(rows), "bad": bad,
            "repeat_changes": repeated, "calibration_failures": calibration}

inputs = load(SOURCE / "INPUTS.json")
assert digest(SOURCE / "INPUTS.json") == "7af013bedfc8f58e972915c6abed38303f6e5267cea65cfb89d89cd29313bb15"
for name, pin in inputs["pins"].items():
    assert digest(SOURCE / name) == pin
before, final, state = (load(SOURCE / name) for name in ["BEFORE.json", "FINAL.json", "STATE.json"])
assert before == final and before["sources"] == inputs["source_pins"]
assert len(before["sources"]) == 25 and set(before["sources"]) == set(inputs["paths"])
for key in ["head", "index_diff_sha256", "index_entries_sha256"]:
    assert before[key] == inputs[key]
assert state["status"] == "terminal" and state["restored"] and not state["recovery_errors"]
assert state["restore_build_exit"] == 0 and "failure" not in state
results, traces, used = {}, {}, {}
for phase, expected_counts in [("baseline", [32, 12]), ("key-omitted", [0, 12]), ("repair", [0, 4]), ("skipped-children", [0, 0])]:
    results[phase] = {}
    phase_state = state["phases"][phase]
    assert all(phase_state[k] == 0 for k in ["build_exit", "probe_exit", "shrink_probe_exit"])
    for index, subdir in enumerate(["project", "shrink/project"]):
        result_path = SOURCE / phase / subdir / "RESULT.json"
        raw = load(result_path)
        used[str(result_path.relative_to(ROOT))] = digest(result_path)
        assert raw["stable"] is True and raw["before"] == raw["after"] and raw["profile_removed"] is True
        assert len(raw["observations"]) == 1
        for name, pin in inputs["source_pins"].items():
            expected = digest(SOURCE / phase / name) if name == "layout/generic/nsFlexContainerFrame.cpp" else pin
            assert raw["before"][str(ROOT / name)] == expected
        assert raw["before"][str(SOURCE / "INPUTS.json")] == digest(SOURCE / "INPUTS.json")
        for name in ["probe.html", "probe.js", "run_browser.py"]:
            path = result_path.parent.parent / name
            assert raw["before"][str(path)] == digest(path)
        record = reconstruct(raw["observations"][0], bool(index))
        assert len(record["bad"]) == expected_counts[index]
        assert not record["repeat_changes"] and not record["calibration_failures"]
        record["binary_pins"] = {k: v for k, v in raw["before"].items() if k.endswith("/firefox") or k.endswith("/XUL")}
        record["browser_termination_exit"] = raw["exit_after_termination"]
        results[phase][subdir] = record
        log = result_path.parent / "browser.log"
        used[str(log.relative_to(ROOT))] = digest(log)
        lines = log.read_text().splitlines()
        for i, line in enumerate(lines):
            if "[hidden-measure-before] dirty=0 hidden=1" not in line:
                continue
            identity = line.split("[hidden-measure-before]")[0]
            if i + 1 < len(lines) and lines[i + 1].startswith(identity + "[hidden-measure-after]"):
                traces[phase + "/" + subdir] = {"first_line": i - 1, "excerpt": lines[max(0, i-2):i+2]}
                break
    log = SOURCE / (phase + "-build.log")
    assert "Your build was successful!" in log.read_text()
    used[str(log.relative_to(ROOT))] = digest(log)
assert "Your build was successful!" in (SOURCE / "restore-build.log").read_text()
receipt = {"results": results, "trace_excerpts": traces, "used_hashes": used,
           "restoration": {"sources": 25, "head_index_before_equals_final": True, "restore_build_exit": 0},
           "runtime_rerun": False}
(HERE / "RECOUNT.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({p: {s: len(x["bad"]) for s, x in values.items()} for p, values in results.items()}, indent=2))
