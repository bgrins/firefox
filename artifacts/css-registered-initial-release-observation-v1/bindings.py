import os
from pathlib import Path
import stat


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
        helper.need(policy[key] == experiment[key], "fixed release input: " + key)
    helper.need(policy["phase"] == "observation-1", "release observation phase")
    helper.need(policy["source_roles"] == {"candidate": {}}, "no local-source attribution to release browser")
    helper.need(policy["held_subtests"] == policy["regression_subtests"] == {}, "registration results are observations")
    helper.need(len(policy["tests"]) == 2 and sum(map(len, policy["target_subtests"].values())) == 68, "exact original21 plus selected47")
    fixture = root / policy["fixture"]
    helper.authenticate(fixture, policy["fixture_sha256"])
    helper.need(helper.read(fixture / "TARGET-SUBTESTS.json") == policy["target_subtests"], "exact sealed fixture names")
    for test in policy["tests"]:
        capture = here / "capture/testing/web-platform/tests" / test.lstrip("/")
        helper.need(helper.sha(capture) == helper.sha(fixture / Path(test).name), "exact sealed fixture bytes")
    staged = root / policy["staged_capsule"]
    helper.authenticate(staged, policy["staged_capsule_sha256"])
    helper.need(policy["helpers"]["epoch"] == str((staged / "epoch.py").relative_to(root)), "reviewed staged preservation guard")
    helper.need(helper.sha(staged / "OBSERVATION-EPOCH.json") == policy["epoch_sha256"], "actual staged observation epoch bytes")
    helper.need(helper.read(staged / "OBSERVATION-EPOCH.json") == epoch, "exact preserved workspace state")
    helper.need(epoch["semantic_index"]["head"] == policy["frozen_head"], "actual harness HEAD")
    staging = helper.read(staged / "STAGING.json")
    helper.need(len(staging["staged_files"]) == 36 and staging["staged_working"] == epoch["staged_working"], "exact pending36 signing bodies")
    helper.need(helper.sha(root / staging["staged_patch"]) == staging["staged_patch_sha256"], "preserved signing patch bytes")
    for name, pin in policy["workspace_controls"].items():
        helper.need(helper.sha(root / name) == pin, "workspace control unchanged: " + name)
    app = Path("/Applications/Firefox.app")
    inventory = helper.read(here / "EXTERNAL-APPLICATION.json")
    helper.need(len(inventory["entries"]) == 110 and external_inventory(app, helper) == inventory, "external application bytes and identities")
    helper.need(policy["application_ini"] == str(app / "Contents/Resources/application.ini"), "release metadata path")
    helper.need(policy["normal_binaries"] == [str(app / "Contents/MacOS/firefox"), str(app / "Contents/MacOS/XUL")], "release executable paths")
    metadata = helper.application_metadata(Path(policy["application_ini"]), policy["frozen_head"])
    helper.need(all(metadata[key] == value for key, value in policy["release_metadata"].items()), "actual release metadata")
    helper.need({name: helper.sha(Path(name)) for name in policy["normal_binaries"]} == policy["phase_binaries"], "release executable bytes")
    return {"phase": policy["phase"], "harness_revision": policy["frozen_head"],
            "workspace_epoch_sha256": policy["epoch_sha256"],
            "preserved_staged_files": 36, "staged_patch_sha256": staging["staged_patch_sha256"],
            "external_browser": {"application": str(app), **policy["release_metadata"],
                                 "binaries": policy["phase_binaries"],
                                 "application_inventory_sha256": helper.sha(here / "EXTERNAL-APPLICATION.json")},
            "repository_sources_built_browser": False, "native_fix_acceptance": False,
            "browser_metadata_rewritten": False}
