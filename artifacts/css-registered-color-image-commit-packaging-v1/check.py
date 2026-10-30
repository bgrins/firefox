import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
info = json.loads((HERE / "SOURCE-DEPENDENCIES.json").read_text())
for name, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / name) == expected
roles = info["roles"]
scratch = Path(tempfile.mkdtemp(prefix="color-image-stack-", dir="/private/tmp"))
logs = []

def write_base():
    for name, role in roles["A"].items():
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / role["source"]).read_bytes())

def apply(path, reverse=False, success=True):
    command = ["/usr/bin/patch", "-f", "-F", "0", "-p1", "-i", str(path)]
    if reverse:
        command.append("-R")
    result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
    logs.append({"patch": str(path.relative_to(ROOT)), "reverse": reverse, "exit": result.returncode, "output": result.stdout + result.stderr})
    assert (result.returncode == 0) == success

def verify(key):
    for name, role in roles[key].items():
        assert sha(scratch / name) == role["candidate_sha256"]

try:
    write_base()
    apply(HERE / "01-union-native.patch")
    verify("A")
    apply(HERE / "02-tested-combined-after-union.patch")
    verify("combined")
    apply(HERE / "02-tested-combined-after-union.patch", reverse=True)
    verify("A")
    apply(HERE / "02-narrow-image-after-union.patch")
    for name, expected in info["narrow_postimages"].items():
        assert sha(scratch / name) == expected
    apply(HERE / "02-narrow-image-after-union.patch", reverse=True)
    apply(HERE / "01-union-native.patch", reverse=True)
    for name, role in roles["A"].items():
        assert sha(scratch / name) == role["base_sha256"]
    apply(HERE / "narrow-combined-native.patch")
    for name, expected in info["narrow_postimages"].items():
        assert sha(scratch / name) == expected
    apply(HERE / "narrow-combined-native.patch", reverse=True)
    image_patch = ROOT / "artifacts" / info["packages"]["B"] / "native.patch"
    apply(image_patch)
    verify("B")
    apply(HERE / "alternative-union-after-image.patch")
    verify("combined")
    write_base()
    apply(HERE / "01-union-native.patch")
    apply(image_patch, success=False)
    for patch, package, filename in [
        ("01-union-wpt.patch", "css-registered-color-scheme-dependency-review-v1", "registered-ident-color-scheme-dependency.tentative.html"),
        ("02-image-wpt.patch", "css-registered-image-unit-probe-v1", "registered-image-font-dependencies.tentative.html"),
    ]:
        target = scratch / "testing/web-platform/tests/css/css-properties-values-api" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        apply(HERE / patch)
        original = ROOT / "artifacts" / package / "tests/css/css-properties-values-api" / filename
        assert target.read_bytes() == original.read_bytes()
    formatter = "/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt"
    result = subprocess.run([formatter, "--check", "--config-path", str(HERE / "rustfmt.toml"), *[str(HERE / "narrow-candidate" / name) for name in roles["A"]]], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
result = {"tested_route_exact_combined": True, "narrow_route_exact_postimages": True, "narrow_equals_tested_combined": False, "reverse_routes": True, "standalone_image_patch_on_A_rejected": True, "unchanged_WPT_pages": 2, "narrow_formatted_files": 3, "scratch": str(scratch), "scratch_removed": True, "native_compile": False, "browser": False, "git": False, "patch_operations": logs}
(HERE / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({key: value for key, value in result.items() if key != "patch_operations"}))
