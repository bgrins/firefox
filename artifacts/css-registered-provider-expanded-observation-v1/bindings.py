import hashlib
import os
from pathlib import Path
import subprocess


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here / "EXPERIMENT.json")
    for key in ["frozen_head", "tests", "target_subtests", "held_subtests", "source_roles", "installed_tests"]:
        helper.need(policy[key] == experiment[key], "fixed observation input: " + key)
    helper.need(policy["phase"] == "observation-1" and policy["regression_subtests"] == {}, "observation mode")
    helper.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "current harness HEAD")
    helper.need(epoch["modified_native_paths"] == [], "accepted baseline has no native working edits")
    helper.need(epoch["registered_number_transition"] == {
        "role": "candidate", "variant": "zoom-standalone-v1", "compiled": True,
        "accepted": True, "last_phase": "zoom-standalone-candidate-build-2"
    }, "actual accepted baseline build role")
    checkpoint = root / "artifacts/css-local-signing-20261027-v25/CURRENT-EPOCH.json"
    helper.need(helper.sha(checkpoint) == policy["epoch_sha256"] and helper.read(checkpoint) == epoch, "signed synchronized epoch")
    build = Path("artifacts/css-registered-number-native-runtime-v1/zoom-standalone-candidate-build-2")
    helper.need(policy["build_result"] == str(build / "RESULT.json") and policy["build_epoch"] == str(build / "EPOCH.json"), "actual historical build paths")
    helper.need(helper.sha(root / policy["build_result"]) == policy["build_result_sha256"], "historical build result bytes")
    result = helper.read(root / policy["build_result"])
    helper.need(result["source_role"] == "candidate" and result["command_success"] and result["preservation_verified"] and result["error"] is None and not result["owned_processes"] and not result["publication_errors"], "successful terminal build")
    helper.need(helper.sha(root / policy["build_epoch"]) == policy["build_epoch_sha256"], "saved build epoch bytes")
    built = helper.read(root / policy["build_epoch"])
    transition = dict(built["registered_number_transition"])
    helper.need(transition.pop("accepted") is False, "historical build preceded acceptance")
    current = dict(epoch["registered_number_transition"])
    helper.need(current.pop("accepted") is True and current == transition, "same actual compilation after acceptance")
    for key in ["installed_identities", "untracked_native", "nested_semantic_index"]:
        helper.need(built[key] == epoch[key], "unchanged compilation state: " + key)
    nonartifact = lambda e: {n: p for n, p in e["pins"].items() if not n.startswith("artifacts/")}
    helper.need(nonartifact(built) == nonartifact(epoch), "all source, binary and config bodies unchanged")
    helper.need(len(policy["source_roles"]["candidate"]) == 9 and all(epoch["pins"].get(n) == pin for n, pin in policy["source_roles"]["candidate"].items()), "nine native source bindings")
    helper.need(len(policy["installed_tests"]) == 7 and all(epoch["pins"].get(n) == pin for n, pin in policy["installed_tests"].items()), "seven accepted test bodies")
    helper.need(set(policy["phase_binaries"]) == set(policy["normal_binaries"]) and all(epoch["pins"].get(n) == pin for n, pin in policy["phase_binaries"].items()), "historical compiled binary bytes")

    succession = helper.read(here / "SUCCESSION.json")
    helper.need(built["semantic_index"]["head"] == succession["build_head"], "historical build HEAD retained")
    helper.need(succession["observation_head"] == policy["frozen_head"] and len(succession["commits"]) == 7, "seven publication/checkpoint successors")
    payload = helper.read(root / "artifacts/css-registered-zoom-fix139-payload-v1/PAYLOAD.json")["source_roles"]
    helper.need(len(payload) == 14 and sum(v["kind"] == "native" for v in payload.values()) == 7, "accepted fourteen-path payload")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args], cwd=root, env=env)
    parent, publications = succession["build_head"], []
    for item in succession["commits"]:
        helper.need(helper.sha(root / item["path"]) == item["sha256"], "signed receipt bytes")
        receipt = helper.read(root / item["path"])
        helper.need(receipt["signature_verified"] and all(receipt[k] == item[k] for k in ["commit", "parent", "tree", "files"]), "actual receipt binding")
        commit = item["commit"]
        helper.need(item["parent"] == parent and git("rev-list", "--parents", "-n", "1", commit).decode().split() == [commit, parent], "actual linear parent")
        helper.need(git("rev-parse", commit + "^{tree}").decode().strip() == item["tree"], "actual committed tree")
        paths = git("diff", "--name-only", parent, commit).decode().splitlines()
        helper.need(sorted(paths) == sorted(item["files"]), "exact committed path list")
        if item["native_publication"]:
            helper.need(sorted(paths) == sorted(payload), "only exact already-tested native/WPT payload published")
            for name, role in payload.items():
                pin = role["candidate_sha256"]
                helper.need(built["pins"].get(name) == epoch["pins"].get(name) == pin, "published body equals compiled body: " + name)
                helper.need(hashlib.sha256(git("show", commit + ":" + name)).hexdigest() == pin, "actual committed payload body")
            publications.append(commit)
        else:
            helper.need(all(n.startswith("artifacts/") and n != "artifacts/css-spec-lean" and not n.startswith("artifacts/css-spec-lean/") for n in paths), "artifact-only successor")
        checked = subprocess.run(["git", "--no-optional-locks", "-c", "gpg.ssh.allowedSignersFile=" + str(root / "artifacts/css-local-signing-20261027-v1/allowed-signers"), "verify-commit", commit], cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        helper.need(checked.returncode == 0, "actual SSH signature")
        parent = commit
    helper.need(parent == policy["frozen_head"] and len(publications) == 1, "single native publication and full chain")
    helper.need(epoch["accepted_registered_zoom"]["fix"] == 139 and epoch["accepted_registered_zoom"]["native_commit"] == publications[0], "accepted overlay identity")
    return {"phase": "observation-1", "build_result": policy["build_result"],
            "build_epoch_sha256": policy["build_epoch_sha256"], "build_head": succession["build_head"],
            "observation_head": policy["frozen_head"], "observation_epoch_sha256": policy["epoch_sha256"],
            "native_sources": policy["source_roles"]["candidate"], "binaries": policy["phase_binaries"],
            "already_compiled_native_publication": publications[0],
            "all_successors_artifact_only": False, "new_native_fix_acceptance": False,
            "build_revision_or_metadata_rewritten": False}
