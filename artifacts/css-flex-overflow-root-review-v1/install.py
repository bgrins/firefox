import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVIDENCE = ROOT / "artifacts/css-flex-overflow-container-fix-v1"
SOURCE = ROOT / "layout/generic/nsFlexContainerFrame.cpp"
TEST = ROOT / "testing/web-platform/tests/css/css-flexbox/flexbox-overflow-container-final-position.html"
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def build(name):
    with (HERE / (name + ".log")).open("w") as log:
        return subprocess.run(["./mach", "build", "binaries"], cwd=ROOT, env=ENV,
                              stdout=log, stderr=subprocess.STDOUT).returncode


assert not TEST.exists()
before = SOURCE.read_bytes()
assert before == (EVIDENCE / "before.cpp").read_bytes()
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
state = {"status": "installing", "head": head.decode().strip(),
         "index_diff_sha256": hashlib.sha256(index).hexdigest()}
success = False
try:
    patch = EVIDENCE / "native-only.patch"
    git("apply", "--check", str(patch))
    git("apply", str(patch))
    assert SOURCE.read_bytes() == (EVIDENCE / "candidate.cpp").read_bytes()
    TEST.write_bytes((EVIDENCE / TEST.name).read_bytes())
    state["build_exit"] = build("installed-build")
    assert state["build_exit"] == 0
    assert SOURCE.read_bytes() == (EVIDENCE / "candidate.cpp").read_bytes()
    assert TEST.read_bytes() == (EVIDENCE / TEST.name).read_bytes()
    success = True
finally:
    if not success:
        SOURCE.write_bytes(before)
        TEST.unlink(missing_ok=True)
        state["restore_build_exit"] = build("failed-install-restoration")
    state["installed"] = success
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    state["test_sha256"] = hashlib.sha256(TEST.read_bytes()).hexdigest() if TEST.exists() else None
    state["status"] = "terminal"
    (HERE / "INSTALL.json").write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps(state, indent=2))
    assert state["head_unchanged"] and state["index_unchanged"]
