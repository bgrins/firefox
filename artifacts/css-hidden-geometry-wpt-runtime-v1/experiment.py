import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = json.loads((HERE / "INPUTS.json").read_text())
CONFIG = json.loads((HERE / "CONFIG.json").read_text())
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", GIT_OPTIONAL_LOCKS="0",
           GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.fsmonitor", GIT_CONFIG_VALUE_0="false")
ENV.pop("MOZ_LOG", None)
GIT = ["git", "-c", "core.fsmonitor=false"]
SOURCE = "layout/generic/nsFlexContainerFrame.cpp"
PHASES = ["baseline", "candidate", "original-key", "original-key-candidate"]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")

def snapshot():
    return {"head": git("rev-parse", "HEAD").decode().strip(),
            "index_diff_sha256": sha(git("diff", "--cached", "--binary")),
            "index_entries_sha256": sha(git("ls-files", "--stage", "-z")),
            "sources": {p: sha((ROOT / p).read_bytes()) for p in INPUTS["source_pins"]}}

assert not (HERE / "BEFORE.json").exists()
for name, pin in INPUTS["payload_pins"].items():
    assert sha((HERE / name).read_bytes()) == pin, name
for name, pin in INPUTS["test_pins"].items():
    assert sha((ROOT / name).read_bytes()) == pin, name
before = snapshot()
assert before == INPUTS["before"]
assert not git("diff", "--cached", "--name-only").strip()
for path in CONFIG["sources"]:
    assert (ROOT / path).read_bytes() == (HERE / "original" / path).read_bytes()
    assert git("show", "HEAD:" + path) == (HERE / "head" / path).read_bytes()
original = {p: (ROOT / p).read_bytes() for p in CONFIG["sources"]}
original_tests = {p: (ROOT / p).read_bytes() if (ROOT / p).exists() else None
                  for p in CONFIG["install"]}
for target, source in CONFIG["install"].items():
    assert original_tests[target] in (None, (HERE / source).read_bytes()), target
spec = importlib.util.spec_from_file_location("wpt_run", HERE / "run_wpt.py")
wpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
save("BEFORE.json", before)
state = {"status": "starting", "accepted_native_repair": False, "phases": {}}
recovery_errors = []
changed = False

def recovery_save(name, value):
    try:
        save(name, value)
    except BaseException as error:
        recovery_errors.append({"operation": "save " + name, "error": repr(error)})

try:
    for target, source in CONFIG["install"].items():
        (ROOT / target).write_bytes((HERE / source).read_bytes())
    state["wpt_lint_exit"] = wpt.command("wpt-lint", ["./mach", "lint", "-l", "wpt", *CONFIG["install"]])
    assert state["wpt_lint_exit"] == 0
    for path in CONFIG["sources"]:
        changed = True
        (ROOT / path).write_bytes((HERE / "head" / path).read_bytes())
    for phase in PHASES:
        candidate = (HERE / "variants" / phase / "nsFlexContainerFrame.cpp").read_bytes()
        (ROOT / SOURCE).write_bytes(candidate)
        state["status"] = "building " + phase
        record = state["phases"][phase] = {}
        save("STATE.json", state)
        record["build_exit"] = wpt.command(phase + "-build", ["./mach", "build", "binaries"])
        assert record["build_exit"] == 0
        for path in INPUTS["source_pins"]:
            expected = (candidate if path == SOURCE else
                        (HERE / "head" / path).read_bytes() if path in CONFIG["sources"] else None)
            assert sha((ROOT / path).read_bytes()) == (sha(expected) if expected is not None else INPUTS["source_pins"][path]), path
        state["status"] = "testing " + phase
        save("STATE.json", state)
        record["wpt"] = wpt.test_run(phase)
        run = json.loads((HERE / phase / "RUN.json").read_text())
        for test, names in CONFIG["expected_new_subtests"].items():
            actual = [r["subtest"] for r in run["rows"] if r["test"] == test]
            assert sorted(actual) == sorted(names), (test, actual)
        record["status_counts"] = {status: sum(r["status"] == status for r in run["rows"])
                                    for status in sorted({r["status"] for r in run["rows"]})}
        record["failures"] = [{"test": r["test"], "subtest": r["subtest"], "status": r["status"]}
                              for r in run["rows"] if r["status"] != "PASS"]
        save("STATE.json", state)
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
finally:
    state["status"] = "restoring original sources"
    state["recovery_errors"] = recovery_errors
    recovery_save("STATE.json", state)
    for path, data in original.items():
        try:
            (ROOT / path).write_bytes(data)
        except BaseException as error:
            recovery_errors.append({"operation": "restore " + path, "error": repr(error)})
    for path, data in original_tests.items():
        try:
            if data is None:
                (ROOT / path).unlink(missing_ok=True)
            else:
                (ROOT / path).write_bytes(data)
        except BaseException as error:
            recovery_errors.append({"operation": "restore test " + path, "error": repr(error)})
    if changed:
        try:
            try:
                log = (HERE / "restore-build.log").open("w")
            except OSError as error:
                recovery_errors.append({"operation": "open restore build log", "error": repr(error)})
                log = None
            try:
                state["restore_build_exit"] = subprocess.run(["./mach", "build", "binaries"], cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT).returncode
            finally:
                if log is not None:
                    log.close()
        except BaseException as error:
            recovery_errors.append({"operation": "restore build", "error": repr(error)})
    state["restored"] = False
    try:
        final = snapshot()
        state["restored"] = final == before and all(
            ((ROOT / p).read_bytes() if (ROOT / p).exists() else None) == data
            for p, data in original_tests.items())
        recovery_save("FINAL.json", final)
    except BaseException as error:
        recovery_errors.append({"operation": "final state", "error": repr(error)})
    state["status"] = "terminal"
    recovery_save("STATE.json", state)
print(json.dumps(state, indent=2))
if "failure" in state or recovery_errors or not state["restored"] or (changed and state.get("restore_build_exit") != 0):
    raise SystemExit(1)
