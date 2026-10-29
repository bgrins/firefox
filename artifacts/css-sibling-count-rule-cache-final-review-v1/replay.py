import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPSULE = ROOT / "artifacts/css-sibling-count-rule-cache-final-wpt-v1"
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
references = {}


def pin(path):
    references[str(path.relative_to(ROOT))] = sha(path)
    return path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha(pin(CAPSULE / "FILES.json")) == "6d5104c72c7affb86f4e4049e8c58103bd04e723bb2f82e45e94985c198aee47"
for name, digest in read(CAPSULE / "FILES.json").items():
    assert sha(pin(CAPSULE / name)) == digest
policy = read(CAPSULE / "POLICY.json")
for name, digest in policy["references"].items():
    assert sha(ROOT / name) == digest
settings = policy["wpt"]
expected = dict(settings, tests={name: "testharness" for name in settings["expected_subtests"]}, held_subtests={})
expected["regression_subtests"] = {test: [name for name in names if name not in settings["target_subtests"].get(test, [])] for test, names in settings["expected_subtests"].items()}
expected["cardinality_description"] = "Exact sealed target and control names; existing control failures retain full signatures."
checks = load("review_checks", ROOT / settings["checks_helper"])
assessor = load("review_assessor", CAPSULE / "assess.py")
original = None
records = {}
for role, directory in (("original", ROOT / policy["original_wpt"]), ("final", ROOT / policy["output"])):
    for name in ("raw.jsonl", "ASSESSMENT.json", "RESULT.json", "PRE.json", "POST.json", "APPLICATION-METADATA.json", "APPLICATION-METADATA-POST.json", "CLEANUP.json", "ASSESSMENT-POLICY.json", "BINARY-PINS.json"):
        pin(directory / name)
    result = read(directory / "RESULT.json")
    assert result["success"] and result["preservation_verified"] and result["execution_error"] is None
    events = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
    metadata = read(directory / "APPLICATION-METADATA.json")
    replay = assessor.assess(events, result["exit"], expected, checks, original=original, run_binding=metadata)
    assert json.loads(json.dumps(replay)) == read(directory / "ASSESSMENT.json")
    assert replay["complete"] and not replay["errors"] and not replay["fixture_setup_errors"] and not replay["infrastructure_faults"]
    assert len(replay["rows"]) == 36 and len(replay["ends"]) == 7 and len(replay["regression_signature"]) == 41
    assert all(end["status"] == "OK" for end in replay["ends"])
    assert read(directory / "PRE.json") == read(directory / "POST.json")
    assert metadata == read(directory / "APPLICATION-METADATA-POST.json")
    cleanup = read(directory / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    targets = [row for row in replay["rows"] if row["subtest"] in settings["target_subtests"].get(row["test"], [])]
    assert len(targets) == 2
    assert all(row["status"] == ("FAIL" if role == "original" else "PASS") for row in targets)
    records[role] = {"pass": sum(row["status"] == "PASS" for row in replay["rows"]), "fail": sum(row["status"] == "FAIL" for row in replay["rows"]), "full_raw_publication_replay": True}
    if role == "original":
        original = replay
    else:
        assert read(directory / "ASSESSMENT-POLICY.json") == expected
        assert replay["comparison_gate_passed"] and not replay["comparison_errors"] and not replay["unexpected"]
        assert replay["regression_signature"] == original["regression_signature"]
        driver = read(pin(directory / "FINAL-DRIVER.json"))
        assert driver == {"error": None, "native_acceptance": False, "owned_processes": {}, "preservation_error": None, "success": True}
        build = ROOT / policy["build_directory"]
        epoch = read(pin(build / "EPOCH.json"))
        assert sha(build / "EPOCH.json") == policy["epoch_sha256"]
        build_metadata = read(pin(build / "APPLICATION-METADATA.json"))
        assert build_metadata == policy["application_metadata"]
        assert metadata == dict(build_metadata, build_revision=build_metadata["revision"], harness_revision=settings["harness_revision"], source_role="candidate")
        for name, digest in read(directory / "BINARY-PINS.json").items():
            assert epoch["pins"][name] == digest
        for name, item in policy["tests"].items():
            captured = directory / "tests" / name.removeprefix("testing/web-platform/tests/")
            assert sha(pin(captured)) == item["sha256"] == epoch["pins"][name]
assert records["original"]["pass"] == 33 and records["original"]["fail"] == 3
assert records["final"]["pass"] == 35 and records["final"]["fail"] == 1
final_directory = ROOT / policy["output"]
assert sha(pin(final_directory / "FILES.json")) == "332adca2499ae5a79f2738be85dfd5d89488a9616ab26f28665692a3d0e29865"
inventory = read(final_directory / "FILES.json")
for name, digest in inventory.items():
    assert sha(final_directory / name) == digest
assert {str(path.relative_to(final_directory)) for path in final_directory.rglob("*") if path.is_file() and not path.is_symlink()} == set(inventory) | {"FILES.json"}
links = read(pin(final_directory / "SYMLINKS.json"))
assert links == {"tests/tools": str(ROOT / "testing/web-platform/tests/tools")}
assert {str(path.relative_to(final_directory)) for path in final_directory.rglob("*") if path.is_symlink()} == set(links)
for name, target in links.items():
    assert os.readlink(final_directory / name) == target
terminal = read(pin(final_directory / "ROOT-REPORTED-TERMINAL.json"))
assert terminal["exit_code"] == 0 and terminal["session_id"] == 58262 and terminal["launch_receipt"] == "7a9f50" and terminal["terminal_receipt"] == "af3f5e"
report = {"status": "CLEAR", "phases": records, "target_repairs": 2, "target_pass": 2, "regressions_unchanged": 34, "ends_unchanged": 7, "complete_signature_entries": 41, "actual_build_metadata_join": True, "saved_preservation_and_cleanup": True, "native_acceptance": False, "live_guards_or_browser_execution_by_reviewer": False}
(HERE / "REVIEW.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
(HERE / "REFERENCES.json").write_text(json.dumps(references, indent=2, sort_keys=True) + "\n")
print(json.dumps(report, sort_keys=True))
