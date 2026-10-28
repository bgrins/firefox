import os
import subprocess


def validate(root, here, policy, helper):
    receipt = helper.read(here / "HEAD-SUCCESSION.json")
    helper.need((policy["original_frozen_head"], policy["frozen_head"]) ==
                (receipt["old_head"], receipt["new_head"]), "exact signed HEAD succession")
    helper.need(helper.sha(here / "assess.py") == receipt["assessor_sha256"], "current successor assessment changed")
    for name, pin in receipt["pins"].items():
        helper.need(helper.sha(root / name) == pin, "signed succession evidence changed: " + name)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

    def git(*args):
        return subprocess.check_output(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args], env=env)

    parent = receipt["old_head"]
    for name in receipt["receipts"]:
        item = helper.read(root / name)
        helper.need(item["parent"] == parent and item["signature_verified"] and
                    item["working_bodies_and_nested_index_preserved"], "signed receipt chain")
        helper.need(git("rev-parse", item["commit"] + "^").decode().strip() == parent, "actual commit parent")
        helper.need(git("rev-parse", item["commit"] + "^{tree}").decode().strip() == item["tree"], "actual signed tree")
        files = [part.decode() for part in git("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", item["commit"]).split(b"\0") if part]
        helper.need(set(files) == set(item["files"]) and all(path.startswith("artifacts/") for path in files),
                    "succession must contain only exact research artifact paths")
        parent = item["commit"]
    helper.need(parent == receipt["new_head"], "succession final HEAD")
    helper.need(not git("diff", "--name-only", receipt["old_head"], receipt["new_head"], "--", ".", ":(exclude)artifacts"),
                "native tree changed across research succession")
    before = helper.read(root / receipt["before_epoch"])
    after = helper.read(root / receipt["after_epoch"])
    helper.need((before["semantic_index"]["head"], after["semantic_index"]["head"]) ==
                (receipt["old_head"], receipt["new_head"]), "signed epoch HEAD pair")
    helper.need(helper.sha(root / receipt["after_epoch"]) == receipt["current_epoch_sha256"], "signed final epoch digest")
    original_pins = {name: pin for name, pin in before["pins"].items() if not name.startswith("artifacts/")}
    final_pins = {name: pin for name, pin in after["pins"].items() if not name.startswith("artifacts/")}
    helper.need(original_pins == final_pins, "native source/binary pins changed during signing")
    helper.need(before["registered_number_transition"] == after["registered_number_transition"], "build provenance changed during signing")
    helper.require_compiled_transition(after, "candidate")
    helper.need(all(final_pins.get(name) == pin for name, pin in policy["source_roles"]["candidate"].items()), "signed candidate source roles")
    directory = root / receipt["signing_directory"]
    final = helper.read(directory / "FINAL-CHECK.json")
    helper.need(final["head"] == receipt["new_head"] and final["signatures_verified"] and
                final["runtime_epoch_synchronized"] and final["candidate_build_complete"] and
                final["current_epoch_sha256"] == receipt["current_epoch_sha256"], "final signed preservation receipt")
    ledger = helper.read(directory / "ROADMAP-UPDATE.json")
    previous = helper.read(root / ledger["prior_authorized_ledger_update"])
    helper.need(previous["after"] == ledger["before"], "v15 to v16 ledger chain")
    helper.need(all(after["pins"].get(name) == pin for name, pin in ledger["after"].items()), "v16 ledger epoch binding")
    return {"old_head": receipt["old_head"], "new_head": receipt["new_head"],
            "signed_commits": parent, "native_sources_and_binaries_unchanged": True,
            "candidate_binaries": {name: final_pins[name] for name in policy["normal_binaries"]}}
