# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mozunit
import pytest
from mach.command_util import load_commands_from_file
from mach.registrar import MachRegistrar
from mozversioncontrol import get_repository_object

from mozbuild import buildbench as bench


@pytest.fixture(scope="module")
def command():
    registrar = MachRegistrar()
    for category in ("build", "post-build"):
        registrar.register_category(category, category, "")
    with patch("mach.decorators.Registrar", registrar):
        load_commands_from_file(Path(bench.__file__).with_name("build_commands.py"))
    return registrar.command_handlers["buildbench"]


@pytest.mark.parametrize("args", [[], ["--list"]])
def test_list_workloads(command, args, capsys):
    assert command.func(None, **vars(command.parser.parse_args(args))) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"{name:16} {description}" for name, description in bench.WORKLOADS.items()
    ]


@pytest.mark.parametrize(
    "args",
    [
        ["--list", "no-change"],
        ["no-change", "--list"],
        ["--patch", "edit.patch", "no-change"],
        ["--list", "--patch", "edit.patch"],
    ],
)
def test_conflicting_selectors(command, args):
    with pytest.raises(SystemExit) as exc:
        command.parser.parse_args(args)
    assert exc.value.code == 2


def test_patch_arguments(command):
    args = command.parser.parse_args([
        "--patch",
        "edit.patch",
        "--repeat",
        "3",
        "-j",
        "4",
    ])
    assert (args.patch, args.workload, args.repeat, args.jobs) == (
        "edit.patch",
        None,
        3,
        4,
    )


@pytest.mark.parametrize("vcs", ["git", "hg"])
def test_tracked_changes(command, tmp_path, monkeypatch, vcs):
    if not shutil.which(vcs):
        pytest.skip(f"{vcs} is unavailable")
    monkeypatch.setenv("HGRCPATH", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)

    def run(*args):
        subprocess.run([vcs, *args], cwd=tmp_path, check=True)

    run("init")
    for name in ("old name", "missing", "edited"):
        (tmp_path / name).write_bytes(b"original\n")
    run("add", "old name", "missing", "edited")
    if vcs == "git":
        run(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.org",
            "commit",
            "-m",
            "base",
        )
    else:
        run("commit", "-u", "Test", "-m", "base")

    run("mv", "old name", "new name")
    (tmp_path / "missing").unlink()
    (tmp_path / "edited").write_bytes(b"changed\n")
    if vcs == "git":
        run("add", "edited")
        (tmp_path / "edited").write_bytes(b"original\n")
    (tmp_path / "untracked").touch()

    context = SimpleNamespace(
        topsrcdir=tmp_path,
        topobjdir=tmp_path / "obj",
        mozconfig={"path": None},
        repository=get_repository_object(tmp_path),
    )
    args = command.parser.parse_args(["no-change"])
    with patch("mach.util.get_state_dir", return_value=tmp_path), patch.object(
        bench, "run"
    ) as measure:
        assert command.func(context, **vars(args)) == 0
    assert measure.call_args.args[3:6] == ("no-change", 1, 0)
    assert measure.call_args.args[6]["tracked_changes"] == [
        "edited",
        "missing",
        "new name",
        "old name",
    ]


if __name__ == "__main__":
    mozunit.main()
