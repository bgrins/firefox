import hashlib
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "layout/base/nsLayoutUtils.cpp"
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}
GIT = ["git", "-c", "core.fsmonitor=false"]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def command(name, args):
    with (HERE / (name + ".log")).open("w") as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    save(name + ".json", {"command": args, "exit": result.returncode})
    return result.returncode


def measure(kind):
    for repeat in [1, 2]:
        name = kind + "-" + str(repeat)
        assert command(name + "-driver", ["python3", "-I", "-S", "-B", str(HERE / "run_browser.py"), name]) == 0


previous = ROOT / "artifacts/css-cssom-rectangle-standalone-runtime-v1"
assert json.loads((previous / "STATE.json").read_text())["status"] == "terminal"
restored = json.loads((previous / "RESTORED.json").read_text())
for name, expected in restored.items():
    assert sha(ROOT / name) == expected, name
before = SOURCE.read_bytes()
assert before == (ROOT / "artifacts/css-exact-size-observer-repair-proposal-v1/original/nsLayoutUtils.cpp").read_bytes()
assert (ROOT / "dom/base/DOMRect.cpp").read_bytes() == (ROOT / "artifacts/css-exact-size-observer-repair-proposal-v1/original/DOMRect.cpp").read_bytes()
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
assert not index
assert not (HERE / "BEFORE.json").exists()
(HERE / "original-nsLayoutUtils.cpp").write_bytes(before)
save("BEFORE.json", {"head": head.decode().strip(), "baseline": restored, "candidate": sha(HERE / "candidate-nsLayoutUtils.cpp")})
state = {"status": "baseline-before", "accepted": False}
save("STATE.json", state)
changed = False
try:
    measure("baseline-before")
    SOURCE.write_bytes((HERE / "candidate-nsLayoutUtils.cpp").read_bytes())
    changed = True
    state["format_check_exit"] = command("format-check", ["./mach", "lint", "-W", "-l", "clang-format", str(SOURCE.relative_to(ROOT))])
    assert state["format_check_exit"] == 0
    state["status"] = "building integer-only"
    save("STATE.json", state)
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    assert state["candidate_build_exit"] == 0
    state["status"] = "measuring integer-only"
    save("STATE.json", state)
    measure("integer-only")
finally:
    state["status"] = "restoring"
    save("STATE.json", state)
    if SOURCE.read_bytes() != before:
        SOURCE.write_bytes(before)
    if changed:
        state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = SOURCE.read_bytes() == before
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    save("STATE.json", state)
    assert not changed or state["restore_build_exit"] == 0
    assert all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
    save("RESTORED.json", {name: sha(ROOT / name) for name in restored})
state["status"] = "baseline-after"
save("STATE.json", state)
measure("baseline-after")
state["status"] = "terminal"
save("STATE.json", state)
print(json.dumps(state, indent=2))
