import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / "artifacts/css-animation-base-metadata-review-v1"
BASE = "976279105b2e78b8666a959eb3f25c9176cefaf8"
SOURCE = "dom/animation/KeyframeEffect.cpp"
TEST = "testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html"
GIT = ["git", "-c", "core.fsmonitor=false"]


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


head = git("rev-parse", "HEAD").decode().strip()
assert not git("diff", "--cached", "--name-only").strip()
assert sha((PROPOSAL / "FREEZE.json").read_bytes()) == "09cdff76fa3d0a2d1dcfd9f92d10ac12713dfeaf4be321173dfaaad73041a4ea"
assert sha((PROPOSAL / "MANIFEST.json").read_bytes()) == "c848ed15d26167fd3d6483ca868148fde3603631a8ca1cf2bc4be6409762f392"
for name, digest in json.loads((PROPOSAL / "MANIFEST.json").read_text()).items():
    assert sha((PROPOSAL / name).read_bytes()) == digest
records = {}
for variant, base, paths in [
    ("stack", head, [SOURCE]),
    ("standalone", BASE, [SOURCE, "servo/components/style/properties_and_values/value.rs", "servo/ports/geckolib/glue.rs"]),
]:
    pins = {}
    for name in paths:
        before = PROPOSAL / "KeyframeEffect.original.cpp" if variant == "stack" else PROPOSAL / "standalone/original" / name
        after = PROPOSAL / "KeyframeEffect.candidate.cpp" if variant == "stack" else PROPOSAL / "standalone/candidate" / name
        assert git("show", base + ":" + name) == before.read_bytes()
        pins[name] = sha(after.read_bytes())
        if variant == "stack":
            assert (ROOT / name).read_bytes() == after.read_bytes()
    assert (ROOT / TEST).read_bytes() == (PROPOSAL / "evidence/probe-v2.html").read_bytes()
    assert not git("ls-tree", base, "--", TEST).strip()
    pins[TEST] = sha((ROOT / TEST).read_bytes())
    patch = PROPOSAL / (variant + "-with-test.patch")
    with tempfile.TemporaryDirectory(prefix="base-animation-package-", dir="/private/tmp") as scratch:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(scratch) / "index")}
        git("read-tree", base, env=env)
        git("apply", "--cached", "--check", str(patch), env=env)
        git("apply", "--cached", str(patch), env=env)
        actual = git("diff", "--cached", "--name-only", base, env=env).decode().splitlines()
        assert sorted(actual) == sorted(pins)
        for name, digest in pins.items():
            assert sha(git("show", ":" + name, env=env)) == digest
        tree = git("write-tree", env=env).decode().strip()
        git("apply", "--cached", "--reverse", str(patch), env=env)
        assert git("write-tree", env=env).strip() == git("rev-parse", base + "^{tree}").strip()
    records[variant] = {"base": base, "patch": str(patch.relative_to(ROOT)), "sha256": sha(patch.read_bytes()),
                        "paths": sorted(pins), "pins": pins, "candidate_tree": tree, "exact_apply_reverse": True}
assert git("rev-parse", "HEAD").decode().strip() == head
assert not git("diff", "--cached", "--name-only").strip()
records["scope"] = "Stack reuses fix78 accessor; standalone includes getter and FFI, no endpoint-loop or map prerequisite. Actual isolated upstream build/browser not run."
(HERE / "PACKAGING.json").write_text(json.dumps(records, indent=2) + "\n")
print("Two-file stack and four-file standalone patches apply and reverse exactly")
