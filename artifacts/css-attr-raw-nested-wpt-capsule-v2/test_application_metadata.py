import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load("application_metadata_runner", HERE / "run.py")
policy = json.loads((HERE / "POLICY.json").read_text())
helper = load("application_metadata_preservation", ROOT / policy["helpers"]["preservation"])
accepted, rejected = [], []


def rejects(label, operation):
    try:
        operation()
    except (RuntimeError, FileNotFoundError, AssertionError):
        rejected.append(label)
    else:
        raise AssertionError(label)


with tempfile.TemporaryDirectory(prefix="css-app-metadata-controls-", dir="/private/tmp") as directory:
    scratch = Path(directory)
    path = scratch / "application.ini"
    data = b"[App]\nBuildID=20261027145735\n"
    digest = hashlib.sha256(data).hexdigest()
    path.write_bytes(data)
    regular = runner.application_metadata(path, "a" * 40)
    assert regular["symlink_target"] is None and regular["sha256"] == digest
    assert regular["entry_type"] == stat.S_IFREG
    assert runner.resource_fingerprint(helper, scratch, "application.ini", "application.ini") == digest
    accepted.append("regular application.ini")
    path.unlink()
    target = scratch / "target.ini"
    target.write_bytes(data)
    path.symlink_to("target.ini")
    before = runner.application_metadata(path, "a" * 40)
    assert before["resolved"] == str(target) and before["symlink_target"] == "target.ini"
    assert before["identity"] == [target.stat().st_dev, target.stat().st_ino]
    assert before["entry_identity"] == [path.lstat().st_dev, path.lstat().st_ino]
    assert before["entry_type"] == stat.S_IFLNK
    assert before["browser_build_id"] == "20261027145735"
    assert runner.resource_fingerprint(helper, scratch, "application.ini", "application.ini") == digest
    assert runner.application_metadata(path, "a" * 40) == before
    accepted.append("known application.ini symlink with regular target")

    other = scratch / "ordinary.ini"
    other.write_bytes(data)
    assert runner.resource_fingerprint(helper, scratch, "ordinary.ini", "application.ini") == digest
    accepted.append("unrelated regular resource retains generic fingerprint")
    other.unlink()
    other.symlink_to("target.ini")
    rejects("unrelated resource symlink", lambda: runner.resource_fingerprint(helper, scratch, "ordinary.ini", "application.ini"))

    replacement = scratch / "replacement-link"
    replacement.symlink_to("target.ini")
    os.replace(replacement, path)
    assert runner.resource_fingerprint(helper, scratch, "application.ini", "application.ini") == digest
    rejects("same-target symlink replacement", lambda: runner.need(runner.application_metadata(path, "a" * 40) == before, "metadata changed"))
    before = runner.application_metadata(path, "a" * 40)

    replacement.write_bytes(data)
    os.replace(replacement, target)
    assert runner.resource_fingerprint(helper, scratch, "application.ini", "application.ini") == digest
    rejects("same-bytes target replacement", lambda: runner.need(runner.application_metadata(path, "a" * 40) == before, "metadata changed"))
    before = runner.application_metadata(path, "a" * 40)

    alternate = scratch / "alternate.ini"
    alternate.write_bytes(data)
    replacement.symlink_to("alternate.ini")
    os.replace(replacement, path)
    assert runner.resource_fingerprint(helper, scratch, "application.ini", "application.ini") == digest
    rejects("same-bytes symlink retarget", lambda: runner.need(runner.application_metadata(path, "a" * 40) == before, "metadata changed"))
    before = runner.application_metadata(path, "a" * 40)
    alternate.write_bytes(b"[App]\nBuildID=20261028120000\n")
    rejects("target bytes and BuildID change", lambda: runner.need(runner.application_metadata(path, "a" * 40) == before, "metadata changed"))

    path.unlink()
    path.symlink_to("absent.ini")
    rejects("broken application symlink", lambda: runner.application_metadata(path, "a" * 40))
    path.unlink()
    path.symlink_to(scratch, target_is_directory=True)
    rejects("non-regular application target", lambda: runner.resource_fingerprint(helper, scratch, "application.ini", "application.ini"))
    rejects("non-regular metadata target", lambda: runner.application_metadata(path, "a" * 40))

assert not scratch.exists()
print(json.dumps({"accepted_controls": accepted, "rejected_controls": rejected,
                  "owned_scratch_removed": True, "browser_executed": False,
                  "mach_executed": False}, indent=2))
