import argparse
import ast
import hashlib
import json
import os
import shutil
from pathlib import Path

import observations
import parse as trace_parser
import process

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PYTHON = "/Users/bgrins/venvs/firefox/bin/python"
SOURCES = ("layout/generic/nsGridContainerFrame.cpp", "layout/generic/nsGridContainerFrame.h",
           "layout/generic/nsFrameStateBits.h", "layout/generic/nsBlockFrame.cpp")
PHASES = ("baseline-bundle", "instrumented-bundle", "restored-bundle")
MIN_FREE = 48 * 1024**3
MAX_JSON = 16 * 1024**2


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    encoded = json.dumps(data, indent=2) + "\n"
    assert len(encoded.encode()) <= MAX_JSON
    Path(path).write_text(encoded)


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


def authenticate_preparation():
    for name, row in read(HERE / "FILES.json")["files"].items():
        assert sha(HERE / name) == row["sha256"], name
    for name, digest in read(HERE / "PARENTS.json").items():
        assert sha(name) == digest, name


def expected_labels(configs):
    result = []
    for phase in PHASES:
        result += [phase + "-build"] + [phase + "-" + c["name"] for c in configs]
    return result + ["restored-demand-build", "restored-demand-focused", "restored-demand-alignment"]


def validate_execution_binding(binding):
    assert {PYTHON, str(ROOT / "mach")} <= set(binding["tools"]), "Required Python/mach pin missing"
    assert {str(ROOT / "mozconfig"), str(ROOT / "objdir-full.noindex/config.status")} <= set(binding["configs"]), "Required config pin missing"


def main(out, authorization, authority):
    out, authorization, authority = out.resolve(), authorization.resolve(), authority.resolve()
    assert not authorization.is_relative_to(HERE) and not authority.is_relative_to(HERE)
    approval, binding = read(authorization), read(authority)
    template = read(HERE / "AUTHORIZATION-TEMPLATE.json")
    assert approval["authorized"] is True and binding["ready"] is True
    validate_execution_binding(binding)
    for key in ("stage", "commands", "build_jobs", "build_timeout", "wpt_timeout",
                "timeout_multiplier", "record_cap", "always_restore"):
        assert approval[key] == template[key], key
    assert approval["preparation_manifest_sha256"] == sha(HERE / "FILES.json")
    assert approval["authority_sha256"] == sha(authority)
    assert approval["out"] == str(out) and out.parent == ROOT / "artifacts" and not out.exists()
    authenticate_preparation()
    assert sha(binding["restoration_receipt"]["path"]) == binding["restoration_receipt"]["sha256"]
    for category in ("tools", "configs"):
        for name, row in binding[category].items():
            assert str(Path(name).resolve()) == row["resolved"] and sha(name) == row["sha256"], name
    current = {name: (HERE / "demand" / name).read_bytes() for name in SOURCES}
    originals = dict(current)
    for name, data in current.items():
        assert (ROOT / name).read_bytes() == data
        assert binding["live_pins"][name] == hashlib.sha256(data).hexdigest()
    configs = read(HERE / "CONFIGS.json")
    fixtures = {c["name"]: (HERE / "fixtures" / (c["name"] + ".html")).read_bytes() for c in configs}
    tests = {name: ROOT / ("testing/web-platform/tests/css/css-grid/alignment/grid-bundle-work-local-" + name + ".html") for name in fixtures}
    assert all(not path.exists() for path in tests.values())
    expected_binaries = binding["binaries"]
    assert all(sha(name) == row["sha256"] and Path(name).stat().st_size == row["bytes"]
               for name, row in expected_binaries.items())
    for name, digest in binding["live_pins"].items():
        assert sha(ROOT / name) == digest, name
    disk = shutil.disk_usage(out.parent)
    assert disk.free >= MIN_FREE
    out.mkdir()
    save(out / "AUTHORIZATION.json", approval)
    save(out / "AUTHORITY.json", binding)
    save(out / "PREPARATION.json", dict(path=str(HERE), sha256=sha(HERE / "FILES.json")))
    save(out / "DISK.json", dict(free=disk.free, required=MIN_FREE))
    for name, data in originals.items():
        target = out / "source-before" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    runner = process.Runner(out)
    env = dict(os.environ, MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"),
               MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
    result = dict(status="INCOMPLETE", accepted_repair=False, timing_claim=False)
    installed_tests, parsed, comparable = [], {}, {}
    touched = False
    input_checks = []

    def execution_inputs(label):
        record = dict(label=label, status="checking")
        try:
            for category in ("tools", "configs"):
                for name, pin in binding[category].items():
                    assert str(Path(name).resolve()) == pin["resolved"], (category, "resolution", name)
                    assert sha(name) == pin["sha256"], (category, "bytes", name)
            preserved()
            record["status"] = "PASS"
        except BaseException as error:
            record.update(status="FAIL", error=repr(error))
            raise
        finally:
            input_checks.append(record)
            save(out / "INPUT-CHECKS.json", input_checks)

    def preserved():
        for name, digest in binding["live_pins"].items():
            assert sha(ROOT / name) == (hashlib.sha256(current[name]).hexdigest() if name in current else digest), name

    def safe():
        assert runner.safe_cleanup and all(process.absent(group) for group in runner.groups)
        for name in SOURCES:
            assert (ROOT / name).read_bytes() == current[name], ("concurrent source mutation", name)

    def binaries(label):
        values = {name: dict(sha256=sha(name), bytes=Path(name).stat().st_size) for name in expected_binaries}
        save(out / (label + "-BINARIES.json"), values)
        return values

    def command(label, argv, timeout):
        execution_inputs(label + ":before")
        save(out / "LIVE.json", dict(phase=label, status="launching"))
        try:
            row, _ = runner.run(argv, ROOT, env, label, timeout=timeout)
            save(out / "LIVE.json", dict(phase=label, status="terminal", exit=row["exit"]))
        finally:
            execution_inputs(label + ":after")
        limit = 64 * 1024**2 if label.endswith("-build") else (4 * 1024**3 if label.startswith("instrumented-bundle-") else 16 * 1024**2)
        assert (out / (label + ".log")).stat().st_size <= limit
        return row

    def install(side):
        nonlocal touched
        safe()
        for name in SOURCES:
            data = (HERE / side / name).read_bytes()
            if data != current[name]:
                touched = True
                (ROOT / name).write_bytes(data)
                current[name] = data
        save(out / (side + "-INSTALL.json"), {name: sha(ROOT / name) for name in SOURCES})

    def build(label):
        assert command(label, [PYTHON, "./mach", "build", "binaries", "-j2"], 1800)["exit"] == 0
        preserved()
        return binaries(label)

    def wpt(label, paths, allow_failure=False, work=False):
        before = binaries(label + "-before")
        args = [PYTHON, "./mach", "wpt", "--headless", "--no-pause-after-test", "--processes=1"]
        if work:
            args += ["--timeout-multiplier=16"]
        args += ["--binary=" + next(name for name in before if name.endswith("/firefox")),
                 "--log-raw=" + str(out / (label + "-raw.log")),
                 "--log-wptreport=" + str(out / (label + "-wptreport.json")), *paths]
        row = command(label, args, 600)
        assert row["exit"] in ((0, 1) if allow_failure else (0,))
        assert binaries(label + "-after") == before
        preserved()
        report = out / (label + "-wptreport.json")
        assert report.stat().st_size <= MAX_JSON
        return read(report)

    def observe(phase):
        for config in configs:
            name = config["name"]
            label = phase + "-" + name
            assert tests[name].read_bytes() == fixtures[name]
            report = wpt(label, [str(tests[name].relative_to(ROOT))], work=True)
            full, value = observations.observation(report, config)
            save(out / (label + "-OBSERVATION.json"), full)
            assert value == binding["work_observations"][name]
            comparable[(phase, name)] = value
            if phase != PHASES[0]:
                assert value == comparable[(PHASES[0], name)]
            raw = out / (label + "-raw.log")
            if phase == "instrumented-bundle":
                trace = out / (label + "-TRACE.log")
                producer = observations.extract_trace(raw, trace, trace_parser)
                data = trace_parser.parse_file(trace, "bundle")
                required = {"seed"} | {"prime" + str(i) for i in range(4)} | {"sample" + str(i) + "-toggle" + str(j) for i in range(3) for j in range(8)}
                assert required <= set(data["phase_totals"])
                save(out / (label + "-PARSED.json"), data)
                parsed[name] = data
                save(out / (label + "-PRODUCER.json"), dict(process=producer))
            else:
                observations.no_trace(raw, trace_parser)

    def remove_fixtures():
        safe()
        for name in installed_tests:
            if tests[name].exists():
                assert tests[name].read_bytes() == fixtures[name], "Concurrent fixture edit"
                tests[name].unlink()
        assert all(not tests[name].exists() for name in installed_tests)

    try:
        for name, data in fixtures.items():
            with tests[name].open("xb") as stream:
                installed_tests.append(name)
                stream.write(data)
        for phase, side in zip(PHASES, ("bundle", "instrumented", "bundle")):
            install(side)
            build(phase + "-build")
            observe(phase)
    except BaseException as error:
        result["error"] = repr(error)
    finally:
        try:
            safe()
            for name in SOURCES:
                (ROOT / name).write_bytes(originals[name])
                current[name] = originals[name]
            result["source_restored"] = True
            remove_fixtures()
            result["owned_fixtures_removed"] = True
            if touched:
                result["runtime_restoration"] = "INCOMPLETE: pinned inputs and restored build/tests not yet verified"
                restored = build("restored-demand-build")
                result["build_restored"] = True
                result["binary_byte_identical"] = restored == expected_binaries
                focused = wpt("restored-demand-focused", list(read(HERE / "FOCUSED.json")))
                assert outcomes(focused) == outcomes(read(HERE / "EXPECTED-FOCUSED.json"))
                assert sum(len(x["subtests"]) for x in focused["results"]) == 700
                alignment = wpt("restored-demand-alignment", ["testing/web-platform/tests/css/css-grid/alignment"], allow_failure=True)
                assert len(alignment["results"]) == 457
                assert outcomes(alignment) == outcomes(read(HERE / "EXPECTED-ALIGNMENT.json"))
                result["restored_focused_pass"] = 700
                result["restored_alignment_files"] = 457
                execution_inputs("restoration:complete")
                result["runtime_restoration"] = "VERIFIED restored build and regression outcomes"
            safe()
            result["fresh_groups_absent"] = True
        except BaseException as error:
            result["restoration_error"] = repr(error)
        try:
            if not any(key.endswith("error") for key in result):
                execution_inputs("transaction:complete")
                assert [row["label"] for row in runner.commands] == expected_labels(configs)
                assert len(parsed) == 4 and len(comparable) == 12
                directions, bundles = set(), 0
                for name, data in parsed.items():
                    if not name.startswith("d4-"):
                        continue
                    bundles += data["bundle_totals"]["bundled_captures"]
                    for text, count in data["exact_bundle_switch_hits"].items():
                        a, b = ast.literal_eval(text)
                        if count and a in (3, 4) and b in (5, 6):
                            directions.add("GridB-to-GridI")
                        if count and a in (5, 6) and b in (3, 4):
                            directions.add("GridI-to-GridB")
                result.update(status="COMPLETED_AND_RESTORED work observations only", command_count=18,
                              actual_bundled_captures_depth4=bundles, observed_switch_directions=sorted(directions),
                              cost_comparison_coverage=bool(bundles and len(directions) == 2),
                              cost_claim=False, provider_gate_pending=True, state_harness_pending=True)
        except BaseException as error:
            result["completion_error"] = repr(error)
        save(out / "RESULT.json", result)
        save(out / "RESTORATION.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"].startswith("COMPLETED") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--authority", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.out, args.authorization, args.authority))
