import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "layout/generic/nsFlexContainerFrame.cpp"
TEST = ROOT / "testing/web-platform/tests/css/css-flexbox/flexbox-overflow-container-final-position.html"
PRIOR = ROOT / "artifacts/css-flex-overflow-container-fix-v1"
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def command(name, args):
    with (HERE / (name + ".log")).open("w") as stream:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
    return {"command": args, "exit": result.returncode}


assert not TEST.exists()
before = SOURCE.read_bytes()
assert before == (HERE / "baseline.cpp").read_bytes()
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
state = {"accepted": False}
try:
    patch = PRIOR / "native-only.patch"
    git("apply", "--check", str(patch))
    git("apply", str(patch))
    unformatted = SOURCE.read_bytes()
    assert unformatted == (HERE / "unformatted.cpp").read_bytes()
    state["format"] = command("live-format", ["./mach", "lint", "-l", "clang-format", "--fix", str(SOURCE)])
    (HERE / "live-formatted.cpp").write_bytes(SOURCE.read_bytes())
    state["format_changed_bytes"] = SOURCE.read_bytes() != unformatted
    TEST.write_bytes((PRIOR / TEST.name).read_bytes())
    state["wpt_lint"] = command("wpt-lint", ["./mach", "lint", "--include-third-party", str(TEST)])
    state["test_unchanged"] = TEST.read_bytes() == (PRIOR / TEST.name).read_bytes()
finally:
    SOURCE.write_bytes(before)
    TEST.unlink(missing_ok=True)
    state["source_restored"] = SOURCE.read_bytes() == before
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal"
    (HERE / "RESULT.json").write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps(state, indent=2))
    assert all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
