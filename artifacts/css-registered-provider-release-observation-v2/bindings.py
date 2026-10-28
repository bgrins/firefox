import os
from pathlib import Path
import stat
import subprocess


def validate_successors(root, here, policy, epoch, helper):
    record = helper.read(here / "SUCCESSION.json")
    helper.need(record["after_head"] == policy["frozen_head"], "successor target HEAD")
    helper.need(helper.sha(root / record["before_epoch"]) == record["before_epoch_sha256"], "initial checkpoint epoch")
    before = helper.read(root / record["before_epoch"])
    helper.need(before["semantic_index"]["head"] == record["before_head"], "prior observation HEAD")
    for key in ["registered_number_transition", "modified_native_paths", "installed_identities", "nested_semantic_index", "untracked_native"]:
        helper.need(before[key] == epoch[key], "preserved workspace field: " + key)
    nonartifact = lambda e: {n: p for n, p in e["pins"].items() if not n.startswith("artifacts/")}
    helper.need(nonartifact(before) == nonartifact(epoch), "unchanged harness/native/binary pins")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args], cwd=root, env=env)
    parent = record["before_head"]
    helper.need(len(record["commits"]) == 3, "three checkpoint successors")
    for item in record["commits"]:
        helper.need(helper.sha(root / item["path"]) == item["sha256"], "successor receipt bytes")
        receipt = helper.read(root / item["path"])
        helper.need(receipt["signature_verified"] and all(receipt[k] == item[k] for k in ["commit", "parent", "tree", "files"]), "receipt binding")
        commit = item["commit"]
        helper.need(item["parent"] == parent and git("rev-list", "--parents", "-n", "1", commit).decode().split() == [commit, parent], "actual successor parent")
        helper.need(git("rev-parse", commit + "^{tree}").decode().strip() == item["tree"], "actual successor tree")
        paths = git("diff", "--name-only", parent, commit).decode().splitlines()
        helper.need(sorted(paths) == sorted(item["files"]) and all(n.startswith("artifacts/") and n != "artifacts/css-spec-lean" and not n.startswith("artifacts/css-spec-lean/") for n in paths), "exact artifact-only successor")
        checked = subprocess.run(["git", "--no-optional-locks", "-c", "gpg.ssh.allowedSignersFile=" + str(root / "artifacts/css-local-signing-20261027-v1/allowed-signers"), "verify-commit", commit], cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        helper.need(checked.returncode == 0, "actual successor signature")
        parent = commit
    helper.need(parent == policy["frozen_head"], "successor chain complete")
    return [item["commit"] for item in record["commits"]]


def external_inventory(path, helper):
    helper.need(path.is_absolute() and not path.is_symlink(), "fixed external application directory")
    entries = {}
    for child in sorted(path.rglob("*")):
        info = child.lstat()
        name = str(child.relative_to(path))
        identity = [info.st_dev, info.st_ino]
        if stat.S_ISREG(info.st_mode):
            entries[name] = {"sha256": helper.sha(child), "identity": identity, "size": info.st_size}
        elif stat.S_ISLNK(info.st_mode):
            entries[name] = {"symlink": os.readlink(child), "identity": identity}
        else:
            helper.need(stat.S_ISDIR(info.st_mode), "unexpected external application entry")
    info = path.stat()
    return {"root": str(path), "root_identity": [info.st_dev, info.st_ino], "entries": entries}


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here / "EXPERIMENT.json")
    for key in ["frozen_head", "tests", "target_subtests", "held_subtests", "source_roles", "release_metadata"]:
        helper.need(policy[key] == experiment[key], "fixed release observation input: " + key)
    helper.need(policy["phase"] == "observation-1", "release observation phase")
    helper.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "current harness HEAD")
    helper.need(epoch["modified_native_paths"] == [], "accepted source working tree")
    helper.need(epoch["registered_number_transition"] == {
        "role": "candidate", "variant": "zoom-standalone-v1", "compiled": True,
        "accepted": True, "last_phase": "zoom-standalone-candidate-build-2"
    }, "preserved local workspace role, not release browser provenance")
    helper.need(policy["source_roles"] == {"candidate": {}}, "no local-source attribution to release binary")
    helper.need(policy["held_subtests"] == policy["regression_subtests"] == {}, "release results are observations")
    helper.need(len(policy["tests"]) == 2 and sum(map(len, policy["target_subtests"].values())) == 32, "exact original32 roster")
    checkpoint = root / "artifacts/css-local-signing-20261027-v25/CURRENT-EPOCH.json"
    helper.need(helper.sha(checkpoint) == policy["epoch_sha256"] and helper.read(checkpoint) == epoch, "signed accepted workspace epoch")
    successors = validate_successors(root, here, policy, epoch, helper)
    app = Path("/Applications/Firefox.app")
    inventory = helper.read(here / "EXTERNAL-APPLICATION.json")
    helper.need(external_inventory(app, helper) == inventory, "external application bytes and identities")
    helper.need(policy["application_ini"] == str(app / "Contents/Resources/application.ini"), "release metadata path")
    helper.need(policy["normal_binaries"] == [str(app / "Contents/MacOS/firefox"), str(app / "Contents/MacOS/XUL")], "release executable paths")
    metadata = helper.application_metadata(Path(policy["application_ini"]), policy["frozen_head"])
    helper.need(all(metadata[key] == value for key, value in policy["release_metadata"].items()), "actual release metadata")
    helper.need({name: helper.sha(Path(name)) for name in policy["normal_binaries"]} == policy["phase_binaries"], "release executable bytes")
    return {"phase": "observation-1", "harness_revision": policy["frozen_head"],
            "workspace_epoch_sha256": policy["epoch_sha256"],
            "external_browser": {"application": str(app), **policy["release_metadata"],
                                 "binaries": policy["phase_binaries"],
                                 "application_inventory_sha256": helper.sha(here / "EXTERNAL-APPLICATION.json")},
            "signed_artifact_successors": successors,
            "repository_sources_built_browser": False, "native_fix_acceptance": False,
            "browser_metadata_rewritten": False}
