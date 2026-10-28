import copy
from pathlib import Path


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here / "EXPERIMENT.json")
    for key in ["frozen_head", "tests", "target_subtests", "held_subtests", "installed_tests"]:
        helper.need(policy[key] == experiment[key], "same fixed experiment: " + key)
    helper.need(policy["phase"] == "observation-1" and policy["regression_subtests"] == {}, "observation mode")
    helper.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "unchanged paired harness HEAD")
    helper.need(policy["transition_variant"] == "registered-provider-default-v4" and policy["build_label"] == "provider-default-candidate-build-2", "provider candidate build identity")
    helper.need(epoch["registered_number_transition"] == {
        "role": "candidate", "variant": policy["transition_variant"], "compiled": True,
        "accepted": False, "last_phase": policy["build_label"]
    }, "compiled unaccepted provider candidate")
    proposal = root / policy["proposal"]
    helper.authenticate(proposal, policy["proposal_manifest_sha256"])
    roles = helper.read(proposal / "SOURCE-ROLES.json")
    paths = {"servo/components/style/custom_properties.rs", "servo/components/style/properties/cascade.rs"}
    helper.need(set(roles) == paths and set(epoch["modified_native_paths"]) == paths, "exact two native edits")
    sources = dict(experiment["source_roles"]["candidate"])
    for name, role in roles.items():
        helper.need(sources[name] == role["base_sha256"], "paired source preimage")
        helper.need(helper.sha(proposal / "candidate" / name) == role["candidate_sha256"], "sealed candidate body")
        sources[name] = role["candidate_sha256"]
    helper.need(len(sources) == 9 and policy["source_roles"] == {"candidate": sources}, "two candidate sources and seven accepted zoom sources")
    helper.need(all(epoch["pins"].get(n) == pin and n in epoch["installed_identities"] for n, pin in sources.items()), "compiled native bodies and identities")
    helper.need(len(policy["installed_tests"]) == 7 and all(epoch["pins"].get(n) == pin and n in epoch["installed_identities"] for n, pin in policy["installed_tests"].items()), "seven accepted test bodies and identities")
    helper.need(epoch["accepted_registered_zoom"]["fix"] == 139, "accepted zoom repair preserved")
    build = Path("artifacts/css-registered-number-native-runtime-v1") / policy["build_label"]
    helper.need(policy["build_result"] == str(build / "RESULT.json") and policy["build_epoch"] == str(build / "EPOCH.json"), "actual build paths")
    helper.need(helper.sha(root / policy["build_result"]) == policy["build_result_sha256"], "actual build result bytes")
    result = helper.read(root / policy["build_result"])
    helper.need(result["source_role"] == "candidate" and result["command_success"] and result["preservation_verified"] and result["error"] is None and not result["owned_processes"] and not result["publication_errors"], "successful terminal candidate build")
    helper.need(helper.sha(root / policy["build_epoch"]) == policy["build_epoch_sha256"], "actual saved build epoch")
    compiled = helper.read(root / policy["build_epoch"])
    staging = helper.read(here / "STAGING.json")
    helper.need(staging["build_epoch_sha256"] == policy["build_epoch_sha256"], "staging derives from actual build")
    helper.need(helper.sha(here / "OBSERVATION-EPOCH.json") == policy["epoch_sha256"] == staging["observation_epoch_sha256"], "explicit staged observation epoch")
    helper.need(helper.read(here / "OBSERVATION-EPOCH.json") == epoch, "exact observation record")
    helper.need(helper.sha(root / staging["staged_patch"]) == staging["staged_patch_sha256"], "exact preserved signing patch")
    helper.need(set(staging["staged_files"]) == set(staging["staged_working"]) and all(n.startswith("artifacts/") for n in staging["staged_files"]), "artifact-only staging scope")
    helper.need(staging["semantic_index"]["head"] == compiled["semantic_index"]["head"] and staging["semantic_index"]["working_diff"] == compiled["semantic_index"]["working_diff"], "unchanged build HEAD and unstaged sources")
    expected = copy.deepcopy(compiled)
    expected["semantic_index"] = staging["semantic_index"]
    expected["raw_index_observation"]["current"] = staging["raw_index"]
    expected["staged_working"] = staging["staged_working"]
    helper.need(expected == epoch, "only recorded artifact staging differs from build epoch")
    helper.need(set(policy["phase_binaries"]) == set(policy["normal_binaries"]) and all(epoch["pins"].get(n) == pin for n, pin in policy["phase_binaries"].items()), "actual normal build binaries")
    return {"phase": policy["phase"], "build_result": policy["build_result"],
            "build_epoch_sha256": policy["build_epoch_sha256"], "build_head": policy["frozen_head"],
            "native_sources": sources, "binaries": policy["phase_binaries"],
            "accepted_zoom_preserved": True, "new_native_fix_acceptance": False,
            "build_revision_or_metadata_rewritten": False}
