from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda name: json.loads((ROOT / name).read_text())
sha = lambda name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
packages = [
    "artifacts/css-contextual-easing-reversible-browser-v4",
    "artifacts/css-contextual-easing-regression-plan-v1",
    "artifacts/css-contextual-easing-browser-completion-v1",
    "artifacts/css-contextual-easing-after-cache-plan-v1",
    "artifacts/css-contextual-easing-rule-expression-plan-v1",
    "artifacts/css-contextual-easing-after-moves-browser-v3",
]
refs = {}
for package in packages:
    refs[package + "/FILES.json"] = sha(package + "/FILES.json")
    manifest = read(package + "/FILES.json")
    for name, pin in manifest.get("files", manifest).items():
        assert sha(package + "/" + name) == (pin["sha256"] if isinstance(pin, dict) else pin)
old = read(packages[0] + "/POLICY.json")["wpt"]
current = read(packages[-1] + "/POLICY.json")["wpt"]
plan = read(packages[3] + "/EXPERIMENT.json")
assert current["expected_subtests"] == plan["target_subtests"] == current["target_subtests"]
new_page = "/css/css-animations/contextual-easing-rule-expression-ownership.html"
new_names = read(packages[4] + "/CHECK.json")["registered_names"]
new_resource = {"path": packages[4] + "/contextual-easing-rule-expression-ownership.html"}
new_resource["sha256"] = sha(new_resource["path"])
inputs = {
    "historical293": old["expected_subtests"],
    "current19": current["expected_subtests"],
    "future3": {new_page: new_names},
}
identities = {key: {(page, name) for page, names in pages.items() for name in names}
              for key, pages in inputs.items()}
for key, pages in inputs.items():
    assert sum(map(len, pages.values())) == len(identities[key])
for index, key in enumerate(inputs):
    for other in list(inputs)[index + 1:]:
        assert not identities[key] & identities[other]
        assert not set(inputs[key]) & set(inputs[other])
expected = {page: names for pages in inputs.values() for page, names in pages.items()}
targets = {**old["target_subtests"], **current["target_subtests"], new_page: new_names}
controls = {page: [name for name in names if name not in targets.get(page, [])]
            for page, names in expected.items()}
controls = {page: names for page, names in controls.items() if names}
assert sum(map(len, controls.values())) == 274
resources, metadata = {}, {}
duplicates = {"resources": [], "metadata": []}
new = {
    "resources": {new_page.lstrip("/"): new_resource},
    "metadata": {new_page.lstrip("/") + ".ini": {
        "path": "testing/web-platform/meta" + new_page + ".ini", "sha256": None}},
}
for source in [old, current, new]:
    for kind, destination in [("resources", resources), ("metadata", metadata)]:
        for name, pin in source[kind].items():
            if name in destination:
                assert pin == destination[name], (kind, name)
                duplicates[kind].append(name)
            destination[name] = pin
            if pin["sha256"] is not None:
                assert sha(pin["path"]) == pin["sha256"]
                refs[pin["path"]] = pin["sha256"]
pins = read(packages[3] + "/SOURCE-PINS.json")
for name, pin in current["resources"].items():
    origin = "testing/web-platform/tests/" + name
    if origin in pins:
        assert pins[origin]["sha256"] == pin["sha256"]
roles = read(packages[3] + "/SOURCE-ROLES.json")
assert roles == read(packages[0] + "/SOURCE-ROLES.json")
for entry in roles.values():
    for role in ["base", "candidate"]:
        assert sha(entry[role + "_capture"]) == entry[role + "_sha256"]
        refs[entry[role + "_capture"]] = entry[role + "_sha256"]
for name in [
    packages[0] + "/POLICY.json", packages[3] + "/EXPERIMENT.json",
    packages[3] + "/SOURCE-PINS.json", packages[4] + "/CHECK.json",
    "artifacts/css-contextual-easing-activation-prototype-v2/native.patch",
    packages[2] + "/PAYLOADS.json", packages[2] + "/BASELINE-SNAPSHOT.json",
    packages[1] + "/SOURCE-PINS.json",
    "artifacts/css-contextual-easing-effect-ownership-model-v2/README.md",
    "artifacts/css-contextual-easing-effect-ownership-model-v2/MAPPING.md",
    "artifacts/css-contextual-easing-dependency-cache-model-v1/README.md",
    packages[0] + "/assess.py",
    "artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py",
    packages[-1] + "/POLICY.json",
    packages[4] + "/SUBSET-MANIFEST.json",
    old["manifest"]["path"], current["manifest"]["path"],
]:
    refs[name] = sha(name)
for name, pin in read(packages[2] + "/PAYLOADS.json").items():
    assert sha(name) == pin
    refs[name] = pin
snapshot = read(packages[2] + "/BASELINE-SNAPSHOT.json")
assert sha(snapshot["path"]) == snapshot["sha256"]
refs[snapshot["path"]] = snapshot["sha256"]
for name in ["raw.jsonl", "ASSESSMENT.json", "ASSESSMENT-POLICY.json", "RESULT.json", "APPLICATION-METADATA.json"]:
    path = "artifacts/css-contextual-easing-reversible-browser-runtime-2/original-wpt/" + name
    refs[path] = sha(path)
missing = "testing/web-platform/tests/css/css-easing/support/util.js"
missing_pin = read(packages[1] + "/SOURCE-PINS.json")[missing]
assert not missing_pin["exists"]
assert "css/css-easing/support/util.js" not in resources
experiment = {
    "execution_enabled": False,
    "conditional_on": "Completed current exact19 comparison and verified restoration, then separately reviewed fresh owner",
    "expected_subtest_count": sum(map(len, expected.values())),
    "expected_page_count": len(expected),
    "expected_subtests": expected,
    "target_subtests": targets,
    "regression_subtests": controls,
    "held_subtests": {},
    "tests": {page: "testharness" for page in expected},
    "candidate_requirements": {
        "all_target_pass": True, "target_count": sum(map(len, targets.values())),
        "all274_control_full_signatures_preserved": True,
        "original_passing_callback_full_signatures_preserved": True,
        "all22_ending_full_signatures_preserved": True,
        "original_failure_required": False, "original_complete_required": True,
        "native_acceptance": False,
    },
    "nonlanding_pages": read(packages[1] + "/POLICY.json")["nonlanding_pages"],
}
assert experiment["expected_subtest_count"] == 315 and len(expected) == 22
assert experiment["candidate_requirements"]["target_count"] == 41
outputs = {
    "EXPERIMENT.json": experiment, "RESOURCES.json": resources, "METADATA.json": metadata,
    "SOURCE-ROLES.json": roles, "REFERENCES.json": refs,
    "MISSING-RESOURCE.json": {
        "origin": missing, "historical_pin": missing_pin, "included_in_resources": False,
        "inert_registration_exception_only": True, "browser_diagnostics_must_be_retained": True,
        "absence_must_be_verified_by_future_owner": True,
    },
    "INPUT-DELTA.json": {
        "groups": {key: {"pages": len(pages), "callbacks": sum(map(len, pages.values()))}
                   for key, pages in inputs.items()},
        "identity_overlap": 0, "page_overlap": 0, "total_pages": 22, "total_callbacks": 315,
        "targets": 41, "strict_historical_controls": 274,
        "combined_control_and_end_signatures": 296, "historical_control_and_end_signatures": 292,
        "resource_entries": len(resources), "metadata_entries": len(metadata),
        "byte_identical_duplicate_inputs": duplicates, "source_overlay_paths": 8,
        "source_overlay_changed": False, "source_or_fixture_bytes_rewritten": False,
        "live_source_validation": False,
    },
}
for name, value in outputs.items():
    path = HERE / name
    if path.exists():
        assert json.loads(path.read_text()) == value, name
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
print(json.dumps(outputs["INPUT-DELTA.json"]))
