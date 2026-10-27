import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = ROOT / "artifacts/css-registered-number-wpt-fixture-v2"
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
enumerated = read(FIXTURE / "ENUMERATION.json")
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
    assert (FIXTURE / ("candidate/testing/web-platform/tests" + name)).read_bytes() == (HERE / ("capture/testing/web-platform/tests" + name)).read_bytes()
assert "observation-only" not in json.dumps(manifest)
for name in read(HERE / "REFERENCES-TO-COPY.json"):
    assert (HERE / ("capture/testing/web-platform/tests" + name)).is_file()
policy = read(HERE / "POLICY.json")
assert policy["tests"] == selected
assert policy["target_subtests"] == targets and policy["regression_subtests"] == regressions
roles = read(HERE / "SOURCE-ROLE-CAPTURES.json")
for phase, source_role in (("original", "base"), ("candidate", "candidate")):
    assert policy["source_roles"][phase] == {name: item["sha256"] for name, item in roles[source_role].items()}
    for name, item in roles[source_role].items():
        assert sha(ROOT / item["capture"]) == item["sha256"], name
assert len(policy["source_roles"]["original"]) == len(policy["source_roles"]["candidate"]) == 3
for name, pin in policy["live_oracle_sources"].items():
    source = ROOT / name
    assert (sha(source) if source.exists() else None) == pin, name
for name, item in read(FIXTURE / "FILES.json").items():
    assert sha(FIXTURE / name) == item["sha256"], name
    assert read(HERE / "REFERENCES.json")[str((FIXTURE / name).relative_to(ROOT))] == item["sha256"]
for name in ("SOURCE-PINS.json", "SELECTED.json", "TARGET-SUBTESTS.json", "REGRESSION-SUBTESTS.json", "SUBSET-MANIFEST.json"):
    assert (HERE / name).read_bytes() == (FIXTURE / name).read_bytes(), name
assert (HERE / "test_application_metadata.py").read_bytes() == (ROOT / "artifacts/css-attr-raw-nested-wpt-capsule-v3/test_application_metadata.py").read_bytes()
for file in HERE.glob("*.py"):
    ast.parse(file.read_text(), filename=str(file))
print(json.dumps({"capture_and_origins_authenticated": True,
                  "present_roles": sum(item["exists"] for item in pins.values()),
                  "absent_roles": sum(not item["exists"] for item in pins.values()),
                  "targets": 58, "regressions": 446, "reftests": 6,
                  "prior_402_actual_names_exact": True,
                  "prior_21_regression_manifest_entries_identical": True,
                  "all_fixture_payloads_bound": True,
                  "reviewed_clean_head_three_file_roles_bound": True,
                  "observation_excluded": True, "browser_executed": False}, indent=2))
