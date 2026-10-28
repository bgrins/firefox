import json
import os
from pathlib import Path
import subprocess


def validate_phase(root, here, policy, epoch, h):
    phase = policy["active_phase"]
    bound = h.read(here / "PHASE-BINDINGS.json")[phase]
    h.need(isinstance(bound, dict), "phase is not bound")
    h.need(h.sha(root / bound["epoch_path"]) == bound["epoch_sha256"], "saved phase epoch")
    h.need(h.read(root / bound["epoch_path"]) == epoch, "exact saved phase epoch")
    h.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "frozen HEAD")
    for name, pin in bound["evidence_pins"].items():
        h.need(h.sha(root / name) == pin, "phase evidence: " + name)
    build = h.read(root / bound["build_result"])
    h.need(build["command_success"] is True and build["preservation_verified"] is True and
           build["error"] is None and build["owned_processes"] == {} and
           build["publication_errors"] == [], "successful preserved build")
    built = h.read(root / bound["build_epoch"])
    h.need(bound["build_result"] in bound["evidence_pins"] and
           bound["build_epoch"] in bound["evidence_pins"], "build path pins required")
    role = phase.split("-")[0]
    if role == "candidate":
        transition = built.get("page_selector_transition", {})
        h.need(transition.get("role") == "candidate" and transition.get("compiled") is True and
               transition.get("accepted") is False, "compiled page-selector candidate")
        h.need(epoch.get("page_selector_transition") == transition, "candidate transition continuity")
    else:
        transition = built["registered_number_transition"]
        h.need(transition["role"] == "candidate" and transition["compiled"] is True and
               transition["variant"] == "registered-provider-default-v5", "original successful build role")
        h.need(epoch["registered_number_transition"] == transition, "original compiled provenance")
    nonartifact = lambda pins: {n: v for n, v in pins.items() if not n.startswith("artifacts/")}
    h.need(nonartifact(built["pins"]) == nonartifact(epoch["pins"]), "build-to-phase source/binary continuity")
    h.need(built["installed_identities"] == epoch["installed_identities"], "build-to-phase owned identities")
    h.need(built["modified_native_paths"] == epoch["modified_native_paths"], "build-to-phase dirty source roles")
    h.need({n: epoch["pins"][n] for n in policy["normal_binaries"]} == bound["binary_pins"], "built browser pins")
    h.need({n: epoch["pins"][n] for n in policy["source_roles"][role]} == policy["source_roles"][role], "native phase pins")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    git = lambda *args: subprocess.check_output(["git", *args], cwd=root, env=env)
    old = built["semantic_index"]["head"]
    chain = bound["signed_artifact_succession"]
    for receipt in chain:
        commit = receipt["commit"]
        if "receipt_path" in receipt:
            path = root / receipt["receipt_path"]
            h.need(h.sha(path) == receipt["receipt_sha256"], "signed receipt digest")
            signed = h.read(path)
            h.need(signed["signature_verified"] and signed["working_bodies_and_nested_index_preserved"] and
                   signed["commit"] == commit and signed["parent"] == receipt["parent"] and
                   signed["tree"] == receipt["tree"] and set(signed["files"]) == set(receipt["paths"]),
                   "signed receipt fields")
        h.need(receipt["parent"] == old and git("rev-parse", commit + "^").decode().strip() == old,
               "signed successor parent")
        h.need(git("rev-parse", commit + "^{tree}").decode().strip() == receipt["tree"], "signed successor tree")
        paths = git("diff", "--name-only", "-z", old, commit).decode().split("\0")[:-1]
        h.need(paths == receipt["paths"] and all(n.startswith("artifacts/") for n in paths), "artifact-only successor")
        subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                        "-c", "gpg.ssh.allowedSignersFile=" + str(root / policy["allowed_signers"]),
                        "verify-commit", commit], cwd=root, env=env, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        old = commit
    h.need(old == policy["frozen_head"], "exact signed succession endpoint")
    return {"phase": phase, "epoch_sha256": bound["epoch_sha256"],
            "build_result": bound["build_result"], "build_epoch": bound["build_epoch"],
            "build_head": built["semantic_index"]["head"], "current_head": old,
            "signed_commits": [r["commit"] for r in chain]}


def original_assessment(root, here, policy, bound, h):
    if policy["active_phase"] == "original-1":
        h.need(bound.get("original") is None, "original cannot adopt another run")
        return None
    original = bound["original"]
    directory = root / original["directory"]
    h.need(directory.parent == root / "artifacts" and directory.name.startswith("css-page-selector-print-runtime-"), "original directory")
    names = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file() and not p.is_symlink() and "tools" not in p.relative_to(directory).parts}
    h.need(names == set(original["files"]), "exact original runtime regular-file inventory")
    for name, pin in original["files"].items():
        h.need(h.sha(directory / name) == pin, "original runtime file: " + name)
    h.need((directory / "tests/tools").is_symlink() and
           (directory / "tests/tools").resolve() == root / "testing/web-platform/tests/tools", "original tools link")
    predecessor = root / original["capsule"]
    h.authenticate(predecessor, original["capsule_sha256"])
    for name in ("EXPERIMENT.json", "SOURCE-PINS.json", "SUBSET-MANIFEST.json", "assess.py", "pixels.py"):
        h.need(h.sha(predecessor / name) == h.sha(here / name), "same experiment/assessment: " + name)
    saved = h.read(directory / "ASSESSMENT.json")
    result = h.read(directory / "RESULT.json")
    cleanup = h.read(directory / "CLEANUP.json")
    h.need(result["observation_gate_passed"] is True and saved["complete"] is True and
           saved["execution_preserved"] is True and saved["phase"] == "original-1", "original complete and preserved")
    h.need(result["execution_error"] is None and result["preservation_error"] is None and
           cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "original lifecycle")
    h.need(h.read(directory / "PRE.json") == h.read(directory / "POST.json"), "original pre/post")
    old_epoch = h.read(directory / "EPOCH.json")
    current = h.read(root / bound["epoch_path"])
    allowed = set(policy["source_roles"]["candidate"]) | set(bound["build_binary_paths"])
    strip = lambda e: {n: v for n, v in e["pins"].items() if not n.startswith("artifacts/") and n not in allowed}
    h.need(strip(old_epoch) == strip(current), "unrelated source preservation across phases")
    h.need(old_epoch["semantic_index"]["head"] == current["semantic_index"]["head"] == policy["frozen_head"], "paired frozen HEAD")
    h.need(saved["native_sources"] == policy["source_roles"]["original"], "original source roles")
    parser = h.load("page_original_assessor", here / "assess.py")
    events = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
    replayed = parser.assess(events, result["exit"], policy, None, original=None,
                             run_binding=h.read(directory / "APPLICATION-METADATA.json"))
    h.need(all(saved.get(key) == value for key, value in replayed.items()), "original raw assessment replay")
    return saved
