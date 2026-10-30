import copy
import importlib.util
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())


def expected_wpt(root, policy):
    old = read(root / policy["baseline_capsule"]["directory"] / "POLICY.json")["wpt"]
    roster = read(root / policy["baseline_binding"]["directory"] / "DISCOVERED-ROSTER.json")
    expected = copy.deepcopy(old)
    assert roster["observed_subtest_count"] == 472
    assert set(roster["expected_subtests"]) == set(old["expected_subtests"])
    for page, names in old["known_subtests"].items():
        assert roster["expected_subtests"][page] == names
    expected.update(expected_subtests=roster["expected_subtests"], expected_subtest_count=472,
                    expected_target_count=14, expected_control_count=458,
                    expected_page_count=12, expected_regression_signature_count=470,
                    roster_mode="sealed-comparison",
                    candidate_required_pass_pages=old["fixture_target_pages"])
    expected["phase_revisions"]["candidate"] = policy["head"]
    assert sum(len(expected["expected_subtests"][page]) for page in expected["candidate_required_pass_pages"]) == 32
    return expected


def phase_policy(settings):
    result = dict(settings, tests={page: "testharness" for page in settings["expected_subtests"]}, held_subtests={})
    result["regression_subtests"] = {page: [name for name in names if name not in settings["target_subtests"].get(page, [])]
                                    for page, names in settings["expected_subtests"].items()}
    result["cardinality_description"] = "Exact sealed target and control names; existing control failures retain full signatures."
    return result


def replay_original(root, policy, assessor, checks):
    directory = root / policy["baseline_binding"]["directory"]
    phase = directory / "original-wpt"
    capsule = root / policy["baseline_capsule"]["directory"]
    spec = importlib.util.spec_from_file_location("original_discovery_assessor", capsule / "assess.py")
    discovery = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(discovery)
    events = [json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines()]
    original_policy = read(capsule / "POLICY.json")
    saved = read(phase / "ASSESSMENT-POLICY.json")
    expected_saved = phase_policy(original_policy["wpt"])
    expected_saved["cardinality_description"] = "Five exact authored rosters and seven original-browser-discovered rosters; aggregate cardinality not predeclared."
    assert saved == expected_saved
    binding = read(phase / "APPLICATION-METADATA.json")
    result = read(phase / "RESULT.json")
    observed = discovery.assess(events, result["exit"], saved, checks, run_binding=binding)
    assert json.loads(json.dumps(observed)) == read(phase / "ASSESSMENT.json")
    assert observed["complete"] and result["success"] and result["preservation_verified"]
    assert read(directory / "DISCOVERED-ROSTER.json")["expected_subtests"] == observed["discovered_subtests"]
    assert read(phase / "PRE.json") == read(phase / "POST.json")
    assert binding == read(phase / "APPLICATION-METADATA-POST.json") == original_policy["prepared_application_metadata"]
    assert policy["wpt"] == expected_wpt(root, policy)
    strict = assessor.assess(events, result["exit"], phase_policy(policy["wpt"]), checks, run_binding=binding)
    assert strict["complete"] and strict["errors"] == []
    for key in ("rows", "starts", "ends", "regression_signature", "held_signature", "run_info", "run_binding",
                "fixture_setup_errors", "unexpected", "infrastructure_faults", "per_test", "observed_subtest_count"):
        assert strict[key] == observed[key], key
    return strict
