import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / "artifacts/css-custom-properties-animation-taint-repair-v1"
BASE = "976279105b2e78b8666a959eb3f25c9176cefaf8"
FILES = ["servo/components/style/properties_and_values/value.rs", "servo/ports/geckolib/glue.rs",
         "dom/animation/KeyframeEffect.cpp"]
MAP = "servo/components/style/custom_properties_map.rs"
TEST = "testing/web-platform/tests/css/css-values/animation-csswide-equal-payload-taint.html"
GIT = ["git", "-c", "core.fsmonitor=false"]


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


head = git("rev-parse", "HEAD").decode().strip()
assert not git("diff", "--cached", "--name-only").strip()
formatting = json.loads((HERE / "FORMAT-TRANSFER.json").read_text())
manifest = json.loads((PROPOSAL / "MANIFEST.json").read_text())
records = {}
for variant, base, folder, paths in [
    ("stack", head, "candidate", FILES),
    ("standalone", BASE, "standalone", FILES + [MAP]),
]:
    patch = ""
    pins = {}
    for name in paths:
        before = git("show", base + ":" + name)
        old_folder = "original" if variant == "stack" else "upstream"
        assert sha(before) == manifest["source/" + old_folder + "/" + name]
        after = (PROPOSAL / "source" / folder / name).read_bytes()
        assert sha(after) == manifest["source/" + folder + "/" + name]
        if name == formatting["path"]:
            old, new = formatting["old"].encode(), formatting["new"].encode()
            assert after.count(old) == 1
            after = after.replace(old, new)
        if variant == "stack":
            assert after == (ROOT / name).read_bytes()
        pins[name] = sha(after)
        patch += "".join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True), fromfile="a/" + name, tofile="b/" + name))
    test = (PROPOSAL / "csswide-endpoint-taint.html").read_bytes()
    assert test == (ROOT / TEST).read_bytes()
    assert not git("ls-tree", base, "--", TEST).strip()
    pins[TEST] = sha(test)
    patch += "".join(difflib.unified_diff([], test.decode().splitlines(True), fromfile="/dev/null", tofile="b/" + TEST))
    patch_path = HERE / (variant + "-native-wpt.patch")
    patch_path.write_text(patch)
    with tempfile.TemporaryDirectory(prefix="animation-package-", dir="/private/tmp") as scratch:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(scratch) / "index")}
        git("read-tree", base, env=env)
        git("apply", "--cached", "--check", str(patch_path), env=env)
        git("apply", "--cached", str(patch_path), env=env)
        actual = git("diff", "--cached", "--name-only", base, env=env).decode().splitlines()
        assert sorted(actual) == sorted(pins)
        for name, digest in pins.items():
            assert sha(git("show", ":" + name, env=env)) == digest
        tree = git("write-tree", env=env).decode().strip()
        git("apply", "--cached", "--reverse", str(patch_path), env=env)
        assert git("write-tree", env=env).strip() == git("rev-parse", base + "^{tree}").strip()
    records[variant] = {"base": base, "patch": str(patch_path.relative_to(ROOT)), "sha256": sha(patch_path.read_bytes()),
                        "paths": sorted(pins), "pins": pins, "candidate_tree": tree, "exact_apply_reverse": True}
assert git("rev-parse", "HEAD").decode().strip() == head
assert not git("diff", "--cached", "--name-only").strip()
records["standalone_runtime"] = "Not run on isolated upstream; source application and prerequisites reviewed."
records["dependency"] = "Stack needs fix76 map do_insert support. Standalone includes precisely that one-site prerequisite; no universal cascade shortcut or fix70 typed-keyframe provider."
(HERE / "PACKAGING.json").write_text(json.dumps(records, indent=2) + "\n")
print("Four-file stack and five-file standalone patches apply and reverse exactly")
