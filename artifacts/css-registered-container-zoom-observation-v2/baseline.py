def validate(root, here, policy, helper, validation):
    base = root / policy["baseline_package"]
    helper.authenticate(base, policy["baseline_manifest_sha256"])
    for name in ["report.html", "report.js", "validate.py", "CASES.json", "PROTOCOL.json"]:
        helper.need((base / name).read_bytes() == (here / name).read_bytes(), "unchanged observer: " + name)
    old_policy = helper.read(base / "POLICY.json")
    directory = root / policy["baseline_directory"]
    for name, pin in helper.read(here / "BASELINE-PINS.json").items():
        path = directory / name
        helper.need(path.is_file() and not path.is_symlink() and helper.sha(path) == pin, "exact observer baseline: " + name)
    result = helper.read(directory / "RESULT.json")
    helper.need(result["complete"] and result["execution_preserved"] and result["error"] is None and result["preservation_error"] is None, "complete preserved observer baseline")
    helper.need(result["manifest_sha256"] == policy["baseline_manifest_sha256"] and result["epoch_sha256"] == old_policy["epoch_sha256"] and result["phase"] == "admission-only-1" and result["source_role"] == "admission-only-v3-build2", "original observer provenance")
    helper.need(result["native_sources"] == old_policy["source_roles"]["candidate"] and result["normal_binaries"] == old_policy["candidate_binaries"], "baseline source/binary roles")
    helper.need(result["application_metadata"] == helper.read(directory / "APPLICATION-METADATA.json") == helper.read(directory / "APPLICATION-METADATA-POST.json"), "baseline metadata")
    helper.need(result["application_metadata"]["revision"] == policy["frozen_head"] and helper.read(directory / "EPOCH.json")["semantic_index"]["head"] == policy["frozen_head"], "same frozen HEAD")
    helper.need(helper.read(directory / "PRE.json") == helper.read(directory / "POST.json"), "baseline preservation")
    cleanup = helper.read(directory / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["profile_removed"] and cleanup["server_thread_stopped"], "baseline cleanup")
    raw = helper.read(directory / "RAW.json")
    helper.need(len(raw["payloads"]) == 1 and not raw["network_errors"] and validation.summarize(raw["payloads"][0]) == result["summary"], "baseline raw replay")
    return result


def compare(original, candidate, validation):
    validation.summarize({"observation":original})
    validation.summarize({"observation":candidate})
    changes = {}
    for family in ["rows", "sequences"]:
        changes[family] = [{"id":before["id"],"original":before,"candidate":after} for before,after in zip(original[family],candidate[family]) if before != after]
    return {"changed_cases":len(changes["rows"]),"changed_sequences":len(changes["sequences"]),"changes":changes,
            "normative_verdict":"not evaluated","native_fix_acceptance":False,
            "limitation":"Raw ordinary/registered deltas; canonical container coordinate contract remains an inference. Ordinary cqw has existing bug1894104."}
