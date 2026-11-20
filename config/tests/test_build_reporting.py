# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import mozunit
import pytest
from mozbuild.test.backend.test_build import make_path

MAKEFILE = r"""
INCLUDED_CONFIG_MK := 1
TOPLEVEL_BUILD := 1
MOZILLA_DIR := $(topsrcdir)
MACH := 1
BUILD_VERBOSE_LOG := 1
NO_BUILDSTATUS_MESSAGES :=
REBUILD_CHECK :=
relativesrcdir := src
CPPOBJS := a.o b.o
SOBJS := asm.o
AS := @:
CCC := @:
include $(topsrcdir)/config/makefiles/functions.mk
include $(topsrcdir)/config/rules.mk

capture:
	$(REPORT_BUILD) > captured

worker-%: FORCE
	@$(MAKE) relativesrcdir=$@ a.o asm.o b.o
"""


@pytest.fixture
def make(tmp_path):
    (tmp_path / "Makefile").write_text(MAKEFILE)
    env = os.environ.copy()
    for key in ("MAKEFLAGS", "GNUMAKEFLAGS", "MFLAGS"):
        env.pop(key, None)
    command = [
        make_path(),
        "--no-print-directory",
        f"topsrcdir={Path(__file__).resolve().parents[2].as_posix()}",
        f'PYTHON3="{Path(sys.executable).as_posix()}"',
    ]

    def run(*args):
        return subprocess.check_output(
            command + list(args), cwd=tmp_path, env=env, text=True
        ).splitlines()

    return run


def test_progress_is_recipe_output(make, tmp_path):
    directory = r"src'%s\t"
    assert make(f"relativesrcdir={directory}", "capture") == []
    captured = tmp_path / "captured"
    assert captured.read_text() == f"{directory}/capture\n"

    assert make("REBUILD_CHECK=1", "capture") == []
    assert captured.read_text() == "capture\n"

    assert make("-s", "MACH=", "capture") == ["src/capture"]
    assert captured.read_text() == ""


def test_dry_run(make):
    progress, start, compile_command, end = make("-kn", "a.o")
    assert progress == "src/a.o"
    assert start == "echo 'BUILDSTATUS@src OBJECT_FILE a.o'"
    assert compile_command.startswith(": ")
    assert end == "echo 'BUILDSTATUS@src END_Object a.o'"


def test_reporting_flags(make):
    assert make("BUILD_VERBOSE_LOG=", "a.o") == [
        "BUILDSTATUS@src BUILD_VERBOSE src",
        "BUILDSTATUS@src OBJECT_FILE a.o",
        "BUILDSTATUS@src END_Object a.o",
    ]
    assert make("NO_BUILDSTATUS_MESSAGES=1", "a.o") == ["src/a.o"]
    assert make("BUILD_VERBOSE_LOG=", "NO_BUILDSTATUS_MESSAGES=1", "a.o") == []


def test_mixed_parallel_reporting(make):
    workers = [f"worker-{i}" for i in range(16)]
    lines = make("-j8", *workers)
    expected = []
    for worker in workers:
        expected.append(f"{worker}/asm.o")
        for obj in ("a.o", "b.o"):
            progress = f"{worker}/{obj}"
            start = f"BUILDSTATUS@{worker} OBJECT_FILE {obj}"
            end = f"BUILDSTATUS@{worker} END_Object {obj}"
            expected.extend([progress, start, end])
            assert lines.index(progress) < lines.index(start) < lines.index(end)
    assert Counter(lines) == Counter(expected)


if __name__ == "__main__":
    mozunit.main()
