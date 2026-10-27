import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
pins = read(HERE / "SOURCE-PINS.json")
for name, item in pins.items():
    source = ROOT / item["origin"]
    assert source.exists() == item["exists"], name
    if item["exists"]:
        assert not source.is_symlink() and sha(source) == item["sha256"], name
        captured = HERE / item["capture"]
        assert sha(captured) == item["sha256"] and captured.stat().st_size == item["bytes"], name
for name, expected in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / name) == expected, name
selected = read(HERE / "SELECTED.json")
targets = read(HERE / "TARGET-SUBTESTS.json")
regressions = read(HERE / "REGRESSION-SUBTESTS.json")
assert len(selected) == 22
assert sum(kind == "reftest" for kind in selected.values()) == 6
assert sum(map(len, targets.values())) == 58
assert sum(map(len, regressions.values())) == 446
assert set(targets).isdisjoint(regressions)
assert set(targets) | set(regressions) == {name for name, kind in selected.items() if kind == "testharness"}
for names in list(targets.values()) + list(regressions.values()):
    assert len(names) == len(set(names))
enumerated = read(HERE / "ENUMERATION.json")
assert list(targets.values()) == [enumerated["target_names"]]
for name, names in enumerated["added_regression_names"].items():
    assert regressions[name] == names
prior = read(ROOT / "artifacts/css-attr-raw-nested-wpt-runtime-candidate-2/ASSESSMENT.json")
prior_names = {}
for row in prior["rows"]:
    assert row["status"] == "PASS"
    prior_names.setdefault(row["test"], []).append(row["subtest"])
assert sum(map(len, prior_names.values())) == 402
for name, names in prior_names.items():
    assert regressions[name] == names
manifest = read(HERE / "SUBSET-MANIFEST.json")
def entry(name, kind):
    result = manifest["items"][kind]
    for part in Path(name.lstrip("/")).parts:
        result = result[part]
    return result
for name, expected in read(HERE / "EXISTING-MANIFEST-ENTRIES.json").items():
    assert entry(name, expected["type"]) == expected["entry"], name
for name, kind in selected.items():
    assert entry(name, kind)[1][0] in (None, name)
for name in targets:
    assert (HERE / ("candidate/testing/web-platform/tests" + name)).read_bytes() == (HERE / ("capture/testing/web-platform/tests" + name)).read_bytes()
assert "observation-only" not in json.dumps(manifest)
for name in read(HERE / "REFERENCES-TO-COPY.json"):
    assert (HERE / ("capture/testing/web-platform/tests" + name)).is_file()
previous = ROOT / "artifacts/css-registered-number-wpt-fixture-v1"
assert enumerated["target_names"][:52] == read(previous / "ENUMERATION.json")["target_names"]
for name in targets:
    current_html = (HERE / ("candidate/testing/web-platform/tests" + name)).read_text()
    previous_html = (previous / ("candidate/testing/web-platform/tests" + name)).read_text()
    assert current_html.startswith(previous_html[:-10])
assert (HERE / "REGRESSION-SUBTESTS.json").read_bytes() == (previous / "REGRESSION-SUBTESTS.json").read_bytes()
for file in HERE.glob("*.py"):
    ast.parse(file.read_text(), filename=str(file))
print(json.dumps({"capture_and_origins_authenticated": True,
                  "present_roles": sum(item["exists"] for item in pins.values()),
                  "absent_roles": sum(not item["exists"] for item in pins.values()),
                  "targets": 58, "regressions": 446, "reftests": 6,
                  "prior_402_actual_names_exact": True,
                  "prior_21_regression_manifest_entries_identical": True,
                  "observation_excluded": True, "browser_executed": False}, indent=2))
