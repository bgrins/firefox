from pathlib import Path
import stat


def validate(root, here, policy, helper):
    record = helper.read(here / "BASELINE.json")
    directory = root / record["directory"]
    helper.need(directory.is_dir() and not directory.is_symlink(), "regular baseline directory")
    capsule = root / record["capsule_directory"]
    helper.authenticate(capsule, record["capsule_sha256"])
    helper.need(helper.sha(directory / "FILES.json") == record["manifest_sha256"], "baseline inventory bytes")
    inventory = helper.read(directory / "FILES.json")
    helper.need(inventory["complete"] and not inventory["native_fix_accepted"], "baseline observation inventory")
    actual, links = set(), set()
    for path in directory.rglob("*"):
        name = str(path.relative_to(directory))
        if path.is_symlink():
            helper.need(inventory["excluded_derived_links"].get(name) == str(path.resolve()), "baseline derived link")
            links.add(name)
        elif path.is_file() and name != "FILES.json":
            helper.need(stat.S_ISREG(path.lstat().st_mode), "baseline regular file")
            actual.add(name)
    helper.need(actual == set(inventory["files"]), "exact frozen baseline files")
    helper.need(links == set(inventory["excluded_derived_links"]), "exact baseline derived links")
    for name, pin in inventory["files"].items():
        path = directory / name
        helper.need(helper.sha(path) == pin["sha256"] and path.stat().st_size == pin["bytes"], "baseline file: " + name)
    original_policy = helper.read(capsule / "POLICY.json")
    for key in ["tests", "target_subtests", "held_subtests", "regression_subtests", "installed_tests"]:
        helper.need(policy[key] == original_policy[key], "same experiment roster: " + key)
    helper.need(helper.read(here / "SUBSET-MANIFEST.json") == helper.read(capsule / "SUBSET-MANIFEST.json"), "same genuine WPT manifest")
    originals = helper.read(capsule / "SOURCE-PINS.json")
    sources = helper.read(here / "SOURCE-PINS.json")
    helper.need(set(sources) == set(originals), "same fixture and metadata inventory")
    for name, item in sources.items():
        helper.need({k: v for k, v in item.items() if k != "capture"} == {k: v for k, v in originals[name].items() if k != "capture"}, "same input body: " + name)
        if item["exists"]:
            helper.need((here / item["capture"]).resolve() == (capsule / originals[name]["capture"]).resolve(), "reuse exact immutable capture")
    assessment = helper.read(directory / "ASSESSMENT.json")
    helper.need(helper.sha(directory / "ASSESSMENT.json") == record["assessment_sha256"], "baseline assessment bytes")
    helper.need(assessment["capsule_directory"] == record["capsule_directory"] and assessment["capsule_manifest_sha256"] == record["capsule_sha256"], "baseline capsule identity")
    helper.need(assessment["complete"] and assessment["execution_preserved"] and not assessment["errors"] and not assessment["infrastructure_faults"] and not assessment["comparison_errors"], "baseline completed and preserved")
    result = helper.read(directory / "RESULT.json")
    outer = helper.read(directory / "OUTER.json")
    helper.need(result["observation_gate_passed"] and result["observation_only"] and result["execution_error"] is None and result["preservation_error"] is None and outer["wrapper_exit"] == 0 and outer["wpt_exit"] == result["exit"], "actual terminal baseline")
    cleanup = helper.read(directory / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "baseline cleanup")
    helper.need(helper.read(directory / "PRE.json") == helper.read(directory / "POST.json"), "baseline full saved preservation")
    metadata = helper.read(directory / "APPLICATION-METADATA.json")
    helper.need(metadata == helper.read(directory / "APPLICATION-METADATA-POST.json") == assessment["run_binding"], "baseline metadata unchanged")
    helper.need(assessment["epoch_sha256"] == original_policy["epoch_sha256"] == helper.sha(directory / "EPOCH.json"), "actual baseline epoch")
    helper.need(assessment["native_sources"] == original_policy["source_roles"]["candidate"], "baseline source role")
    parser = helper.load("baseline_assessor", capsule / "assess.py")
    checks = helper.load("baseline_checks", root / original_policy["helpers"]["checks"])
    events = [helper.json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
    replay = parser.assess(events, result["exit"], original_policy, checks, original=None, run_binding=metadata)
    for key in ["complete", "errors", "infrastructure_faults", "rows", "ends", "starts", "run_info", "held_signature", "regression_signature"]:
        helper.need(replay[key] == assessment[key], "actual raw baseline replay: " + key)
    helper.need(len(replay["rows"]) == 775 and len(replay["ends"]) == 36, "exact baseline cardinality")
    return {"directory": record["directory"], "manifest_sha256": record["manifest_sha256"],
            "assessment_sha256": record["assessment_sha256"], "raw_replayed": True,
            "assertions": 775, "pages": 36, "native_fix_acceptance": False,
            "same_fail_is_not_acceptance": True, "color_calibrations_require_full_snapshot_review": True}
