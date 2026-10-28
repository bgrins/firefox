import json
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
root = here.parents[1]
tools = root / "testing/web-platform/tests/tools"
sys.path.insert(0, str(tools))
for name in ("atomicwrites", "html5lib", "webencodings", "six"):
    sys.path.insert(0, str(tools / "third_party" / name))
from manifest.manifest import Manifest
source = here / "capture/testing/web-platform/tests"
selected = json.loads((here / "POLICY.json").read_text())["tests"]
manifest = Manifest(str(source), "/")
manifest.update([(test.lstrip("/"), None, True) for test in selected], parallel=False)
value = json.loads(json.dumps(manifest.to_json()))
loaded = Manifest.from_json(str(source), value)
actual = {item.id: kind for kind, _, items in loaded for item in items}
assert actual == selected, (actual, selected)
(here / "SUBSET-MANIFEST.json").write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
print(json.dumps({"genuine_manifest": True, "tests": actual}, indent=2))
