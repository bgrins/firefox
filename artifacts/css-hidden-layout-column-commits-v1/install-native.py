import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
kind = sys.argv[1]
assert kind in ["principal", "absolute"]
package = ROOT / "artifacts/css-hidden-layout-native-packaging-v1"
overlay = ROOT / "artifacts/css-hidden-layout-worktree-overlay-v1"
for directory, expected in [
    (package, "4391cfe61097a7048a5a7bce2dc7b208aefe4c434d9e89f17c0ba6590ccf31b2"),
    (overlay, "523ce10a5d730f111b61c0d776f854d551e55c3ce867d8803b2867f5431ae7cb"),
]:
    assert hashlib.sha256((directory / "FILES.json").read_bytes()).hexdigest() == expected
    for name, digest in json.loads((directory / "FILES.json").read_text()).items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
bindings = json.loads((package / "BINDINGS.json").read_text())["recipes"][kind]
overlays = json.loads((overlay / "BINDINGS.json").read_text())["bindings"]
selected = next(r for r in overlays if r["kind"] == kind)
expected = json.loads((ROOT / "artifacts/css-hidden-layout-column-runtime-v1/BEFORE.json").read_text())["sources"]
if kind == "absolute":
    principal = next(r for r in overlays if r["kind"] == "principal")
    expected[principal["path"]] = principal["after_sha256"]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot():
    return {name: digest(ROOT / name) for name in expected}

env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
git = ["git", "-c", "core.fsmonitor=false"]
assert not subprocess.check_output(git + ["diff", "--cached", "--name-only"], cwd=ROOT, env=env)
assert snapshot() == expected
native = ROOT / selected["path"]
original = native.read_bytes()
for binding in bindings:
    assert digest(ROOT / binding["final_source"]) == binding["after_sha256"]
    if binding["before_blob"] is None:
        target = ROOT / binding["path"]
        assert not target.exists() and not target.is_symlink()
    else:
        actual = subprocess.check_output(git + ["rev-parse", "HEAD:" + binding["path"]], cwd=ROOT, env=env).decode().strip()
        assert actual == binding["before_blob"]
patch = overlay / (kind + "-worktree.patch")
subprocess.run(git + ["apply", "--check", str(patch)], cwd=ROOT, env=env, check=True)
installed = []
try:
    subprocess.run(git + ["apply", str(patch)], cwd=ROOT, env=env, check=True)
    for binding in bindings:
        if binding["before_blob"] is None:
            target = ROOT / binding["path"]
            with target.open("xb") as stream:
                installed.append(target)
                stream.write((ROOT / binding["final_source"]).read_bytes())
    after = dict(expected)
    after[selected["path"]] = selected["after_sha256"]
    assert snapshot() == after
    assert all(digest(ROOT / r["path"]) == r["after_sha256"] for r in bindings if r["before_blob"] is None)
except BaseException:
    native.write_bytes(original)
    for target in installed:
        target.unlink()
    raise
record = {"kind": kind, "before": expected, "after": after,
          "installed_tests": [str(p.relative_to(ROOT)) for p in installed],
          "prototype_bytes_preserved": True}
(HERE / (kind + "-installation.json")).write_text(json.dumps(record, indent=2) + "\n")
print(kind + ": exact worktree overlay and tested WPTs installed; index unchanged")
