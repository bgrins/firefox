import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]
NATIVE = "servo/components/style/custom_properties_map.rs"
TESTS = ["testing/web-platform/tests/css/css-variables/" + name for name in [
    "invalid-custom-property-enumeration.html",
    "custom-property-enumeration-shadowing.html",
    "resurrected-custom-property-enumeration.html",
]]


def git(args, env=None):
    return subprocess.check_output(GIT + args, cwd=ROOT, env=env)


head = git(["rev-parse", "HEAD"]).decode().strip()
upstream = git(["rev-parse", "976279105b2e78b8666a959eb3f25c9176cefaf8"]).decode().strip()
patch_pins = json.loads((HERE / "PATCH-PINS.json").read_text())
for name, pin in patch_pins.items():
    assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == pin
records = []
assert not git(["diff", "--cached", "--name-only"]).strip()
for base in [head, upstream]:
    assert git(["show", base + ":" + NATIVE]) == (HERE / "source/original.rs").read_bytes()
    for mode, patches, native, tests in [
        ("count", ["count-native-wpt.patch"], "count-only", TESTS[:1]),
        ("ordered-stack", ["count-native-wpt.patch", "iterator-native-wpt.patch"], "combined", TESTS),
        ("standalone-iterator", ["iterator-standalone-native-wpt.patch"], "combined", TESTS),
    ]:
        with tempfile.TemporaryDirectory(prefix="css-map-packaging-") as directory:
            env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
            git(["read-tree", base], env)
            for patch in patches:
                git(["apply", "--cached", "--check", str(HERE / patch)], env)
                git(["apply", "--cached", str(HERE / patch)], env)
            roster = git(["diff", "--cached", "--name-only", base], env).decode().splitlines()
            assert sorted(roster) == sorted([NATIVE] + tests)
            expected = {NATIVE: (HERE / "source" / (native + ".rs")).read_bytes()}
            expected.update({name: (ROOT / name).read_bytes() for name in tests})
            for name, data in expected.items():
                assert git(["show", ":" + name], env) == data
            git(["diff", "--cached", "--check", base], env)
            tree = git(["write-tree"], env).decode().strip()
            for patch in reversed(patches):
                git(["apply", "--cached", "--reverse", str(HERE / patch)], env)
            assert git(["write-tree"], env) == git(["rev-parse", base + "^{tree}"])
            records.append({"base": base, "mode": mode, "patches": patches,
                            "files": sorted(roster), "tree": tree,
                            "exact_blobs_and_reverse": True})
assert not git(["diff", "--cached", "--name-only"]).strip()
(HERE / "STANDALONE-PACKAGING.json").write_text(json.dumps({
    "checks": records, "patch_pins": patch_pins,
    "scope": "Temporary-index apply/reverse and complete blob checks; no isolated upstream build or browser execution."
}, indent=2) + "\n")
print("Six exact packaging checks passed; primary index unchanged.")
