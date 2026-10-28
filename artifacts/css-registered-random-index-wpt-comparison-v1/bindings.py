import json


def validate_phase(root, here, policy, epoch, h):
    h.need(h.sha(root / policy["build_epoch"]) == policy["build_epoch_sha256"] == policy["epoch_sha256"], "saved build epoch")
    h.need(h.read(root / policy["build_epoch"]) == epoch, "actual build and observation epochs differ")
    h.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "frozen HEAD")
    marker = policy["build_marker"]
    h.need(marker["key"] == "random_counter_transition" and marker["value"]["accepted"] is False, "unaccepted random comparison marker")
    h.need(epoch.get(marker["key"]) == marker["value"] and marker["value"]["compiled"] is True,
           "exact successful compiled phase marker")
    role = policy["phase"].split("-", 1)[0]
    h.need(marker["value"]["role"] == role and marker["value"]["last_phase"] == role + "-build-1", "compiled role/label")
    h.need({policy["build_epoch"], policy["build_result"], policy["inner_build_result"]} <= set(policy["build_evidence"]), "mandatory build evidence pins")
    for name, digest in policy["build_evidence"].items():
        h.need(h.sha(root / name) == digest, "actual build evidence: " + name)
    result = h.read(root / policy["build_result"])
    h.need(h.sha(root / policy["build_result"]) == policy["build_result_sha256"], "build result hash")
    h.need(result["command_success"] is True and result["preservation_verified"] is True and
           not result["owned_processes"] and result["error"] is None and not result["publication_errors"] and result["source_role"] == role,
           "successful preserved build")
    inner = h.read(root / policy["inner_build_result"])
    h.need(inner["exit"] == 0 and inner["error"] is None and inner["stop_reason"] is None and
           not inner["cleanup_errors"] and inner["owned_group_absent"] is True, "inner build exit/cleanup")
    for name, digest in dict(policy["source_roles"][role], **policy["phase_binaries"]).items():
        h.need(epoch["pins"].get(name) == digest, "compiled source/binary: " + name)
    h.need(set(policy["normal_binaries"]) == set(policy["phase_binaries"]), "binary roster")
    h.need(role == "original" or bool(policy["original_binding"]), "candidate needs exact original")
    return {"role": role, "build_epoch_sha256": policy["build_epoch_sha256"],
            "build_result_sha256": policy["build_result_sha256"], "marker": marker,
            "source_roles": policy["source_roles"][role], "binaries": policy["phase_binaries"]}


def validate_original(root, here, policy, h):
    binding = policy["original_binding"]
    if binding is None:
        h.need(policy["phase"].startswith("original-"), "unbound original")
        return None
    h.need(policy["phase"].startswith("candidate-"), "original run cannot adopt another original")
    old = root / binding["capsule"]
    h.authenticate(old, binding["capsule_sha256"])
    for name in ("EXPERIMENT.json", "SOURCE-PINS.json", "SUBSET-MANIFEST.json", "assess.py"):
        h.need((here / name).read_bytes() == (old / name).read_bytes(), "changed original experiment: " + name)
    original_policy = h.read(old / "POLICY.json")
    for name in ("tests", "target_subtests", "regression_subtests", "held_subtests", "frozen_head",
                 "source_roles", "live_oracle_sources", "unchanged_native_sources", "rebuilt_binaries"):
        h.need(original_policy[name] == policy[name], "changed experiment policy: " + name)
    runtime = root / binding["runtime"]
    actual = {str(p.relative_to(runtime)): h.sha(p) for p in runtime.rglob("*")
              if p.is_file() and not p.is_symlink() and "tools" not in p.relative_to(runtime).parts}
    h.need(actual == binding["files"], "original exact file inventory")
    links = {str(p.relative_to(runtime)): str(p.readlink()) for p in runtime.rglob("*") if p.is_symlink()}
    h.need(links == binding["symlinks"], "original exact symlinks")
    result, saved = h.read(runtime / "RESULT.json"), h.read(runtime / "ASSESSMENT.json")
    h.need(result["observation_gate_passed"] is True and result["execution_error"] is None and
           result["preservation_error"] is None and saved["complete"] is True and
           saved["execution_preserved"] is True, "original complete preserved")
    h.need(saved["capsule_manifest_sha256"] == binding["capsule_sha256"] and
           saved["epoch_sha256"] == original_policy["epoch_sha256"] and
           saved["native_sources"] == policy["source_roles"]["original"], "original provenance")
    h.need(h.read(runtime / "PRE.json") == h.read(runtime / "POST.json"), "original state preservation")
    metadata = h.read(runtime / "APPLICATION-METADATA.json")
    h.need(metadata == h.read(runtime / "APPLICATION-METADATA-POST.json"), "original application metadata")
    cleanup = h.read(runtime / "CLEANUP.json")
    h.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "original cleanup")
    h.need(h.sha(runtime / "EPOCH.json") == original_policy["epoch_sha256"], "original epoch")
    original_epoch = h.read(runtime / "EPOCH.json")
    current_epoch = h.read(root / policy["build_epoch"])
    changed = {name for name, digest in policy["source_roles"]["original"].items()
               if policy["source_roles"]["candidate"].get(name) != digest}
    allowed = changed | set(policy["rebuilt_binaries"])
    stable = lambda e: {name: digest for name, digest in e["pins"].items()
                        if not name.startswith("artifacts/") and name not in allowed}
    h.need(stable(original_epoch) == stable(current_epoch), "unrelated compiled/source inputs changed")
    parser = h.load("random_original_assessor", here / "assess.py")
    checks = h.load("random_original_checks", root / policy["helpers"]["checks"])
    events = [json.loads(line) for line in (runtime / "raw.jsonl").read_text().splitlines()]
    replayed = parser.assess(events, result["exit"], original_policy, checks, run_binding=metadata)
    replayed = json.loads(json.dumps(replayed))
    h.need(all(saved.get(k) == v for k, v in replayed.items()), "original raw assessment replay")
    h.need(saved["run_binding"]["revision"] == policy["frozen_head"], "same original HEAD")
    return saved
