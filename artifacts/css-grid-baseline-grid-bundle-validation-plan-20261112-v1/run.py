import argparse
import hashlib
import json
import os
from pathlib import Path

import process

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PYTHON = "/Users/bgrins/venvs/firefox/bin/python"
SOURCES = ("layout/generic/nsGridContainerFrame.cpp", "layout/generic/nsGridContainerFrame.h",
           "layout/generic/nsFrameStateBits.h")


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def outcomes(report):
    result = {}
    for item in report["results"]:
        key = (item["test"], None)
        assert key not in result
        result[key] = item["status"]
        for subtest in item["subtests"]:
            key = (item["test"], subtest["name"])
            assert key not in result
            result[key] = subtest["status"]
    return result


def authenticate(side="original"):
    for name, row in read(HERE / "FILES.json")["files"].items():
        assert sha(HERE / name) == row["sha256"], name
    for name, digest in read(HERE / "PARENTS.json").items():
        assert sha(name) == digest, name
    for name, row in read(HERE / "TOOL-PINS.json").items():
        assert str(Path(name).resolve()) == row["resolved"], name
        assert sha(name) == row["sha256"], name
    for name, digest in read(HERE / "LIVE-PINS.json").items():
        expected = sha(HERE / side / name) if name in SOURCES else digest
        assert sha(ROOT / name) == expected, name


def validate_authorization(auth, out):
    assert auth["authorized"] is True
    assert auth["preparation_manifest_sha256"] == sha(HERE / "FILES.json")
    assert Path(auth["out"]).resolve() == out
    expected = dict(stage="correctness", commands=8, build_jobs=2,
                    build_timeout=1800, wpt_timeout=600, always_restore=True)
    assert all(auth[name] == value for name, value in expected.items())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    validate_authorization(read(args.authorization), out)
    authenticate()
    out.mkdir(exist_ok=False)
    (out / "AUTHORIZATION.json").write_bytes(args.authorization.read_bytes())
    save(out / "PREPARATION.json", dict(path=str(HERE), sha256=sha(HERE / "FILES.json")))
    runner = process.Runner(out)
    env = dict(os.environ, MOZCONFIG=str(ROOT / "mozconfig"),
               MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"), MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
    expected_binaries = read(HERE / "BINARY-AUTHORITY.json")
    originals = {name: (HERE / "original" / name).read_bytes() for name in SOURCES}
    candidates = {name: (HERE / "candidate" / name).read_bytes() for name in SOURCES}
    for name in SOURCES:
        target = out / "source-before" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(originals[name])
    result = dict(status="INCOMPLETE", accepted_repair=False, stages={})
    installed = []

    def binaries(label):
        data = {name: dict(sha256=sha(name), bytes=Path(name).stat().st_size)
                for name in expected_binaries}
        save(out / (label + "-BINARIES.json"), data)
        return data

    def command(label, argv, timeout):
        save(out / "LIVE.json", dict(phase=label, status="launching"))
        row, _ = runner.run(argv, ROOT, env, label, timeout=timeout)
        save(out / "LIVE.json", dict(phase=label, status="terminal", exit=row["exit"]))
        return row

    def build(label):
        row = command(label, [PYTHON, "./mach", "build", "binaries", "-j2"], 1800)
        assert row["exit"] == 0
        return binaries(label)

    def wpt(label, paths):
        before = binaries(label + "-before")
        row = command(label, [PYTHON, "./mach", "wpt", "--headless", "--no-pause-after-test",
                             "--processes=1", "--binary=" + next(n for n in before if n.endswith("/firefox")),
                             "--log-raw=" + str(out / (label + "-raw.log")),
                             "--log-wptreport=" + str(out / (label + "-wptreport.json")), *paths], 600)
        assert row["exit"] in (0, 1)
        if label.endswith("-focused"):
            assert row["exit"] == 0
        assert binaries(label + "-after") == before
        return read(out / (label + "-wptreport.json"))

    def check_phase(phase, side):
        authenticate(side)
        focused = wpt(phase + "-focused", list(read(HERE / "FOCUSED.json")))
        assert len(focused["results"]) == 3
        assert outcomes(focused) == outcomes(read(HERE / "EXPECTED-FOCUSED.json"))
        assert sum(len(item["subtests"]) for item in focused["results"]) == 700
        assert all(item["status"] == "OK" and all(s["status"] == "PASS" for s in item["subtests"])
                   for item in focused["results"])
        alignment = wpt(phase + "-alignment", ["testing/web-platform/tests/css/css-grid/alignment"])
        assert len(alignment["results"]) == 457
        assert outcomes(alignment) == outcomes(read(HERE / "EXPECTED-ALIGNMENT.json"))
        authenticate(side)
        result["stages"][phase] = dict(focused_pass=700, alignment_files=457,
                                      alignment_outcomes_equal=True)

    try:
        assert binaries("before") == expected_binaries
        check_phase("baseline", "original")
        for name in SOURCES:
            assert (ROOT / name).read_bytes() == originals[name]
            (ROOT / name).write_bytes(candidates[name])
            installed.append(name)
        save(out / "INSTALL.json", dict(files=installed))
        build("candidate-build")
        check_phase("candidate", "candidate")
    except BaseException as error:
        result["error"] = repr(error)
    finally:
        try:
            assert runner.safe_cleanup and all(process.absent(g) for g in runner.groups)
            for name in installed:
                assert (ROOT / name).read_bytes() == candidates[name], ("concurrent source mutation", name)
                (ROOT / name).write_bytes(originals[name])
            result["source_restored"] = all((ROOT / name).read_bytes() == originals[name] for name in SOURCES)
            save(out / "RESTORATION.json", result)
            if installed:
                restored = build("restored-build")
                result["restored_binary_byte_identical"] = restored == expected_binaries
                check_phase("restored", "original")
                result["build_restored"] = True
            authenticate()
            result["fresh_groups_absent"] = all(process.absent(g) for g in runner.groups)
            assert result["fresh_groups_absent"]
            if "error" not in result:
                assert len(runner.commands) == 8
                assert set(result["stages"]) == {"baseline", "candidate", "restored"}
                result["status"] = "COMPLETED_AND_RESTORED correctness gate only"
        except BaseException as error:
            result["restoration_error"] = repr(error)
        save(out / "RESTORATION.json", result)
        save(out / "RESULT.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"].startswith("COMPLETED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
