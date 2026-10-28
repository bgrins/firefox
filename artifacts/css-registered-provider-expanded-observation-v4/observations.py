from collections import Counter
import json
import stat


def validate(root, here, policy, helper):
    histories = []
    for record in helper.read(here / "HISTORICAL.json"):
        directory = root / record["directory"]
        helper.need(directory.is_dir() and not directory.is_symlink(), "historical regular directory")
        helper.need(helper.sha(directory / "FILES.json") == record["manifest_sha256"], "historical inventory")
        inventory = helper.read(directory / "FILES.json")
        helper.need(inventory["complete"] and not inventory["native_fix_accepted"], "historical observation only")
        files, links = set(), set()
        for path in directory.rglob("*"):
            name = str(path.relative_to(directory))
            if path.is_symlink():
                helper.need(inventory["excluded_derived_links"].get(name) == str(path.resolve()), "historical derived link")
                links.add(name)
            elif path.is_file() and name != "FILES.json":
                helper.need(stat.S_ISREG(path.lstat().st_mode), "historical regular payload")
                files.add(name)
        helper.need(files == set(inventory["files"]) and links == set(inventory["excluded_derived_links"]), "historical exact inventory")
        for name, pin in inventory["files"].items():
            path = directory / name
            helper.need(helper.sha(path) == pin["sha256"] and path.stat().st_size == pin["bytes"], "historical payload: " + name)
        capsule = root / record["capsule_directory"]
        helper.authenticate(capsule, record["capsule_manifest_sha256"])
        previous_policy = helper.read(capsule / "POLICY.json")
        for key in ["tests", "target_subtests", "held_subtests", "regression_subtests", "installed_tests"]:
            helper.need(policy[key] == previous_policy[key], "historical unchanged experiment: " + key)
        helper.need(helper.read(here / "SUBSET-MANIFEST.json") == helper.read(capsule / "SUBSET-MANIFEST.json"), "historical genuine manifest")
        old_pins, new_pins = helper.read(capsule / "SOURCE-PINS.json"), helper.read(here / "SOURCE-PINS.json")
        helper.need(set(old_pins) == set(new_pins), "historical input inventory")
        for name, item in new_pins.items():
            old = old_pins[name]
            helper.need({k:v for k,v in item.items() if k != "capture"} == {k:v for k,v in old.items() if k != "capture"}, "historical fixture/metadata identity")
            if item["exists"]:
                helper.need((here / item["capture"]).resolve() == (capsule / old["capture"]).resolve(), "same frozen capture")
        saved = helper.read(directory / "ASSESSMENT.json")
        helper.need(helper.sha(directory / "ASSESSMENT.json") == record["assessment_sha256"], "historical assessment")
        helper.need(saved["capsule_directory"] == record["capsule_directory"] and saved["capsule_manifest_sha256"] == record["capsule_manifest_sha256"], "historical capsule provenance")
        helper.need(saved["complete"] and saved["execution_preserved"] and not saved["errors"] and not saved["infrastructure_faults"], "historical completion")
        result = helper.read(directory / "RESULT.json")
        helper.need(result["observation_gate_passed"] and result["execution_error"] is None and result["preservation_error"] is None, "historical successful capture")
        outer = helper.read(directory / "OUTER.json")
        if "wrapper_exit" in outer:
            helper.need(outer["wrapper_exit"] == 0 and outer["wpt_exit"] == result["exit"], "historical wrapper exit")
        else:
            helper.need(outer["exit_code"] == 0, "historical outer exit")
        cleanup = helper.read(directory / "CLEANUP.json")
        helper.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "historical cleanup")
        helper.need(helper.read(directory / "PRE.json") == helper.read(directory / "POST.json"), "historical preservation")
        metadata = helper.read(directory / "APPLICATION-METADATA.json")
        helper.need(metadata == helper.read(directory / "APPLICATION-METADATA-POST.json") == saved["run_binding"], "historical metadata")
        helper.need(metadata["revision"] == policy["frozen_head"] == previous_policy["frozen_head"], "historical harness HEAD")
        helper.need(saved["epoch_sha256"] == previous_policy["epoch_sha256"] == helper.sha(directory / "EPOCH.json"), "historical epoch identity")
        helper.need(saved["native_sources"] == previous_policy["source_roles"]["candidate"], "historical native role")
        parser = helper.load("historical_parser", capsule / "assess.py")
        checks = helper.load("historical_checks", root / previous_policy["helpers"]["checks"])
        events = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
        replay = parser.assess(events, result["exit"], previous_policy, checks, original=None, run_binding=metadata)
        for key in ["complete", "errors", "infrastructure_faults", "rows", "starts", "ends", "run_info", "held_signature", "regression_signature"]:
            helper.need(replay[key] == saved[key], "historical raw replay: " + key)
        helper.need(len(replay["rows"]) == record["assertions"] and len(replay["ends"]) == record["pages"], "historical cardinality")
        histories.append({"record": record, "assessment": saved})
    return histories


def signatures(assessment):
    result = {}
    for event in assessment["rows"] + assessment["ends"]:
        identity = (event["action"], event["test"], event.get("subtest"))
        if identity in result:
            raise ValueError("duplicate comparison identity")
        result[identity] = {key: event[key] for key in ["status", "message", "expected", "known_intermittent"] if key in event}
    return result


def compare(current, histories):
    output = {"complete": current["complete"] and current["execution_preserved"], "native_fix_acceptance": False, "comparisons": []}
    after = signatures(current)
    for history in histories:
        old = history["assessment"]
        if {k:v for k,v in current["run_info"].items() if k != "browser_build_id"} != {k:v for k,v in old["run_info"].items() if k != "browser_build_id"}:
            raise ValueError("comparison run_info changed outside bound BuildID")
        before = signatures(old)
        if set(before) != set(after):
            raise ValueError("comparison identities changed")
        changes = [{"identity": list(key), "before": before[key], "after": after[key]} for key in before if before[key] != after[key]]
        output["comparisons"].append({"baseline": history["record"], "same_full_signatures": len(before)-len(changes),
            "before_statuses": dict(Counter(e["status"] for e in old["rows"])), "after_statuses": dict(Counter(e["status"] for e in current["rows"])),
            "changed_statuses": sum(before[key]["status"] != after[key]["status"] for key in before),
            "changed_fail_messages": sum(before[key]["status"] == after[key]["status"] == "FAIL" and before[key].get("message") != after[key].get("message") for key in before),
            "changes": changes})
    output["limits"] = "Full raw messages retained, including reference diagnostic ports. No normalization, conformance verdict or automatic acceptance. Conditional color/weight initials need separate interpretation."
    return output
