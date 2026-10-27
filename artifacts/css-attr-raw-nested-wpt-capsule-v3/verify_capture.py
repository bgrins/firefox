import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / "artifacts/css-attr-raw-nested-wpt-capsule-v2"
PROPOSAL = ROOT / "artifacts/css-attr-raw-nested-repair-v2"
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
policy = read(HERE / "POLICY.json")
pins = read(HERE / "SOURCE-PINS.json")
old_pins = read(PRIOR / "SOURCE-PINS.json")
for name, item in pins.items():
    path = ROOT / item["origin"]
    assert path.exists() == item["exists"], name
    if item["exists"]:
        assert not path.is_symlink() and sha(path) == item["sha256"], name
        captured = HERE / item["capture"]
        assert sha(captured) == item["sha256"] and captured.stat().st_size == item["bytes"], name
    if name in old_pins and name not in {"testing/web-platform/tests" + t for t in policy["target_subtests"]}:
        assert item == old_pins[name], name
for name, pin in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / name) == pin, name
for name, pin in policy["live_oracle_sources"].items():
    assert (sha(ROOT / name) if (ROOT / name).exists() else None) == pin, name
assert len(pins) == 78
assert sum(item["exists"] for item in pins.values()) == 28
manifest = read(HERE / "SUBSET-MANIFEST.json")
old_manifest = read(PRIOR / "SUBSET-MANIFEST.json")
def entry(value, name, kind):
    current = value["items"][kind]
    for part in Path(name.lstrip("/")).parts:
        current = current[part]
    return current
unchanged = []
for name, kind in read(PRIOR / "SELECTED.json").items():
    current, previous = entry(manifest, name, kind), entry(old_manifest, name, kind)
    if name in policy["target_subtests"]:
        assert current[0] != previous[0] and current[1:] == previous[1:], name
    else:
        assert current == previous, name
        unchanged.append(name)
for name in policy["target_subtests"]:
    captured = HERE / ("capture/testing/web-platform/tests" + name)
    assert captured.read_bytes() == (PROPOSAL / ("candidate/testing/web-platform/tests" + name)).read_bytes()
assert sum(map(len, policy["target_subtests"].values())) == 73
assert sum(map(len, policy["regression_subtests"].values())) == 329
assert set(policy["target_subtests"]).isdisjoint(policy["regression_subtests"])
assert set(policy["target_subtests"]) | set(policy["regression_subtests"]) == {t for t,k in policy["tests"].items() if k == "testharness"}
assert (HERE / "run.py").read_bytes() == (PRIOR / "run.py").read_bytes()
assert policy["source_roles"] == read(PRIOR / "POLICY.json")["source_roles"]
for item in read(HERE / "NATIVE-EQUIVALENCE.json")["snapshots"].values():
    assert sha(ROOT / item["v1"]) == sha(ROOT / item["v2"]) == item["sha256"]
for name in ("run.py", "assess.py", "test_assess.py", "test_application_metadata.py", "generate_manifest.py", "verify_manifest.py", "verify_capture.py"):
    ast.parse((HERE / name).read_text(), filename=name)
print(json.dumps({"capture_and_origins_authenticated": True,
                  "source_roles": len(pins), "present_roles": 28, "absent_roles": 50,
                  "all_helpers_authenticated": True, "unchanged_manifest_entries": unchanged,
                  "all14_regression_manifest_entries_unchanged": True,
                  "two_target_manifest_entries_only_content_digest_changed": True,
                  "target_pages_exact_proposal_bytes": True,
                  "target_subtests": 73, "regression_subtests": 329,
                  "python_syntax": True, "browser_executed": False}, indent=2))
