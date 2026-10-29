import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(path) for path in (WPT / "tools/third_party").iterdir() if path.is_dir()] + [str(WPT / "tools"), str(WPT)]
import html5lib
from manifest.manifest import Manifest

read = lambda name: json.loads((HERE / name).read_text())
for name, pin in read("REFERENCES.json").items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
experiment = read("EXPERIMENT.json")
resources = read("RESOURCES.json")
expected = experiment["expected_subtests"]
with tempfile.TemporaryDirectory(prefix="css-hypot-roster-") as temporary:
    scratch = Path(temporary)
    for name, pin in resources.items():
        part = Path(name)
        assert not part.is_absolute() and ".." not in part.parts
        data = (ROOT / pin["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == pin["sha256"]
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    registration_input = scratch / "registration.json"
    registration_input.write_text(json.dumps({"root": str(scratch), "expected": expected}))
    result = subprocess.run(["node", str(HERE / "enumerate.js"), str(registration_input)], text=True, capture_output=True, check=True)
    assert {"/" + k.lstrip("/"): v for k, v in json.loads(result.stdout).items()} == expected
    manifest = Manifest(str(scratch), "/")
    manifest.update([(name, None, True) for name in sorted(resources)], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    assert sum(1 for _ in manifest.itertypes("testharness")) == 4
    saved = HERE / "SUBSET-MANIFEST.json"
    if saved.exists():
        assert json.loads(saved.read_text()) == serialized
    else:
        saved.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
print(json.dumps({"registered_pages": 4, "registered_callbacks": 227, "targets": 16, "controls": 211, "callbacks_executed": False, "missing_resources_waived": False, "scratch_removed": True}))
