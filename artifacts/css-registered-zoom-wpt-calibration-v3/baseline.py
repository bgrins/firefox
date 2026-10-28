import json


def validate(root, here, policy, helper, parser, checks):
    base = root / policy["capture_package"]
    helper.authenticate(base, policy["capture_manifest_sha256"])
    for name in ["SOURCE-PINS.json", "SELECTED.json", "TARGET-SUBTESTS.json"]:
        helper.need((here / name).read_bytes() == (base / name).read_bytes(), "unchanged fixture binding: " + name)
    before_policy = helper.read(base / "POLICY.json")
    for key in ["target_subtests", "tests", "live_oracle_sources", "regression_subtests", "held_subtests", "frozen_head"]:
        helper.need(policy[key] == before_policy[key], "unchanged experiment: " + key)
    directory = root / policy["baseline_directory"]
    for name, expected in helper.read(here / "BASELINE-PINS.json").items():
        path = directory / name
        helper.need(path.is_file() and not path.is_symlink() and helper.sha(path) == expected, "exact saved baseline: " + name)
    assessment = helper.read(directory / "ASSESSMENT.json")
    result = helper.read(directory / "RESULT.json")
    epoch = helper.read(directory / "EPOCH.json")
    metadata = helper.read(directory / "APPLICATION-METADATA.json")
    helper.need(assessment["capsule_manifest_sha256"] == policy["capture_manifest_sha256"] and
                assessment["epoch_sha256"] == before_policy["epoch_sha256"] and
                assessment["native_sources"] == before_policy["native_sources"] and
                assessment["source_role"] == "admission-only-v3-build2" and
                assessment["phase"] == "admission-only-1", "baseline role and provenance")
    helper.need(assessment["complete"] and assessment["execution_preserved"] and result["observation_gate_passed"] and
                result["execution_error"] is None and result["preservation_error"] is None, "successful preserved baseline capture")
    helper.need(epoch["semantic_index"]["head"] == policy["frozen_head"] and
                helper.read(directory / "NORMAL-BINARIES.json") == before_policy["candidate_binaries"], "baseline HEAD/binaries")
    helper.need(metadata == helper.read(directory / "APPLICATION-METADATA-POST.json") == assessment["run_binding"], "baseline metadata")
    helper.need(helper.read(directory / "PRE.json") == helper.read(directory / "POST.json"), "baseline preservation")
    cleanup = helper.read(directory / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "baseline cleanup")
    events = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
    replay = parser.assess(events, result["exit"], before_policy, checks, original=None, run_binding=metadata)
    replay.update(subtest_cardinality_policy="Exact 56 calibration identities across four pages; PASS and FAIL are complete observations",
                  oracle_caveat="Unexecuted draft calibration on admission-only candidate; failures are observations, not accepted fixes")
    helper.need(all(assessment.get(key) == value for key, value in replay.items()), "baseline raw replay")
    statuses = [row["status"] for row in assessment["rows"]]
    helper.need(statuses.count("FAIL") == 50 and statuses.count("PASS") == 6 and len(statuses) == 56, "baseline 50 FAIL / 6 PASS")
    return assessment
