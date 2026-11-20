# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import errno
import hashlib
import json
import os
import subprocess
from pathlib import Path

import mozunit
import pytest

from mozbuild import buildbench as bench


@pytest.fixture
def checkout(tmp_path, request):
    source = tmp_path / "checkout"
    source.mkdir()

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=source)

    git("init", "-q")
    target = source / getattr(request, "param", "target")
    target.write_bytes(b"before\n")
    git("add", target.name)
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.org",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-qm",
        "original",
    )
    target.write_bytes(b"after\n")
    patch = tmp_path / "edit.patch"
    patch.write_bytes(git("diff", "--binary"))
    git("restore", target.name)
    return source, target, patch


@pytest.fixture
def run_workload(tmp_path, monkeypatch):
    monkeypatch.setattr(
        bench, "configured_build", lambda source, objdir, mozconfig_path: {}
    )
    output = tmp_path / "output"

    def run(source, measure, workload="patch", patch=None):
        monkeypatch.setattr(bench, "measure", measure)
        return bench.run(
            source, tmp_path / "obj", tmp_path, workload, 1, 0, {}, output, patch
        )

    return run


@pytest.mark.parametrize("when", ["setup", "prepare", "1-following-no-change"])
def test_deleted_preimage(checkout, tmp_path, run_workload, when):
    source, target, patch = checkout
    if when == "setup":
        target.unlink()

    def measure(source, output, label, jobs, *, objdir, mozconfig_path):
        assert when != "setup"
        if label == when:
            target.unlink()
        return {"wall_s": 1}

    with pytest.raises(RuntimeError, match="Missing patch preimage"):
        run_workload(source, measure, patch=patch)
    assert not target.exists()
    needs_recovery = when == "1-following-no-change"
    assert (tmp_path / "buildbench.lock").exists() == needs_recovery
    assert (tmp_path / "output" / "patch.index").exists() == needs_recovery


@pytest.mark.parametrize("checkout", ["CLOBBER"], indirect=True)
def test_refuse_clobber_patch_before_mutation(checkout, run_workload):
    source, target, patch = checkout
    original_time = target.stat().st_mtime_ns
    with pytest.raises(ValueError, match="touches CLOBBER"):
        run_workload(
            source, lambda *args, **kwargs: pytest.fail("unexpected build"), patch=patch
        )
    assert target.read_bytes() == b"before\n"
    assert target.stat().st_mtime_ns == original_time


def test_saved_patch_files_are_artifacts(checkout, run_workload):
    source, target, patch = checkout
    digest = hashlib.sha256(patch.read_bytes()).hexdigest()

    def measure(source, output, label, jobs, *, objdir, mozconfig_path):
        if label == "prepare":
            for name in ("workload.patch", "restore.patch"):
                (output / name).write_bytes(b"unusable patch\n")
        if label in ("1-edit", "1-following-no-change"):
            assert target.read_bytes() == b"after\n"
        return {"wall_s": 1}

    output = run_workload(source, measure, patch=patch)
    assert target.read_bytes() == b"before\n"
    assert json.loads((output / "results.json").read_bytes())["patch_sha256"] == digest


@pytest.mark.parametrize("workload", ["image-alt-text", "patch"])
@pytest.mark.parametrize("build_fails", [False, True])
def test_summary_enospc_during_rollback(
    checkout, tmp_path, run_workload, monkeypatch, workload, build_fails
):
    source, target, patch = checkout
    if workload != "patch":
        relative, before, _ = bench.EDITS[workload]
        target = source / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(before)
        patch = None
    original = target.read_bytes()
    output = tmp_path / "output"
    failed_writes = []
    write_text = Path.write_text

    def fail_summary(path, data, *args, **kwargs):
        if path == output / "results.tmp":
            record = json.loads(data)
            if failed_writes or record.get("recovery", {}).get("phase") == "restoring":
                failed_writes.append(record)
                raise OSError(errno.ENOSPC, "No space left on device")
        return write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_summary)
    build_error = RuntimeError("edit build exited 11")

    def measure(source, output, label, jobs, **kwargs):
        if label == "1-edit":
            assert target.read_bytes() != original
            if build_fails:
                raise build_error
        return {"wall_s": 1}

    with pytest.raises(RuntimeError if build_fails else OSError) as exc:
        run_workload(source, measure, workload, patch)
    if build_fails:
        assert exc.value is build_error
    else:
        assert exc.value.errno == errno.ENOSPC
    assert failed_writes[-1]["status"] == "incomplete"
    assert failed_writes[-1]["error"] == str(exc.value)
    assert target.read_bytes() == original
    assert not (tmp_path / "buildbench.lock").exists()
    assert not (output / "patch.index").exists()


@pytest.mark.parametrize("phase", ["applying", "restoring"])
def test_interrupted_git_write(checkout, tmp_path, run_workload, monkeypatch, phase):
    source, target, patch = checkout
    output = tmp_path / "output"
    original_run = subprocess.run

    def interrupt(command, **kwargs):
        result = original_run(command, **kwargs)
        if command[-1] == "apply":
            record = json.loads((output / "results.json").read_bytes())
            if record["recovery"]["phase"] == phase:
                raise KeyboardInterrupt
        return result

    monkeypatch.setattr(subprocess, "run", interrupt)
    with pytest.raises(KeyboardInterrupt):
        run_workload(source, lambda *args, **kwargs: {"wall_s": 1}, patch=patch)
    assert target.read_bytes() == (b"after\n" if phase == "applying" else b"before\n")
    assert (tmp_path / "buildbench.lock").is_file()
    assert (output / "patch.index").is_file()
    record = json.loads((output / "results.json").read_bytes())
    assert record["status"] == "incomplete"
    assert record["recovery"]["phase"] == phase


@pytest.mark.parametrize("phase", ["applying", "restoring"])
@pytest.mark.parametrize("when", ["before-rename", "after-rename"])
def test_editor_save_at_fixture_replacement(
    tmp_path, run_workload, monkeypatch, phase, when
):
    workload = "image-alt-text"
    relative, before, _ = bench.EDITS[workload]
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(before)
    output = tmp_path / "output"
    original_rename = Path.rename

    def race(self, destination):
        if self == path:
            record = json.loads((output / "results.json").read_bytes())
            if record["recovery"]["phase"] == phase:
                if when == "before-rename":
                    path.write_bytes(b"editor save")
                displaced = original_rename(self, destination)
                if when == "after-rename":
                    path.write_bytes(b"editor save")
                return displaced
        return original_rename(self, destination)

    monkeypatch.setattr(Path, "rename", race)
    with pytest.raises((OSError, RuntimeError)):
        run_workload(tmp_path, lambda *args, **kwargs: {"wall_s": 1}, workload)
    assert path.read_bytes() == b"editor save"
    record = json.loads((output / "results.json").read_bytes())
    assert record["recovery"]["phase"] == phase
    assert Path(record["recovery"]["directory"]).is_dir()
    assert (output / f"{path.name}.original").read_bytes() == before
    assert (tmp_path / "buildbench.lock").is_file()


def test_restore_refreshes_fixture_mtime(tmp_path):
    workload = "image-alt-text"
    relative, before, _ = bench.EDITS[workload]
    source = tmp_path / "checkout"
    path = source / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(before)
    path.chmod(0o640)
    os.utime(path, (1, 1))
    old_mtime = path.stat().st_mtime_ns
    output = tmp_path / "output"
    output.mkdir()
    with bench.source_edit(source, output, workload):
        assert list(path.parent.iterdir()) == [path]
    assert path.read_bytes() == before
    assert path.stat().st_mtime_ns > old_mtime
    assert list(output.iterdir()) == [output / f"{path.name}.original"]


if __name__ == "__main__":
    mozunit.main()
