import copy
import os
from pathlib import Path


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here / "EXPERIMENT.json")
    for key in ["tests", "target_subtests", "held_subtests", "installed_tests"]:
        helper.need(policy[key] == experiment[key], "same fixed experiment: " + key)
    helper.need(experiment["frozen_head"] == policy["historical_head"], "historical experiment HEAD retained")
    helper.need(policy["phase"] == "observation-1" and policy["regression_subtests"] == {}, "observation mode")
    helper.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "unchanged paired harness HEAD")
    helper.need(policy["transition_variant"] == "registered-provider-default-v5" and policy["build_label"] == "provider-default-candidate-build-3", "provider candidate build identity")
    helper.need(epoch["registered_number_transition"] == {
        "role": "candidate", "variant": policy["transition_variant"], "compiled": True,
        "accepted": False, "last_phase": policy["build_label"]
    }, "compiled unaccepted provider candidate")
    proposal = root / policy["proposal"]
    helper.authenticate(proposal, policy["proposal_manifest_sha256"])
    roles = helper.read(proposal / "SOURCE-ROLES.json")
    paths = {"servo/components/style/custom_properties.rs", "servo/components/style/properties/cascade.rs"}
    helper.need(set(roles) == paths and epoch["modified_native_paths"] == ["servo/components/style/custom_properties.rs"], "one dirty native path after ordinary restoration")
    sources = dict(experiment["source_roles"]["candidate"])
    for name, role in roles.items():
        helper.need(sources[name] == role["base_sha256"], "paired source preimage")
        helper.need(helper.sha(proposal / "ordinary-restored" / name) == role["ordinary_restored_sha256"], "sealed candidate body")
        sources[name] = role["ordinary_restored_sha256"]
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
    helper.need(helper.sha(here / "OBSERVATION-EPOCH.json") == policy["epoch_sha256"] == policy["build_epoch_sha256"], "actual staged build epoch identity")
    helper.need(helper.read(here / "OBSERVATION-EPOCH.json") == compiled == epoch, "no projection from saved build epoch")
    helper.need(epoch["staged_working"] == {}, "clean post-signing index")
    signed_capsule = root / policy["signing_build_capsule"]
    helper.authenticate(signed_capsule, policy["signing_build_capsule_sha256"])
    signed = helper.read(signed_capsule / "INITIAL-EPOCH.json")
    succession = helper.load("observer_signed_succession", signed_capsule / "succession.py")
    preservation = helper.load("observer_succession_git", root / policy["helpers"]["preservation"])
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    succession.validate(root, signed_capsule, helper.read(signed_capsule / "POLICY.json"), signed, preservation, environment)
    helper.need(signed["semantic_index"]["head"] == policy["frozen_head"], "exact signed successor HEAD")
    signing_initial = helper.read(root / helper.read(signed_capsule / "POLICY.json")["signing"] / "INITIAL-EPOCH.json")
    helper.need(signing_initial["semantic_index"]["head"] == policy["historical_head"], "exact historical HEAD")
    expected = copy.deepcopy(signed)
    binary_paths = ["objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
                    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL",
                    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL",
                    "objdir-full.noindex/dist/bin/gtest/XUL"]
    for name in binary_paths:
        expected["pins"][name] = compiled["pins"][name]
    expected["raw_index_observation"]["current"] = compiled["raw_index_observation"]["current"]
    expected["registered_number_transition"] = compiled["registered_number_transition"]
    helper.need(expected == compiled, "only actual build binaries, raw-index observation and compiled transition changed after signing")
    helper.need(set(policy["phase_binaries"]) == set(policy["normal_binaries"]) and all(epoch["pins"].get(n) == pin for n, pin in policy["phase_binaries"].items()), "actual normal build binaries")
    return {"phase": policy["phase"], "build_result": policy["build_result"],
            "build_epoch_sha256": policy["build_epoch_sha256"], "build_head": policy["frozen_head"],
            "native_sources": sources, "binaries": policy["phase_binaries"],
            "accepted_zoom_preserved": True, "new_native_fix_acceptance": False,
            "build_revision_or_metadata_rewritten": False}
