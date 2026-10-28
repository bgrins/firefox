import os
import subprocess

def validate(root, here, policy, helper):
    receipt = helper.read(here / "HEAD-SUCCESSION.json")
    helper.need(policy["frozen_head"] == receipt["new_head"] and policy["epoch_sha256"] == receipt["epoch_sha256"], "exact successor HEAD and epoch")
    for name, pin in receipt["pins"].items():
        helper.need(helper.sha(root / name) == pin, "signed succession evidence: " + name)
    previous = root / receipt["predecessor"]
    helper.authenticate(previous, receipt["predecessor_manifest_sha256"])
    old_policy = helper.read(previous / "POLICY.json")
    comparable = dict(policy, frozen_head=old_policy["frozen_head"], epoch_sha256=old_policy["epoch_sha256"])
    helper.need(comparable == old_policy and old_policy["frozen_head"] == receipt["old_head"], "only fixed HEAD/epoch bindings may change")
    for name in ["SOURCE-PINS.json", "SELECTED.json", "TARGET-SUBTESTS.json", "SUBSET-MANIFEST.json"]:
        helper.need((here / name).read_bytes() == (previous / name).read_bytes(), "unchanged calibration fixture: " + name)
    for item in helper.read(here / "SOURCE-PINS.json").values():
        if item["exists"]:
            helper.need(helper.sha(here / item["capture"]) == item["sha256"], "unchanged capture")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    helper.need(all(not env.get(k) for k in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"]), "unexpected Git environment")
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(root), *args], env=env, stderr=subprocess.PIPE)
    parent = receipt["old_head"]
    helper.need(len(receipt["receipts"]) == 4, "exact four signed research commits")
    for name in receipt["receipts"]:
        item = helper.read(root / name)
        helper.need(item["parent"] == parent and item["signature_verified"] and item["working_bodies_and_nested_index_preserved"], "signed receipt chain")
        helper.need(git("rev-list", "--parents", "-n", "1", item["commit"]).decode().split() == [item["commit"], parent], "actual single commit parent")
        helper.need(git("rev-parse", item["commit"] + "^{tree}").decode().strip() == item["tree"], "actual signed tree")
        git("-c", "gpg.ssh.allowedSignersFile=" + str(root / "artifacts/css-local-signing-20261027-v1/allowed-signers"), "verify-commit", item["commit"])
        paths = [n.decode() for n in git("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", item["commit"]).split(b"\0") if n]
        helper.need(set(paths) == set(item["files"]) and all(n.startswith("artifacts/") and not n.startswith("artifacts/css-spec-lean") for n in paths), "exact artifact-only changes without nested repository")
        parent = item["commit"]
    helper.need(parent == receipt["new_head"], "exact successor endpoint")
    helper.need(not git("diff", "--name-only", receipt["old_head"], receipt["new_head"], "--", ".", ":(exclude)artifacts"), "native tree unchanged")
    before, after = [helper.read(root / receipt[key]) for key in ["before_epoch", "after_epoch"]]
    helper.need([before["semantic_index"]["head"], after["semantic_index"]["head"]] == [receipt["old_head"], receipt["new_head"]], "preserved signing epoch pair")
    helper.need(helper.sha(root / receipt["after_epoch"]) == policy["epoch_sha256"], "signed final epoch")
    pin_sets = [{n:p for n,p in epoch["pins"].items() if not n.startswith("artifacts/")} for epoch in [before,after]]
    helper.need(pin_sets[0] == pin_sets[1], "source/binary pins changed across signing")
    helper.need(before["registered_number_transition"] == after["registered_number_transition"], "build provenance changed")
    helper.require_compiled_transition(after, "candidate")
    helper.need(after["registered_number_transition"]["accepted"] is False and after["registered_number_transition"]["last_phase"] == "head-candidate-build-2", "admission-only build2")
    helper.need(all(after["pins"].get(n) == pin for n,pin in dict(policy["native_sources"], **policy["candidate_binaries"]).items()), "source/build2 pins")
    final = helper.read(root / receipt["signing_directory"] / "FINAL-CHECK.json")
    helper.need(final["head"] == receipt["new_head"] and final["signatures_verified"] and final["runtime_epoch_synchronized"] and not final["candidate_accepted"] and final["current_epoch_sha256"] == policy["epoch_sha256"], "final signed preservation")
    ledger = helper.read(root / receipt["signing_directory"] / "ROADMAP-UPDATE.json")
    prior = helper.read(root / ledger["prior_authorized_ledger_update"])
    helper.need(prior["after"] == ledger["before"], "v17 to v18 ledger continuation")
    helper.need(all(after["pins"].get(n) == pin for n,pin in ledger["after"].items()), "ledger pins")
    return {"old_head":receipt["old_head"], "new_head":receipt["new_head"], "signed_research_commits":4, "source_binaries_build_provenance_unchanged":True}
