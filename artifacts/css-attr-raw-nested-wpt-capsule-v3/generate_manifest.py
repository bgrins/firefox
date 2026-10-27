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
source = here / "capture/testing/web-platform/tests"
selected = json.loads((here / "SELECTED.json").read_text())
references = json.loads((here / "REFERENCES-TO-COPY.json").read_text())
paths = [name.lstrip("/") for name in list(selected) + references]
manifest = Manifest(str(source), "/")
manifest.update([(name, None, True) for name in paths], parallel=False)
value = json.loads(json.dumps(manifest.to_json()))
for name, expected in json.loads((here / "EXISTING-MANIFEST-ENTRIES.json").read_text()).items():
    actual = value["items"][expected["type"]]
    for part in Path(name.lstrip("/")).parts:
        actual = actual[part]
    assert actual == expected["entry"], (name, actual, expected["entry"])
with (here / "SUBSET-MANIFEST.json").open("x") as stream:
    json.dump(value, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps({"selected":len(selected), "reference_documents":len(references),
                  "version":value["version"], "existing_entries_identical":True}))
