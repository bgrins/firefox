import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "layout/generic/nsFlexContainerFrame.cpp"
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def command(name, args):
    with (HERE / (name + ".log")).open("w") as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    return result.returncode


def save():
    (HERE / "STATE.json").write_text(json.dumps(state, indent=2) + "\n")


baseline = json.loads((HERE / "baseline/RESULT.json").read_text())
assert baseline["stable"] and len(baseline["observations"][0]["rows"]) == 30
before = SOURCE.read_bytes()
assert hashlib.sha256(before).hexdigest() == baseline["after"][str(SOURCE)]
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
(HERE / "before.cpp").write_bytes(before)
state = {"status": "building", "accepted": False}
save()
try:
    patch = HERE / "native-only.patch"
    pins = json.loads((HERE / "INPUT.json").read_text())
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == pins["native-only.patch"]
    git("apply", "--check", str(patch))
    git("apply", str(patch))
    (HERE / "candidate.cpp").write_bytes(SOURCE.read_bytes())
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    save()
    if state["candidate_build_exit"] == 0:
        state["candidate_browser_exit"] = command("candidate-driver", ["python3", "-I", "-S", str(HERE / "run_browser.py"), "candidate"])
finally:
    state["status"] = "restoring"
    save()
    if SOURCE.read_bytes() != before:
        SOURCE.write_bytes(before)
    state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = SOURCE.read_bytes() == before
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal"
    save()
    print(json.dumps(state, indent=2))
    assert state["restore_build_exit"] == 0
    assert all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
