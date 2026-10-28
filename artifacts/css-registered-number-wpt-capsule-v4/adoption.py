import json
from pathlib import Path


def semantic_policy(policy):
    result = dict(policy)
    result["source_roles"] = {"original": policy["source_roles"]["original"]}
    return result


def validate(root, here, baseline_path, baseline_sha, policy, helper):
    receipt = helper.read(here / "ADOPTED-ORIGINAL.json")
    previous = root / receipt["predecessor"]
    runtime = root / receipt["runtime"]
    helper.need(baseline_path == runtime / "ASSESSMENT.json" and
                baseline_sha == receipt["assessment_sha256"], "only the exact adopted original assessment is permitted")
    helper.authenticate(previous, receipt["predecessor_manifest_sha256"])
    old_policy = helper.read(previous / "POLICY.json")
    helper.need(semantic_policy(policy) == semantic_policy(old_policy), "adopted original experiment policy drift")
    for name in ["SOURCE-PINS.json", "SELECTED.json", "TARGET-SUBTESTS.json", "HELD-SUBTESTS.json",
                 "HELD-COMPARISON-POLICY.json", "REGRESSION-SUBTESTS.json", "SUBSET-MANIFEST.json",
                 "EXISTING-MANIFEST-ENTRIES.json", "REFERENCES-TO-COPY.json", "assess.py"]:
        helper.need((here / name).read_bytes() == (previous / name).read_bytes(), "adopted original fixture/assessor drift: " + name)
    old_pins = helper.read(previous / "SOURCE-PINS.json")
    for item in old_pins.values():
        if item["exists"]:
            helper.need(helper.sha(here / item["capture"]) == item["sha256"], "adopted original capture drift")
    files, links = {}, {}
    for path in runtime.rglob("*"):
        if path.is_symlink():
            links[str(path.relative_to(runtime))] = str(path.readlink())
        elif path.is_file():
            files[str(path.relative_to(runtime))] = helper.sha(path)
    helper.need(files == receipt["runtime_files"] and links == receipt["runtime_symlinks"],
                "adopted original runtime inventory changed")
    original = helper.read(baseline_path)
    result = helper.read(runtime / "RESULT.json")
    epoch = helper.read(runtime / "EPOCH.json")
    command = helper.read(runtime / "COMMAND.json")
    helper.need(helper.sha(runtime / "RESULT.json") == receipt["result_sha256"], "adopted result binding")
    helper.need(original["phase"] == result["phase"] == command["phase"] == receipt["phase"] and
                original["capsule_manifest_sha256"] == command["wrapper_manifest_sha256"] == receipt["predecessor_manifest_sha256"],
                "adopted predecessor provenance")
    helper.need(original["complete"] and original["execution_preserved"] and result["observation_gate_passed"] and
                result["execution_error"] is None and result["preservation_error"] is None,
                "adopted original must be complete and preserved")
    helper.need(helper.sha(runtime / "EPOCH.json") == original["epoch_sha256"] == command["epoch_sha256"] == receipt["epoch_sha256"],
                "adopted epoch digest")
    helper.need(epoch["semantic_index"]["head"] == original["run_binding"]["revision"] == policy["frozen_head"] == receipt["frozen_head"],
                "adopted frozen HEAD")
    helper.require_compiled_transition(epoch, "original")
    helper.need(original["native_sources"] == policy["source_roles"]["original"], "adopted original sources")
    helper.need(all(epoch["pins"].get(name) == pin for name, pin in original["native_sources"].items()), "adopted epoch native sources")
    binary_pins = helper.read(runtime / "NORMAL-BINARIES.json")
    helper.need(all(epoch["pins"].get(name) == pin for name, pin in binary_pins.items()), "adopted built binaries")
    helper.need(original["run_binding"] == helper.read(runtime / "APPLICATION-METADATA.json") ==
                helper.read(runtime / "APPLICATION-METADATA-POST.json"), "adopted application metadata preservation")
    helper.need(helper.read(runtime / "PRE.json") == helper.read(runtime / "POST.json"), "adopted full preservation")
    cleanup = helper.read(runtime / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "adopted cleanup")
    parser = helper.load("adopted_original_assessment", here / "assess.py")
    checks = helper.load("adopted_original_checks", root / policy["helpers"]["checks"])
    events = [json.loads(line) for line in (runtime / "raw.jsonl").read_text().splitlines()]
    derived = parser.assess(events, result["exit"], policy, checks, run_binding=original["run_binding"])
    helper.need(derived["complete"] and all(original.get(name) == value for name, value in derived.items()),
                "adopted raw outcomes do not reproduce assessment")
    return {"adopted": True, "predecessor": receipt["predecessor"],
            "predecessor_manifest_sha256": receipt["predecessor_manifest_sha256"],
            "assessment_path": str(baseline_path), "assessment_sha256": baseline_sha,
            "result_sha256": receipt["result_sha256"], "phase": receipt["phase"],
            "retains_original_provenance": True}
