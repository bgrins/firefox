import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ["git", "-c", "core.fsmonitor=false"]
PATHS = ["layout/generic/nsFlexContainerFrame.cpp", "layout/generic/nsContainerFrame.cpp"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def command(name, args):
    with (HERE / (name + ".log")).open("w") as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    save(name + ".json", {"command": args, "exit": result.returncode})
    return result.returncode


head = git("rev-parse", "HEAD").decode().strip()
index = git("diff", "--cached", "--binary")
before = {name: (ROOT / name).read_bytes() for name in PATHS}
for name, data in before.items():
    target = HERE / "before" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
save("BEFORE.json", {"head": head, "index_diff_sha256": hashlib.sha256(index).hexdigest(),
                     "source": {name: hashlib.sha256(data).hexdigest() for name, data in before.items()}})
state = {"status": "applying candidate and diagnostic", "accepted": False}
save("STATE.json", state)
try:
    git("apply", "--check", str(HERE / "native-only.patch"))
    git("apply", str(HERE / "native-only.patch"))
    assert command("instrument", ["python3", str(HERE / "instrument.py")]) == 0
    for name in PATHS:
        target = HERE / "instrumented" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    state["status"] = "building diagnostic"
    save("STATE.json", state)
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    if state["candidate_build_exit"] == 0:
        state["status"] = "running diagnostic"
        save("STATE.json", state)
        state["diagnostic_exit"] = command("diagnostic", ["python3", "-I", "-S", str(HERE / "run_browser.py"), "project"])
finally:
    state["status"] = "restoring source and build"
    save("STATE.json", state)
    for name, data in before.items():
        path = ROOT / name
        if path.read_bytes() != data:
            path.write_bytes(data)
    state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = all((ROOT / name).read_bytes() == data for name, data in before.items())
    state["head_unchanged"] = git("rev-parse", "HEAD").decode().strip() == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal"
    save("STATE.json", state)
    print(json.dumps(state, indent=2))
    assert state["restore_build_exit"] == 0 and all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
