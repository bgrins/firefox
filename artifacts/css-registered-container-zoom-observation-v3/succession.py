import json
import os
import subprocess


def validate_core(receipt, policy, old_policy, before, after, calibration_epoch, need):
    need(receipt["old_head"] == "1c7870c6d36d002b1c785ec2a6251ddc4ca2a040" and
         receipt["new_head"] == "6eb538c23bcf3dde9c7631a1c826cba4de562462", "exact signed HEAD pair")
    need(policy["frozen_head"] == receipt["new_head"] and policy["original_frozen_head"] == receipt["old_head"] and
         policy["epoch_sha256"] == receipt["epoch_sha256"] and policy["calibration_epoch_sha256"] == receipt["calibration_epoch_sha256"], "policy succession bindings")
    expected = dict(old_policy, execution_enabled=True, frozen_head=receipt["new_head"], epoch_sha256=receipt["epoch_sha256"],
                    original_frozen_head=receipt["old_head"], calibration_epoch_sha256=receipt["calibration_epoch_sha256"],
                    calibration_assessment_sha256="8436235d45f7750de2a7328dad6e4694bdf97bc57cfc0c3b55925b8c5fb7b870")
    need(policy == expected and old_policy["frozen_head"] == receipt["old_head"] and
         old_policy["epoch_sha256"] == receipt["calibration_epoch_sha256"], "only exact disabled-to-bound successor policy changes")
    need([e["semantic_index"]["head"] for e in [calibration_epoch, before, after]] ==
         [receipt["old_head"], receipt["old_head"], receipt["new_head"]], "exact calibration/signing HEAD chain")
    pins = [{n:v for n,v in e["pins"].items() if not n.startswith("artifacts/")} for e in [calibration_epoch,before,after]]
    need(pins[0] == pins[1] == pins[2], "source/binary pins changed across signing")
    transition = {"role":"candidate","variant":"zoom-normalization-v3","compiled":True,"accepted":False,"last_phase":"zoom-normalization-build-2"}
    need(all(e["registered_number_transition"] == transition for e in [calibration_epoch,before,after]), "build provenance changed")
    required = dict(policy["source_roles"]["candidate"], **policy["candidate_binaries"])
    need(len(policy["source_roles"]["candidate"]) == 9 and all(after["pins"].get(n) == v for n,v in required.items()), "exact nine native and binary bindings")


def validate_metadata(actual, historical, receipt, need):
    need(actual["revision"] == receipt["new_head"] and historical["revision"] == receipt["old_head"], "exact metadata HEAD pair")
    need(dict(actual, revision=receipt["old_head"]) == historical, "only provenance HEAD may differ in application metadata")


def validate(root, here, policy, helper):
    receipt = helper.read(here / "HEAD-SUCCESSION.json")
    for name,pin in receipt["pins"].items():
        helper.need(helper.sha(root / name) == pin, "signed/candidate evidence: " + name)
    previous = root / receipt["predecessor"]
    helper.authenticate(previous, receipt["predecessor_manifest_sha256"])
    old_policy = helper.read(previous / "POLICY.json")
    for name in ["report.html","report.js","validate.py","CASES.json","PROTOCOL.json","BASELINE-PINS.json"]:
        helper.need((here / name).read_bytes() == (previous / name).read_bytes(), "unchanged observer payload: " + name)
    before,after = [helper.read(root / receipt[key]) for key in ["before_epoch","after_epoch"]]
    candidate = root / receipt["candidate_runtime"]
    calibration_epoch = helper.read(candidate / "EPOCH.json")
    validate_core(receipt,policy,old_policy,before,after,calibration_epoch,helper.need)
    helper.need(helper.sha(root / receipt["after_epoch"]) == policy["epoch_sha256"] and
                helper.sha(candidate / "EPOCH.json") == policy["calibration_epoch_sha256"], "exact current and historical epoch bytes")
    assessment = helper.read(candidate / "ASSESSMENT.json")
    result = helper.read(candidate / "RESULT.json")
    helper.need(helper.sha(candidate / "ASSESSMENT.json") == policy["calibration_assessment_sha256"] and
                assessment["complete"] and assessment["execution_preserved"] and result["observation_gate_passed"] and
                result["execution_error"] is None and result["preservation_error"] is None, "complete preserved exact candidate calibration")
    helper.need(assessment["epoch_sha256"] == policy["calibration_epoch_sha256"] and
                assessment["native_sources"] == policy["source_roles"]["candidate"] and
                assessment["capsule_manifest_sha256"] == policy["wpt_capsule_manifest_sha256"], "candidate provenance")
    metadata = helper.read(candidate / "APPLICATION-METADATA.json")
    helper.need(metadata == helper.read(candidate / "APPLICATION-METADATA-POST.json") == assessment["run_binding"] and
                metadata["revision"] == receipt["old_head"], "historical metadata preserved")
    helper.need(helper.read(candidate / "PRE.json") == helper.read(candidate / "POST.json") and
                helper.read(candidate / "NORMAL-BINARIES.json") == policy["candidate_binaries"], "candidate preservation/binaries")
    cleanup = helper.read(candidate / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "candidate cleanup")
    events = [json.loads(line) for line in (candidate / "raw.jsonl").read_text().splitlines()]
    helper.need([e for e in events if e.get("action") == "test_status"] == assessment["rows"], "exact raw candidate rows")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    helper.need(all(not env.get(k) for k in ["GIT_DIR","GIT_WORK_TREE","GIT_INDEX_FILE","GIT_OBJECT_DIRECTORY","GIT_ALTERNATE_OBJECT_DIRECTORIES"]), "unexpected Git environment")
    def git(*args):
        return subprocess.check_output(["git","--no-optional-locks","-c","core.fsmonitor=false","-C",str(root),*args],env=env,stderr=subprocess.PIPE)
    parent = receipt["old_head"]
    helper.need(len(receipt["receipts"]) == 3, "exact three signed research commits")
    for name in receipt["receipts"]:
        item = helper.read(root / name)
        helper.need(item["parent"] == parent and item["signature_verified"] and item["working_bodies_and_nested_index_preserved"], "signed receipt chain")
        helper.need(git("rev-list","--parents","-n","1",item["commit"]).decode().split() == [item["commit"],parent], "actual single commit parent")
        helper.need(git("rev-parse",item["commit"]+"^{tree}").decode().strip() == item["tree"], "actual signed tree")
        git("-c","gpg.ssh.allowedSignersFile="+str(root/"artifacts/css-local-signing-20261027-v1/allowed-signers"),"verify-commit",item["commit"])
        paths = [n.decode() for n in git("diff-tree","--no-commit-id","--name-only","-r","-z",item["commit"]).split(b"\0") if n]
        helper.need(set(paths) == set(item["files"]) and all(n.startswith("artifacts/") and not n.startswith("artifacts/css-spec-lean") for n in paths), "exact artifact-only commit changes")
        parent = item["commit"]
    helper.need(parent == receipt["new_head"] and not git("diff","--name-only",receipt["old_head"],receipt["new_head"],"--",".",":(exclude)artifacts"), "exact successor with no native tree delta")
    final = helper.read(root / receipt["signing_directory"] / "FINAL-CHECK.json")
    helper.need(final["head"] == receipt["new_head"] and final["signatures_verified"] and final["runtime_epoch_synchronized"] and
                not final["candidate_accepted"] and final["current_epoch_sha256"] == policy["epoch_sha256"], "final signed preservation")
    ledger = helper.read(root / receipt["signing_directory"] / "ROADMAP-UPDATE.json")
    prior = helper.read(root / ledger["prior_authorized_ledger_update"])
    helper.need(prior["after"] == ledger["before"] and all(after["pins"].get(n) == pin for n,pin in ledger["after"].items()), "v18 to v19 ledger continuation")
    return {"old_head":receipt["old_head"],"new_head":receipt["new_head"],"signed_research_commits":3,
            "calibration_epoch_sha256":policy["calibration_epoch_sha256"],"current_epoch_sha256":policy["epoch_sha256"],
            "source_binaries_build_provenance_unchanged":True,"historical_application_metadata":metadata}
