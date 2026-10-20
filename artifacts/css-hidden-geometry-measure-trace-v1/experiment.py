import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = json.loads((HERE / "INPUTS.json").read_text())
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1", MOZ_LOG="FlexContainer:5")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT, env=ENV)

def state_snapshot():
    return {"head": git("rev-parse", "HEAD").decode().strip(),
            "index_diff_sha256": sha(git("diff", "--cached", "--binary")),
            "index_entries_sha256": sha(git("ls-files", "--stage", "-z")),
            "sources": {n: sha((ROOT / n).read_bytes()) for n in INPUTS["paths"]}}

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")

def command(label, args, recovery=False):
    try:
        log = (HERE / (label + ".log")).open("w")
    except OSError as error:
        if not recovery:
            raise
        recovery_errors.append({"operation": "open " + label + " log", "error": repr(error)})
        return subprocess.run(args, cwd=ROOT, env=ENV, stderr=subprocess.STDOUT).returncode
    with log:
        return subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT).returncode


def validate_rows(observation):
    assert set(observation) == {"rows", "userAgent"}
    assert isinstance(observation["userAgent"], str)
    rows = observation["rows"]
    assert isinstance(rows, list) and len(rows) == 32
    expected = {(columns, flex, hidden, api)
                for columns in (False, True) for flex in (False, True)
                for hidden in (False, True)
                for api in ("bounding", "rects", "offset", "scroll")}
    seen = set()
    phases = ["initial", "hide", "append", "append-again", "show"]
    def vector(value, size):
        return (isinstance(value, list) and len(value) == size and
                all(type(n) in (int, float) and math.isfinite(n) for n in value))
    for row in rows:
        assert set(row) == {"columns", "flex", "initiallyHidden", "api", "stages"}
        assert all(type(row[k]) is bool for k in ("columns", "flex", "initiallyHidden"))
        key = (row["columns"], row["flex"], row["initiallyHidden"], row["api"])
        assert key in expected and key not in seen
        seen.add(key)
        stages = row["stages"]
        assert isinstance(stages, list) and len(stages) == 5
        assert [s["phase"] for s in stages] == phases
        for stage in stages:
            assert set(stage) == {"phase", "outer", "first", "second", "third"}
            assert vector(stage["outer"], 3)
            for read in ("first", "second", "third"):
                value = stage[read]
                if row["api"] == "rects":
                    assert isinstance(value, list) and all(vector(r, 2) for r in value)
                else:
                    assert vector(value, 2)
    assert seen == expected
    return rows


def recovery_save(name, value):
    try:
        save(name, value)
    except BaseException as error:
        recovery_errors.append({"operation": "save " + name, "error": repr(error)})

assert not (HERE / "BEFORE.json").exists()
for name, expected in INPUTS["pins"].items():
    assert sha((HERE / name).read_bytes()) == expected, name
spec = importlib.util.spec_from_file_location("shrink_validation", HERE / "shrink-validate.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
before = state_snapshot()
for key in ["head", "index_diff_sha256", "index_entries_sha256"]:
    assert before[key] == INPUTS[key], key
assert not git("diff", "--cached", "--name-only").strip()
assert before["sources"] == INPUTS["source_pins"]
source_path = "layout/generic/nsFlexContainerFrame.cpp"
original = (HERE / "original" / source_path).read_bytes()
assert (ROOT / source_path).read_bytes() == original
for phase in ["baseline", "key-omitted", "repair"]:
    assert not (HERE / phase / "project").exists()
    assert not (HERE / phase / "shrink/project").exists()
save("BEFORE.json", before)
state = {"status": "starting", "accepted_native_bug": False, "phases": {}}
recovery_errors = []
changed = False
try:
    for phase in ["baseline", "key-omitted", "repair"]:
        changed = True
        candidate = (HERE / phase / source_path).read_bytes()
        (ROOT / source_path).write_bytes(candidate)
        state["status"] = "building " + phase
        save("STATE.json", state)
        record = state["phases"][phase] = {}
        record["build_exit"] = command(phase + "-build", ["./mach", "build", "binaries"])
        assert record["build_exit"] == 0
        assert (ROOT / source_path).read_bytes() == candidate
        for name, pin in INPUTS["source_pins"].items():
            if name != source_path:
                assert sha((ROOT / name).read_bytes()) == pin, name
        state["status"] = "probing " + phase
        save("STATE.json", state)
        record["probe_exit"] = command(phase + "-probe", [sys.executable, "-I", "-S", "-B", str(HERE / phase / "run_browser.py"), "project"])
        assert record["probe_exit"] == 0
        result = json.loads((HERE / phase / "project/RESULT.json").read_text())
        assert result["stable"] is True and len(result["observations"]) == 1
        rows = validate_rows(result["observations"][0])
        bad = [{**{k: v for k, v in r.items() if k != "stages"}, **s}
               for r in rows for s in r["stages"]
               if any(s[k] not in ([24, 32], [[24, 32]]) for k in ["first", "second", "third"])]
        save(phase + "-OBSERVATIONS.json", {"rows": len(rows), "stages": sum(len(r["stages"]) for r in rows), "bad_stages": bad})
        record["bad_stages"] = len(bad)
        record["shrink_probe_exit"] = command(phase + "-shrink-probe", [sys.executable, "-I", "-S", "-B", str(HERE / phase / "shrink/run_browser.py"), "project"])
        assert record["shrink_probe_exit"] == 0
        shrink = json.loads((HERE / phase / "shrink/project/RESULT.json").read_text())
        assert shrink["stable"] is True and len(shrink["observations"]) == 1
        summary = validation.summarize(shrink["observations"][0])
        save(phase + "-SHRINK-OBSERVATIONS.json", summary)
        assert not summary["calibration_failures"]
        record["shrink_bad_stages"] = len(summary["differences"])
        record["shrink_repeated_changes"] = len(summary["repeated_changes"])
        save("STATE.json", state)
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
finally:
    state["status"] = "restoring original source"
    state["recovery_errors"] = recovery_errors
    recovery_save("STATE.json", state)
    try:
        (ROOT / source_path).write_bytes(original)
    except BaseException as error:
        recovery_errors.append({"operation": "restore " + source_path, "error": repr(error)})
    if changed:
        try:
            state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"], recovery=True)
        except BaseException as error:
            recovery_errors.append({"operation": "restore build", "error": repr(error)})
    state["restored"] = False
    try:
        final = state_snapshot()
        state["restored"] = final == before
        recovery_save("FINAL.json", final)
    except BaseException as error:
        recovery_errors.append({"operation": "final state", "error": repr(error)})
    state["status"] = "terminal"
    recovery_save("STATE.json", state)
print(json.dumps(state, indent=2))
if ("failure" in state or recovery_errors or not state["restored"] or
        (changed and state.get("restore_build_exit") != 0)):
    raise SystemExit(1)
