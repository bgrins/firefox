import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
here = Path(__file__).resolve().parent
root = here.parents[1]
sys.path.insert(0, str(root / "testing/web-platform/tests/tools"))
for name in ("atomicwrites", "html5lib", "webencodings", "six"):
    sys.path.insert(0, str(root / "testing/web-platform/tests/tools/third_party" / name))
from manifest.manifest import Manifest
selected = json.loads((here / "SELECTED.json").read_text())
source = here / "capture/testing/web-platform/tests"
manifest = Manifest(str(source), "/")
manifest.update([(name.lstrip("/"), None, True) for name in selected], parallel=False)
value = json.loads(json.dumps(manifest.to_json()))
path = here / "SUBSET-MANIFEST.json"
if path.exists():
    assert json.loads(path.read_text()) == value
else:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
loaded = Manifest.from_json(str(source), value)
actual = {item.id: kind for kind, _, items in loaded for item in items}
assert actual == selected and len(actual) == 2 and set(actual.values()) == {"testharness"}
(here / "MANIFEST-CHECK.json").write_text(json.dumps({"genuine_manifest_generated_and_loaded": True, "selected": actual, "browser_executed": False}, indent=2)+"\n")
print(json.dumps({"selected": len(actual), "version": value["version"], "genuine_manifest_roundtrip": True}))
