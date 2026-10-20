import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = json.loads((HERE / "INPUTS.json").read_text())
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")

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

def command(label, args):
    with (HERE / (label + ".log")).open("w") as log:
        code = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT).returncode
    return code

assert not (HERE / "BEFORE.json").exists()
for name, expected in INPUTS["pins"].items():
    assert sha((HERE / name).read_bytes()) == expected, name
before = state_snapshot()
for key in ["head", "index_diff_sha256", "index_entries_sha256"]:
    assert before[key] == INPUTS[key], key
assert len(git("diff", "--cached", "--name-only").decode().splitlines()) == INPUTS["staged_paths"] == 229
for name in INPUTS["paths"]:
    assert (ROOT / name).read_bytes() == (HERE / "original" / name).read_bytes(), name
    assert git("show", "HEAD:" + name) == (HERE / "head" / name).read_bytes(), name
save("BEFORE.json", before)
state = {"status": "starting", "accepted_native_bug": False}
save("STATE.json", state)
changed = False
try:
    for name in INPUTS["paths"]:
        changed = True
        (ROOT / name).write_bytes((HERE / "head" / name).read_bytes())
    state["status"] = "building exact committed native sources"
    save("STATE.json", state)
    state["head_build_exit"] = command("head-build", ["./mach", "build", "binaries"])
    assert state["head_build_exit"] == 0
    assert not git("diff", "--name-only", "--", "layout", "dom", "servo").strip()
    for name in INPUTS["paths"]:
        assert (ROOT / name).read_bytes() == (HERE / "head" / name).read_bytes(), name
    state["status"] = "probing exact committed native sources"
    save("STATE.json", state)
    state["probe_exit"] = command("head-probe", [sys.executable, "-I", "-S", "-B", str(HERE / "case/run_browser.py"), "project"])
    assert state["probe_exit"] == 0
    result = json.loads((HERE / "case/project/RESULT.json").read_text())
    assert result["stable"] and len(result["observations"]) == 1
    rows = result["observations"][0]["rows"]
    assert len(rows) == 32 and "error" not in result["observations"][0]
    bad = [{**{k: v for k, v in r.items() if k != "stages"}, **s}
           for r in rows for s in r["stages"] if s["first"] not in ([24, 32], [[24, 32]])]
    save("OBSERVATIONS.json", {"rows": len(rows), "stages": sum(len(r["stages"]) for r in rows), "bad_stages": bad})
    state["bad_stages"] = len(bad)
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
    raise
finally:
    state["status"] = "restoring prototypes"
    save("STATE.json", state)
    for name in INPUTS["paths"]:
        original = (HERE / "original" / name).read_bytes()
        if (ROOT / name).read_bytes() != original:
            (ROOT / name).write_bytes(original)
    if changed:
        state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    final = state_snapshot()
    save("FINAL.json", final)
    state["restored"] = final == before
    save("STATE.json", state)
    assert state["restored"] and (not changed or state["restore_build_exit"] == 0)
state["status"] = "terminal"
save("STATE.json", state)
print(json.dumps(state, indent=2))
