import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / "artifacts/css-contextual-duration-masked-snapshot-candidate-v2"
ORIGINAL = ROOT / "artifacts/css-contextual-duration-masked-nine-original-runtime-1/original-wpt"
CANDIDATE = ROOT / "artifacts/css-contextual-duration-masked-snapshot-candidate-runtime-2/candidate-wpt"
refs = {}
def read(path):
    body = path.read_bytes()
    refs[str(path.relative_to(ROOT))] = {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
    return body
def load(path):
    return json.loads(read(path))
def module(name, path):
    read(path)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
baseline_manifest = read(ORIGINAL.parent / "FILES.json")
assert hashlib.sha256(baseline_manifest).hexdigest() == "b38215f9a1967236a18ba4983fe37ae4afe9b4469a779cd1be26c4491d7a3595"
for name, pin in json.loads(baseline_manifest).items():
    body = read(ORIGINAL.parent / name)
    assert hashlib.sha256(body).hexdigest() == (pin["sha256"] if isinstance(pin, dict) else pin)
    if isinstance(pin, dict):
        assert len(body) == pin["bytes"]
assessor = module("snapshot_triage_assessor", OWNER / "assess.py")
read(ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py")
original_assessor = module("original_triage_assessor", ROOT / "artifacts/css-contextual-duration-masked-nine-original-v1/assess.py")
policy = load(CANDIDATE / "ASSESSMENT-POLICY.json")
checks = module("snapshot_triage_checks", ROOT / policy["checks_helper"])
original_policy = load(ORIGINAL / "ASSESSMENT-POLICY.json")
assert policy["resources"] == original_policy["resources"]
assert policy["manifest"] == original_policy["manifest"]
assert policy["target_subtests"] == {} and policy["expected_target_count"] == 0
assert policy["expected_control_count"] == 9 and policy["expected_regression_signature_count"] == 13
saved = {}
for role, phase in [("original", ORIGINAL), ("candidate", CANDIDATE)]:
    assert hashlib.sha256(read(phase / "metadata/MANIFEST.json")).hexdigest() == policy["manifest"]["sha256"]
    for name, pin in policy["resources"].items():
        assert hashlib.sha256(read(phase / "tests" / name)).hexdigest() == pin["sha256"]
        assert hashlib.sha256(read(ROOT / pin["path"])).hexdigest() == pin["sha256"]
    for name, pin in policy["metadata"].items():
        path = phase / "metadata" / name
        if pin["sha256"] is None:
            assert not path.exists()
        else:
            assert hashlib.sha256(read(path)).hexdigest() == pin["sha256"]
    events = [json.loads(line) for line in read(phase / "raw.jsonl").decode().splitlines()]
    result = load(phase / "RESULT.json")
    assert result["exit"] == (1 if role == "original" else 0)
    binding = load(phase / "APPLICATION-METADATA.json")
    assert binding == load(phase / "APPLICATION-METADATA-POST.json")
    current_policy = original_policy if role == "original" else policy
    actual = (original_assessor if role == "original" else assessor).assess(events, result["exit"], current_policy, checks,
        original=saved.get("original"), run_binding=binding)
    assert actual == load(phase / "ASSESSMENT.json")
    assert actual["complete"] and actual["errors"] == [] and actual["infrastructure_faults"] == []
    saved[role] = actual
assert saved["candidate"]["comparison_gate_passed"] is False
assert saved["candidate"]["comparison_errors"] == ["regression identities/status/expectations/intermittents changed"]
def keyed(items):
    pairs = [((item["kind"], item["test"], item["subtest"]), item) for item in items]
    assert len(pairs) == len(dict(pairs))
    return dict(pairs)
a = keyed(saved["original"]["regression_signature"])
b = keyed(saved["candidate"]["regression_signature"])
assert a.keys() == b.keys() and len(a) == 13
expected_targets = {
 "getAnimations processes a masked font change before retained effect timing is queried",
 "Changing a masked authored font updates contextual animation duration on the first read",
 "Changing an inherited host variable updates masked ::before duration on the first opacity read",
}
deltas = []
unchanged = []
for key in a:
    old, new = a[key], b[key]
    if old == new:
        unchanged.append(new)
        continue
    assert key[0] == "test_status" and key[2] in expected_targets
    assert old["status"] == "FAIL" and new["status"] == "PASS"
    assert old["expected"] == new["expected"] == "PASS"
    assert old["known_intermittent"] == new["known_intermittent"] == []
    changes = {name: {"original": old[name], "candidate": new[name]} for name in old if old[name] != new[name]}
    assert set(changes) == {"status", "expected_field_present", "message", "message_field_present"}
    deltas.append({"test": key[1], "subtest": key[2], "changes": changes})
assert {d["subtest"] for d in deltas} == expected_targets
assert len(unchanged) == 10
assert sum(row["kind"] == "test_status" and row["status"] == "PASS" for row in unchanged) == 6
assert sum(row["kind"] == "test_end" and row["status"] == "OK" for row in unchanged) == 4
print(json.dumps({"original": {"PASS": 6, "FAIL": 3, "OK": 4},
 "candidate": {"PASS": 9, "FAIL": 0, "OK": 4}, "candidate_browser_exit": 0,
 "strict_comparison_gate_preserved": False, "strict_comparison_errors": saved["candidate"]["comparison_errors"],
 "improvements": deltas, "unchanged_controls_and_endings": unchanged,
 "resources_and_metadata_match": True, "native_acceptance": False,
 "owner_terminal_or_restoration_reviewed": False, "references": refs}, indent=2, sort_keys=True))
