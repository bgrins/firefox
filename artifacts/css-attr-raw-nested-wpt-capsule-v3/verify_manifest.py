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
manifest = Manifest.from_json(str(here / "capture/testing/web-platform/tests"),
                              json.loads((here / "SUBSET-MANIFEST.json").read_text()))
selected = json.loads((here / "SELECTED.json").read_text())
observed = {}
references = {}
for kind, path, items in manifest:
    if kind in ("testharness", "reftest"):
        for item in items:
            observed[item.id] = kind
            if kind == "reftest":
                references[item.id] = item.references
assert observed == selected, (observed, selected)
assert sum(kind == "reftest" for kind in observed.values()) == 6
assert sum(kind == "testharness" for kind in observed.values()) == 10
print(json.dumps({"real_manifest_loader_roundtrip": True, "selected": observed,
                  "references": references}, indent=2))
