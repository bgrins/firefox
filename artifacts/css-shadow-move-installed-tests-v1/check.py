import hashlib
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
CAPSULE = ROOT / "artifacts/css-shadow-move-promotion-v1"
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(CAPSULE / "FILES.json") == "6f7f6caab9e048718f32cb65920f9301da5b970c44eb5264cfbaefaec2aa5b6c"
for name, digest in json.loads((CAPSULE / "FILES.json").read_text()).items():
    assert sha(CAPSULE / name) == (digest["sha256"] if isinstance(digest, dict) else digest)
policy = json.loads((CAPSULE / "POLICY.json").read_text())
paths = []
pins = {}
for name, record in policy["tests"].items():
    assert sha(ROOT / name) == sha(ROOT / record["capture"]) == record["sha256"]
    paths.append(str((ROOT / name).relative_to(WPT)))
    pins[name] = record["sha256"]
assert len(paths) == 4
assert not (ROOT / policy["deleted_metadata"]["path"]).exists()
assert not (ROOT / policy["preserved_absent_metadata"]).exists()
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT)]
sys.path.insert(0, str(ROOT / "third_party/python/PyYAML/lib"))
from manifest.manifest import Manifest
from tools.lint import lint

manifest = Manifest(str(WPT), "/")
manifest.update([(name, None, True) for name in sorted(paths)], parallel=False)
serialized = json.loads(json.dumps(manifest.to_json()))
for name in paths:
    node = serialized["items"]["testharness"]
    for part in name.split("/"):
        node = node[part]
    assert len(node) == 2 and node[1][0] is None
os.chdir(WPT)
errors = lint.lint(str(WPT), sorted(paths), "normal", jobs=1)
assert errors == 0
assert all(sha(ROOT / name) == digest for name, digest in pins.items())
report = {"installed_pages": 4, "landing_callbacks": 29, "lint_errors": errors,
          "genuine_manifest_testharness_pages": 4, "installed_bytes_match_captures": pins,
          "browser_execution": False, "native_fix_acceptance": False}
with (HERE / "RESULT.json").open("x") as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write("\n")
with (HERE / "MANIFEST.json").open("x") as stream:
    json.dump(serialized, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps(report, sort_keys=True))
