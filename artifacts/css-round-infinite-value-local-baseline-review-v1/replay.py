import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda path: json.loads(path.read_bytes())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(path, pin, runtime=False):
    assert digest(path / "FILES.json") == pin
    manifest = read(path / "FILES.json")
    for name, expected in manifest.items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert not (path / name).is_symlink() and digest(path / name) == expected, name
    if runtime:
        regular = {str(p.relative_to(path)) for p in path.rglob("*") if p.is_file() and not p.is_symlink()}
        links = {str(p.relative_to(path)): str(p.readlink()) for p in path.rglob("*") if p.is_symlink()}
        assert regular == set(manifest) | {"FILES.json"}
        assert links == {"tests/tools": str(ROOT / "testing/web-platform/tests/tools")}
    return len(manifest)


cases = [
    ("numeric", "css-round-infinite-value-validation-plan-v1", "74d94041cd22e3d9227f46ac74755b89f1797a4ce9b858482dda229ace7cb9bb",
     "css-round-infinite-value-baseline-runtime-1", "3ac78fd21ebc41155e3f0133383287f34e5e79a91c6863454f32d3383879fa23"),
    ("admission", "css-round-infinite-value-admission-plan-v1", "7a52068a11e26671e0774e4c27661598a0ae8208a75d7ad6ed5f64e205504aed",
     "css-round-infinite-value-admission-runtime-1", "7de45599430767e849b4868c6e942220fc322f6451d7807c8d88d24c5ae1e7ad"),
]
report = {}
for label, capsule_name, capsule_pin, runtime_name, runtime_pin in cases:
    capsule = ROOT / "artifacts" / capsule_name
    runtime = ROOT / "artifacts" / runtime_name
    authenticate(capsule, capsule_pin)
    count = authenticate(runtime, runtime_pin, True)
    result, policy = read(runtime / "RESULT.json"), read(capsule / "BASELINE-POLICY.json")
    before, after = read(runtime / "PRE.json"), read(runtime / "POST.json")
    assert before == after
    assert before["controls"]["CURRENT-EPOCH.json"] == policy["epoch_sha256"]
    assert before["indexes"]["root"]["head"] == policy["head"]
    for name, pin in policy["expected_pins"].items():
        assert before["files"][name]["sha256"] == pin
    cleanup = read(runtime / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    terminal = read(runtime / "ROOT-TERMINAL.json")
    assert terminal["exit_code"] == 0 and terminal["result_sha256"] == digest(runtime / "RESULT.json")
    assert not terminal["native_candidate_installed"] and not terminal["native_fix_accepted"]
    assert result["success"] and result["preservation_verified"] and not result["native_fix_acceptance"]
    assert result["execution_error"] is None and result["assessment_error"] is None
    events = [json.loads(line) for line in (runtime / "raw.jsonl").read_text().splitlines()]
    rows = [event for event in events if event.get("action") == "test_status"]
    observation = read(runtime / "observation.json")
    if label == "numeric":
        source = (capsule / "run_baseline.py").read_text()
        start = source.index("assessment_error = None\nsummary = {}\ntry:\n")
        end = source.index("\nsuccess = error is None", start)
        scope = {"json": json, "read": read, "output": runtime, "code": result["harness_exit"], "policy": policy}
        exec(compile(source[start:end], "saved numeric assessment only", "exec"), scope)
        assert scope["assessment_error"] is None and scope["summary"] == result["summary"]
        mismatches = Counter()
        for row in rows:
            snapshots = [s for s in observation["snapshots"] if f'{s["kind"]} {s["mode"]} {s["sign"]}' == row["subtest"]]
            assert len(snapshots) == 3
            passed = all(float(s["actual"]) == s["expected"] for s in snapshots)
            assert row["status"] == ("PASS" if passed else "FAIL")
        for snapshot in observation["snapshots"]:
            if float(snapshot["actual"]) != snapshot["expected"]:
                mismatches[snapshot["kind"]] += 1
                assert snapshot["font"] == 0
        assert mismatches == {"relative-leaf-step": 8}
        report[label] = {"summary": scope["summary"], "mismatched_snapshots": dict(mismatches)}
    else:
        spec = importlib.util.spec_from_file_location("saved_admission_assessment", capsule / "assess.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        summary = module.assess(runtime, result["harness_exit"], policy)
        assert summary == result["summary"] and summary["pass"] == 8 and summary["fail"] == 0
        rejected = {s["id"] for s in observation["snapshots"] if not s["directSupported"]}
        assert rejected == {"steps", "bezier", "linear-output", "linear-second-position"}
        for snapshot in observation["snapshots"]:
            assert bool(snapshot["directSpecified"]) == snapshot["directSupported"]
        report[label] = {"summary": summary, "direct_context_rejected": sorted(rejected)}
    report[label].update({"runtime_manifest": runtime_pin, "runtime_payloads": count,
                          "raw_status_counts": dict(Counter(row["status"] for row in rows)),
                          "pre_post_equal": True, "owned_cleanup_complete": True,
                          "browser": observation["userAgent"], "root_terminal": terminal})
assert report["numeric"]["raw_status_counts"] == {"PASS": 16, "FAIL": 8}
print(json.dumps(report, indent=2, sort_keys=True))
