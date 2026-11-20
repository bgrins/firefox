# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import gzip
import json
import subprocess
from unittest.mock import patch

import mozunit
import pytest

from mozbuild import buildbench as bench


def write_configuration(source, obj, mozconfig=None):
    config = dict(
        MOZ_BUILD_APP="browser",
        CC=["clang"],
        CXX=["clang++"],
        HOST_CC=["clang"],
        HOST_CXX=["clang++"],
        RUSTC="rustc",
    )
    roots = {"topsrcdir": str(source), "topobjdir": str(obj)}
    (obj / "config.status.json").write_text(json.dumps({**roots, "substs": config}))
    (obj / "mozinfo.json").write_text(json.dumps({**roots, "mozconfig": mozconfig}))


@pytest.fixture
def obj(tmp_path):
    obj = tmp_path / "obj"
    obj.mkdir()
    write_configuration(tmp_path, obj)
    return obj


@pytest.mark.parametrize("matches", [0, 2])
def test_inapplicable_edit_skips_preparation(tmp_path, obj, matches):
    name = "image-alt-text"
    path, before, _ = bench.EDITS[name]
    source = tmp_path / path
    source.parent.mkdir(parents=True)
    original = before * matches
    source.write_bytes(original)
    with patch.object(bench, "measure", return_value={"wall_s": 1}) as measure:
        with pytest.raises(ValueError, match="Expected one image-alt-text fixture"):
            bench.run(tmp_path, obj, tmp_path, name, 1, 4, {})
        measure.assert_not_called()
    assert source.read_bytes() == original
    assert not (tmp_path / "buildbench.lock").exists()


@pytest.mark.parametrize("workload", bench.EDITS)
def test_edit_lifecycle(tmp_path, obj, workload):
    path, before, after = bench.EDITS[workload]
    source = tmp_path / path
    source.parent.mkdir(parents=True)
    source.write_bytes(before)
    seen = []

    def capture(source_dir, output, label, jobs, **kwargs):
        seen.append((label, source.read_bytes()))
        return {"wall_s": 1}

    with patch.object(bench, "measure", capture):
        out = bench.run(tmp_path, obj, tmp_path, workload, 2, 4, {})
    assert [data for _, data in seen] == [before] + [
        after,
        after,
        before,
    ] * 2
    record = json.loads((out / "results.json").read_text())
    assert record["status"] == "complete"
    assert "active_sample" not in record
    assert "patch_setup" not in record
    assert record["edited_path"] == path.as_posix()
    assert [r["trial"] for r in record["samples"]] == [0, 1, 1, 1, 2, 2, 2]
    assert source.read_bytes() == before


@pytest.mark.parametrize("workload", bench.EDITS)
def test_failure_restores_source(tmp_path, workload):
    relative_path, before, _ = bench.EDITS[workload]
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True)
    path.write_bytes(before)
    with pytest.raises(KeyboardInterrupt), bench.source_edit(
        tmp_path, tmp_path, workload
    ):
        raise KeyboardInterrupt
    assert path.read_bytes() == before
    with pytest.raises(RuntimeError, match="Original saved"), bench.source_edit(
        tmp_path, tmp_path, workload
    ):
        path.write_bytes(b"concurrent edit")
    assert path.read_bytes() == b"concurrent edit"
    assert (tmp_path / f"{path.name}.original").read_bytes() == before


def test_interrupted_sample(tmp_path, obj, monkeypatch):
    workload = "image-alt-text"
    relative, before, _ = bench.EDITS[workload]
    fixture = tmp_path / relative
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(before)
    output = tmp_path / "results"

    def measure(source, output, label, jobs, **kwargs):
        if label == "prepare":
            return {"wall_s": 1}
        summary = json.loads((output / "results.json").read_text())
        assert summary["status"] == "running"
        assert summary["active_sample"] == {
            "phase": "edit",
            "trial": 1,
            "log": "1-edit.log",
        }
        assert [sample["phase"] for sample in summary["samples"]] == ["prepare"]
        raise KeyboardInterrupt

    monkeypatch.setattr(bench, "measure", measure)
    with pytest.raises(KeyboardInterrupt):
        bench.run(tmp_path, obj, tmp_path, workload, 1, 4, {}, output)
    summary = json.loads((output / "results.json").read_text())
    assert summary["status"] == "incomplete"
    assert summary["active_sample"]["phase"] == "edit"
    assert [sample["phase"] for sample in summary["samples"]] == ["prepare"]
    assert fixture.read_bytes() == before


def test_selector_edit_crlf(tmp_path):
    workload = "selector-invalidation"
    relative_path, before, after = bench.EDITS[workload]
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True)
    original = before.replace(b"\n", b"\r\n") + b"\r\n"
    path.write_bytes(original)
    with bench.source_edit(tmp_path, tmp_path, workload):
        assert path.read_bytes() == after + b"\r\n"
    assert path.read_bytes() == original


@pytest.mark.parametrize("collect_usage", [True, False])
def test_no_change_artifacts(tmp_path, obj, monkeypatch, collect_usage):
    if not collect_usage:
        monkeypatch.setattr(bench, "resource", None)
    monkeypatch.delenv("RUSTC_WRAPPER", raising=False)
    monkeypatch.delenv("RUSTC_WORKSPACE_WRAPPER", raising=False)
    monkeypatch.setenv("CARGO_INCREMENTAL", "1")
    mozconfig = tmp_path / "configs" / "selected"
    mozconfig.parent.mkdir()
    mozconfig.touch()
    write_configuration(tmp_path, obj, str(mozconfig))
    monkeypatch.setenv("MOZCONFIG", "configs/selected")
    monkeypatch.setenv("MOZ_OBJDIR", str(tmp_path / "other"))
    monkeypatch.setenv("MOZ_RESOURCE_MONITOR_FORWARD", str(tmp_path / "forward"))
    machine = {
        "CPUName": "Test processor",
        "logicalCPUs": 8,
        "physicalCPUs": 4,
        "abi": "aarch64-unknown-linux-gnu",
    }
    profile = {
        "meta": {**machine, "oscpu": None, "interval": 100},
        "threads": [
            {
                "stringArray": ["Object", "xpt", "file_generate"],
                "markers": {"name": [0, 0, 1, 2, 2], "endTime": [1, None, 2, 3, None]},
            }
        ],
    }
    (tmp_path / "mach").write_text(
        "import os\n"
        "assert os.environ['RUSTC_WRAPPER'] == ''\n"
        "assert os.environ['RUSTC_WORKSPACE_WRAPPER'] == ''\n"
        "assert os.environ['CARGO_INCREMENTAL'] == '1'\n"
        "from pathlib import Path\n"
        f"assert Path.cwd() == Path({str(obj)!r}).resolve()\n"
        f"assert Path(os.environ['MOZCONFIG']) == Path({str(mozconfig)!r})\n"
        "assert Path(os.environ['MOZ_OBJDIR']) == Path.cwd()\n"
        "assert 'MOZ_RESOURCE_MONITOR_FORWARD' not in os.environ\n"
        "p = Path.cwd() / 'profile.json'\n"
        f"p.write_text({json.dumps(profile)!r})\n"
        f"print({bench.PROFILE_PREFIX!r} + p.name)\n"
    )
    out = bench.run(
        tmp_path, obj, tmp_path, "no-change", 2, 0, {}, mozconfig={"path": mozconfig}
    )
    record = json.loads((out / "results.json").read_text())
    assert [r["phase"] for r in record["samples"]] == [
        "prepare",
        "no-change",
        "no-change",
    ]
    for row in record["samples"]:
        assert row["profile_machine"] == machine
        assert row["completed_profile_markers"] == {
            "Object": 1,
            "xpt": 1,
            "file_generate": 1,
        }
        usage = row["child_usage"]
        if bench.resource is None:
            assert usage == {}
        else:
            assert usage["user_s"] + usage["system_s"] > 0
            assert usage["major_page_faults"] >= 0
            assert usage["input_blocks"] >= 0
            assert usage["output_blocks"] >= 0
        assert (out / row["log"]).is_file()
        with gzip.open(out / row["profile"], "rt") as stream:
            assert json.load(stream) == profile


def test_profile_without_machine_details(tmp_path):
    profile = tmp_path / "build-profile.json.gz"
    with gzip.open(profile, "wt") as stream:
        json.dump({"threads": []}, stream)
    assert bench.profile_summary(profile) == {
        "completed_profile_markers": {},
        "profile_machine": {},
    }


def test_explicit_output(tmp_path, obj):
    output = tmp_path / "comparison" / "baseline"
    with patch.object(bench, "measure", return_value={"wall_s": 1}) as measure:
        bench.run(tmp_path, obj, tmp_path, "no-change", 1, 4, {}, output)
        record = (output / "results.json").read_bytes()
        assert json.loads(record)["status"] == "complete"
        measure.reset_mock()
        with pytest.raises(FileExistsError):
            bench.run(tmp_path, obj, tmp_path, "no-change", 1, 4, {}, output)
        measure.assert_not_called()
        assert (output / "results.json").read_bytes() == record


@pytest.mark.parametrize("outcome", ["complete", "conflict", "inapplicable"])
@pytest.mark.parametrize("index_version", [None, "2"])
def test_patch_workload(tmp_path, obj, outcome, index_version, monkeypatch):
    source = tmp_path / "checkout"
    source.mkdir()
    write_configuration(source, obj)

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=source)

    git("init", "-q")
    old = source / "old [1]"
    copied = source / "copied"
    copy_source = source / "copy-source"
    copy_source.write_bytes(b"copy this blob\n")
    edited = source / "edited"
    added = source / "added"
    (source / ".gitattributes").write_text("untouched filter=unexpected\n")
    (source / "untouched").write_text("keep this file out of patch preparation")
    old.write_bytes(b"delete me\n")
    edited.write_bytes(b"original\n")
    git("add", ".")
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
    copied.write_bytes(copy_source.read_bytes())
    old.unlink()
    added.write_bytes(b"new\n")
    edited.write_bytes(b"replacement\n")
    git("add", "-A")
    patch_file = tmp_path / "change.patch"
    patch_file.write_bytes(git("diff", "--cached", "--binary", "--find-copies-harder"))
    assert b"copy from copy-source" in patch_file.read_bytes()
    git("restore", "--source=HEAD", "--staged", "--worktree", ".")
    unrelated = source / "unrelated"
    unrelated.write_text("preserve staged content")
    git("add", "unrelated")
    git("config", "filter.unexpected.clean", "false")
    git("config", "filter.unexpected.required", "true")
    index = (source / ".git/index").read_bytes()
    labels = []

    def measure(source, output, label, jobs, **kwargs):
        labels.append(label)
        if label.endswith(("-edit", "-following-no-change")):
            assert copied.read_bytes() == copy_source.read_bytes()
            assert added.exists() and not old.exists()
            assert edited.read_bytes() == b"replacement\n"
            if outcome == "conflict" and label.endswith("-following-no-change"):
                edited.write_bytes(b"concurrent edit\n")
        else:
            assert not copied.exists()
            assert not added.exists() and old.exists()
            assert edited.read_bytes() == b"original\n"
        return {"wall_s": 1}

    output = tmp_path / "result"

    prepare = bench.prepare_patch

    def check_setup(source, destination, patch_path):
        record = json.loads((destination / "results.json").read_text())
        assert record["patch_setup"] == {"status": "running"}
        assert record["samples"] == [] and "active_sample" not in record
        if index_version is None:
            monkeypatch.delenv("GIT_INDEX_VERSION", raising=False)
        else:
            monkeypatch.setenv("GIT_INDEX_VERSION", index_version)
        edit = prepare(source, destination, patch_path)
        with (destination / "patch.index").open("rb") as stream:
            assert stream.read(4) == b"DIRC"
            assert int.from_bytes(stream.read(4), "big") == int(index_version or "4")
        return edit

    monkeypatch.setattr(bench, "prepare_patch", check_setup)

    def run():
        return bench.run(source, obj, tmp_path, "patch", 2, 4, {}, output, patch_file)

    with patch.object(bench, "measure", measure):
        if outcome == "complete":
            run()
            assert len(labels) == 7
        elif outcome == "conflict":
            with pytest.raises(RuntimeError, match="Could not restore"):
                run()
            assert edited.read_bytes() == b"concurrent edit\n"
            assert copied.read_bytes() == copy_source.read_bytes()
            assert added.exists() and not old.exists()
        else:
            edited.write_bytes(b"preexisting edit\n")
            with pytest.raises(RuntimeError):
                run()
            assert labels == [] and edited.read_bytes() == b"preexisting edit\n"
    record = json.loads((output / "results.json").read_text())
    setup = record["patch_setup"]
    assert setup["status"] == (
        "incomplete" if outcome == "inapplicable" else "complete"
    )
    assert setup["wall_s"] >= 0
    assert setup["child_usage"].keys() == bench.child_usage().keys()
    assert all(value >= 0 for value in setup["child_usage"].values())
    assert all(row["phase"] != "patch-setup" for row in record["samples"])
    assert (output / "workload.patch").read_bytes() == patch_file.read_bytes()
    assert (source / ".git/index").read_bytes() == index
    recovery = outcome == "conflict"
    assert (output / "patch.index").exists() == recovery
    assert (tmp_path / "buildbench.lock").exists() == recovery
    assert ("recovery" in record) == recovery


def test_interrupted_patch_setup(tmp_path, obj, monkeypatch):
    output = tmp_path / "results"

    def interrupt(source, destination, patch_path):
        (destination / "patch.index").touch()
        raise KeyboardInterrupt

    monkeypatch.setattr(bench, "prepare_patch", interrupt)
    with pytest.raises(KeyboardInterrupt):
        bench.run(
            tmp_path, obj, tmp_path, "patch", 1, 4, {}, output, tmp_path / "edit.patch"
        )
    record = json.loads((output / "results.json").read_text())
    assert record["patch_setup"]["status"] == record["status"] == "incomplete"
    assert record["error"] == "KeyboardInterrupt"
    assert record["samples"] == [] and "active_sample" not in record
    assert not (output / "patch.index").exists()
    assert not (tmp_path / "buildbench.lock").exists()


def test_reject_clobber_during_edit(tmp_path, obj, monkeypatch):
    relative, before, _ = bench.EDITS["image-alt-text"]
    fixture = tmp_path / relative
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(before)
    (obj / "CLOBBER").touch()
    calls = []

    def measure(*args, **kwargs):
        import os

        calls.append(True)
        source_clobber = tmp_path / "CLOBBER"
        source_clobber.touch()
        newer = (obj / "CLOBBER").stat().st_mtime + 60
        os.utime(source_clobber, (newer, newer))
        return {"wall_s": 1}

    monkeypatch.setattr(bench, "measure", measure)
    with pytest.raises(ValueError, match="clobber is required before 1-edit"):
        bench.run(tmp_path, obj, tmp_path, "image-alt-text", 1, 4, {})
    assert len(calls) == 1
    assert fixture.read_bytes() == before


def test_edit_of_active_mozconfig_stops_before_build(tmp_path, obj):
    relative, original, _ = bench.EDITS["image-alt-text"]
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(original)
    write_configuration(tmp_path, obj, str(path))
    with patch.object(bench, "measure", return_value={"wall_s": 1}) as measure:
        with pytest.raises(ValueError, match="mozconfig changed before 1-edit"):
            bench.run(
                tmp_path,
                obj,
                tmp_path,
                "image-alt-text",
                1,
                1,
                {},
                mozconfig={"path": path},
            )
    assert measure.call_count == 1
    assert path.read_bytes() == original


def test_output_survives_clobber(tmp_path, obj):
    with pytest.raises(ValueError, match="outside the objdir"):
        bench.run(tmp_path, obj, tmp_path, "no-change", 1, 4, {}, obj / "results")
    assert not (obj / "results").exists()


def test_failed_build_retains_log(tmp_path, obj):
    (tmp_path / "mach").write_text("raise SystemExit(11)")
    with pytest.raises(RuntimeError, match="prepare exited 11"):
        bench.run(tmp_path, obj, tmp_path, "no-change", 1, 0, {})
    (out,) = (tmp_path / "buildbench").iterdir()
    assert json.loads((out / "results.json").read_text())["status"] == "incomplete"
    assert (out / "prepare.log").exists()
    assert not (tmp_path / "buildbench.lock").exists()


@pytest.mark.parametrize(
    "key",
    [
        "CCACHE",
        "COMPILER_WRAPPER",
        "MOZ_ARTIFACT_BUILDS",
        "MOZ_RUSTC_WRAPPER",
        "MOZ_PGO",
    ],
)
def test_configuration(key):
    config = dict(
        MOZ_BUILD_APP="browser",
        CC=["clang"],
        CXX=["clang++"],
        HOST_CC=["clang"],
        HOST_CXX=["clang++"],
        RUSTC="rustc",
        CARGO_INCREMENTAL="1",
    )
    assert bench.configuration(config, {})["CARGO_INCREMENTAL"] == "1"
    with pytest.raises(ValueError):
        bench.configuration({**config, key: "1"}, {})
    with pytest.raises(ValueError):
        bench.configuration(config, {"RUSTC_WRAPPER": "sccache"})


@pytest.mark.parametrize(
    ("key", "command"),
    [
        ("CC", ["env", "sccache", "clang"]),
        ("HOST_CC", ["buildcache", "clang"]),
        ("HOST_CXX", ["sccache.exe", "clang-cl.exe"]),
    ],
)
def test_reject_wrapped_compiler(obj, key, command):
    config = json.loads((obj / "config.status.json").read_bytes())["substs"]
    with pytest.raises(ValueError, match=key):
        bench.configuration({**config, key: command}, {})


@pytest.mark.parametrize(
    ("filename", "key"),
    [("mozinfo.json", "topsrcdir"), ("config.status.json", "topobjdir")],
)
def test_reject_mismatched_directory(tmp_path, obj, filename, key):
    path = obj / filename
    data = json.loads(path.read_bytes())
    data[key] = str(tmp_path / "other")
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=key):
        bench.run(tmp_path, obj, tmp_path, "no-change", 1, 4, {})


@pytest.mark.parametrize(
    ("mozconfig", "message"),
    [
        ({"path": "other"}, "different mozconfig"),
        ({"configure_args": ["MOZ_PGO=1"]}, "disable MOZ_PGO"),
    ],
)
def test_reject_mozconfig_before_prepare(tmp_path, obj, mozconfig, message):
    with patch.object(bench, "measure") as measure:
        with pytest.raises(ValueError, match=message):
            bench.run(
                tmp_path, obj, tmp_path, "no-change", 1, 4, {}, mozconfig=mozconfig
            )
        measure.assert_not_called()


@pytest.mark.parametrize("key", ["host", "target", "MOZ_DEBUG", "MOZ_OPTIMIZE_FLAGS"])
def test_configuration_drift(tmp_path, obj, key):
    def measure(*args, **kwargs):
        path = obj / "config.status.json"
        data = json.loads(path.read_bytes())
        data["substs"][key] = "changed"
        path.write_text(json.dumps(data))
        return {"wall_s": 1}

    with patch.object(bench, "measure", measure):
        with pytest.raises(ValueError, match="configuration changed"):
            bench.run(tmp_path, obj, tmp_path, "no-change", 1, 4, {})


if __name__ == "__main__":
    mozunit.main()
