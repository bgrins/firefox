from pathlib import Path


def semantic_policy(policy):
    value = dict(policy)
    if "original_frozen_head" in value:
        value["frozen_head"] = value.pop("original_frozen_head")
    value["source_roles"] = {"original": policy["source_roles"]["original"]}
    del value["wpt_capsule"]
    del value["wpt_capsule_manifest_sha256"]
    return value


def validate(root, here, original_path, original_sha, policy, helper):
    receipt = helper.read(here / "ADOPTED-ORIGINAL.json")
    previous = root / receipt["predecessor"]
    runtime = root / receipt["runtime"]
    helper.need(original_path == runtime / "RESULT.json" and original_sha == receipt["result_sha256"],
                "only exact predecessor observation is permitted")
    helper.authenticate(previous, receipt["predecessor_manifest_sha256"])
    helper.need(semantic_policy(policy) == semantic_policy(helper.read(previous / "POLICY.json")),
                "observation original experiment policy drift")
    helper.need(policy["wpt_capsule"] == receipt["active_wpt_capsule"] and
                policy["wpt_capsule_manifest_sha256"] == receipt["active_wpt_manifest_sha256"],
                "observation active WPT capsule binding")
    for name in ["report.js", "report.html", "CASES.json", "validate.py"]:
        helper.need((here / name).read_bytes() == (previous / name).read_bytes(), "observation payload or validator drift: " + name)
    files = {}
    for path in runtime.rglob("*"):
        helper.need(not path.is_symlink(), "adopted observation runtime symlink")
        if path.is_file():
            files[str(path.relative_to(runtime))] = helper.sha(path)
    helper.need(files == receipt["runtime_files"], "adopted observation runtime changed")
    original = helper.read(original_path)
    command = helper.read(runtime / "COMMAND.json")
    epoch = helper.read(runtime / "EPOCH.json")
    helper.need(original["manifest_sha256"] == command["manifest_sha256"] == receipt["predecessor_manifest_sha256"] and
                original["phase"] == command["phase"] == receipt["phase"], "observation predecessor provenance")
    helper.need(original["complete"] and original["execution_preserved"] and original["error"] is None and
                original["preservation_error"] is None, "adopted observation incomplete")
    helper.need(original["epoch_sha256"] == command["epoch_sha256"] == helper.sha(runtime / "EPOCH.json"), "observation epoch binding")
    helper.need(epoch["semantic_index"]["head"] == original["application_metadata"]["revision"] == policy["original_frozen_head"] == receipt["frozen_head"],
                "observation frozen HEAD")
    helper.require_compiled_transition(epoch, "original")
    helper.need(original["native_sources"] == policy["source_roles"]["original"], "observation original native sources")
    helper.need(all(epoch["pins"].get(name) == pin for name, pin in original["native_sources"].items()), "observation epoch native sources")
    helper.need(original["normal_binaries"] == helper.read(runtime / "NORMAL-BINARIES.json") and
                all(epoch["pins"].get(name) == pin for name, pin in original["normal_binaries"].items()), "observation built binaries")
    helper.need(original["application_metadata"] == helper.read(runtime / "APPLICATION-METADATA.json") ==
                helper.read(runtime / "APPLICATION-METADATA-POST.json"), "observation metadata preservation")
    helper.need(helper.read(runtime / "PRE.json") == helper.read(runtime / "POST.json"), "observation full preservation")
    cleanup = helper.read(runtime / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["profile_removed"] and cleanup["server_thread_stopped"], "observation cleanup")
    wrapper = root / policy["wpt_capsule"]
    helper.authenticate(wrapper, policy["wpt_capsule_manifest_sha256"])
    wrapper_policy = helper.read(wrapper / "POLICY.json")
    helper.need(policy["frozen_head"] == wrapper_policy["frozen_head"] and
                policy["original_frozen_head"] == wrapper_policy["original_frozen_head"], "exact observer signed HEAD pair")
    normative_adoption = helper.load("observer_normative_adoption", wrapper / "adoption.py")
    normative_path = root / receipt["normative_assessment"]
    helper.need(command["normative_assessment"] == str(normative_path) and
                command["normative_sha256"] == original["normative_assessment_sha256"] == receipt["normative_assessment_sha256"],
                "observation original normative binding")
    normative_adoption.validate(root, wrapper, normative_path, receipt["normative_assessment_sha256"],
                               helper.read(wrapper / "POLICY.json"), helper)
    normative = helper.read(normative_path)
    helper.need(normative["run_binding"] == original["application_metadata"] and
                normative["epoch_sha256"] == original["epoch_sha256"] and normative["phase"] == original["normative_phase"],
                "observation original normative environment")
    raw = helper.read(runtime / "RAW.json")
    helper.need(len(raw["payloads"]) == 1 and not raw["network_errors"], "observation raw completeness")
    validation = helper.load("adopted_observer_validator", here / "validate.py")
    helper.need(validation.summarize(raw["payloads"][0]) == original["summary"], "observation raw summary changed")
    helper.need(original["profile_configuration"] == "fresh default profile; WPT preferences are not imported",
                "observation original profile convention")
    return {"adopted": True, "predecessor": receipt["predecessor"],
            "predecessor_manifest_sha256": receipt["predecessor_manifest_sha256"],
            "result_path": str(original_path), "result_sha256": original_sha,
            "phase": receipt["phase"], "retains_original_provenance": True}
