import contextlib
import copy
import io
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import run

HERE = Path(__file__).resolve().parent
CONFIGS = run.read(HERE / "CONFIGS.json")
CASES = ["success"] + run.expected_labels(CONFIGS) + ["unsafe-lifecycle", "concurrent-source-change",
         "partial-install", "truncated-trace", "missing-phase", "wrong-final-count", "missing-switch-coverage", "tool-drift", "config-drift", "tool-resolution-drift",
         "config-resolution-drift", "tool-unavailable"]


def exercise(case, base):
    root = base.resolve() / case
    prep = root / "artifacts/preparation"
    prep.mkdir(parents=True)
    for name in ("EXPECTED-FOCUSED.json", "EXPECTED-ALIGNMENT.json", "FOCUSED.json", "CONFIGS.json", "AUTHORIZATION-TEMPLATE.json"):
        (prep / name).write_bytes((HERE / name).read_bytes())
    for side in ("demand", "bundle", "instrumented"):
        for i, name in enumerate(run.SOURCES):
            path = prep / side / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(side + " source " + str(i))
    originals = {name: (prep / "demand" / name).read_bytes() for name in run.SOURCES}
    for name, data in originals.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    fixture_dir = prep / "fixtures"
    fixture_dir.mkdir()
    (root / "testing/web-platform/tests/css/css-grid/alignment").mkdir(parents=True)
    for c in CONFIGS:
        (fixture_dir / (c["name"] + ".html")).write_text("mock fixture " + c["name"])
    binary = root / "firefox"
    binary.write_text("demand binary")
    bins = {str(binary): dict(sha256=run.sha(binary), bytes=binary.stat().st_size)}
    receipt = root / "restoration.json"
    run.save(receipt, {"mock": True})
    work = {c["name"]: dict((key, c[key]) for key in ("depth", "lines", "columns", "orientation", "group")) for c in CONFIGS}
    for value in work.values():
        value["checksum"] = 10
    tool_target = root / "python-target"
    tool_target.write_text("mock python")
    tool = root / "python"
    tool.symlink_to(tool_target)
    config_target = root / "config-target"
    config_target.write_text("mock config")
    config = root / "mozconfig"
    config.symlink_to(config_target)
    mach = root / "mach"
    mach.write_text("mock mach")
    status = root / "objdir-full.noindex/config.status"
    status.parent.mkdir()
    status.write_text("mock config status")
    def pins(paths):
        return {str(path): dict(resolved=str(path.resolve()), sha256=run.sha(path)) for path in paths}
    binding = dict(ready=True, restoration_receipt=dict(path=str(receipt), sha256=run.sha(receipt)), tools=pins((tool, mach)), configs=pins((config, status)),
                   live_pins={name: run.sha(root / name) for name in run.SOURCES}, binaries=bins, work_observations=work)
    authority = root / "authority.json"
    run.save(authority, binding)
    run.save(prep / "PARENTS.json", {})
    run.save(prep / "FILES.json", dict(files={str(path.relative_to(prep)):dict(sha256=run.sha(path)) for path in prep.rglob("*") if path.is_file()}))
    out = root / "artifacts/output"
    auth = run.read(prep / "AUTHORIZATION-TEMPLATE.json")
    auth.update(authorized=True, preparation_manifest_sha256=run.sha(prep / "FILES.json"), authority_sha256=run.sha(authority), out=str(out))
    authorization = root / "authorization.json"
    run.save(authorization, auth)
    commands = []

    class Runner:
        def __init__(self, target):
            assert target == out
            self.commands, self.groups, self.safe_cleanup = commands, [], True

        def run(self, argv, cwd, env, label, timeout):
            assert cwd == root and argv[:2] == [run.PYTHON, "./mach"]
            if label.endswith("-build"):
                assert argv[2:] == ["build", "binaries", "-j2"] and timeout == 1800
                if case == "unsafe-lifecycle" and label == "instrumented-bundle-build":
                    self.safe_cleanup = False
                    raise RuntimeError("mock unresolved process")
                binary.write_text("demand binary" if label == "restored-demand-build" else label)
                if label == "instrumented-bundle-build":
                    if case == "tool-drift":
                        tool.write_text("changed tool")
                    elif case == "config-drift":
                        status.write_text("changed config")
                    elif case in ("tool-resolution-drift", "config-resolution-drift"):
                        link = tool if case == "tool-resolution-drift" else config
                        alternate = root / "alternate-target"
                        alternate.write_bytes(link.read_bytes())
                        link.unlink()
                        link.symlink_to(alternate)
                    elif case == "tool-unavailable":
                        tool_target.unlink()
            else:
                assert argv[2:6] == ["wpt", "--headless", "--no-pause-after-test", "--processes=1"] and timeout == 600
                if label.endswith(("-focused", "-alignment")):
                    report = copy.deepcopy(run.read(prep / ("EXPECTED-FOCUSED.json" if label.endswith("-focused") else "EXPECTED-ALIGNMENT.json")))
                else:
                    assert "--timeout-multiplier=16" in argv
                    name = next(c["name"] for c in CONFIGS if label.endswith(c["name"]))
                    value = dict(work[name], samples=[1, 2, 3])
                    report = dict(results=[dict(test=argv[-1], status="OK", subtests=[
                        dict(name="Collect a bounded dual-axis baseline workload; native demand coverage is required", status="PASS"),
                        dict(name="WORKLOAD " + run.json.dumps(value), status="PASS")])])
                report_path = Path(next(x.split("=", 1)[1] for x in argv if x.startswith("--log-wptreport=")))
                run.save(report_path, report)
                Path(next(x.split("=", 1)[1] for x in argv if x.startswith("--log-raw="))).write_text("")
                if case == "concurrent-source-change" and label == "instrumented-bundle-d1-parallel":
                    (root / run.SOURCES[0]).write_text("external mutation")
            (out / (label + ".log")).write_text("mock retained log")
            row = dict(label=label, argv=argv, exit=2 if case == label else 0)
            commands.append(row)
            if case == "wrong-final-count" and label == "restored-demand-alignment":
                commands.append(dict(label="extra"))
            return row, None

    def extract(raw, trace, parser):
        if case == "truncated-trace":
            raise AssertionError("mock cap refusal")
        trace.write_text("mock parsed through separate accepted parser tests")
        return "mock-process"

    def parsed(path, version):
        phases = {"seed": {}} | {"prime" + str(i): {} for i in range(4)} | {"sample" + str(i) + "-toggle" + str(j): {} for i in range(3) for j in range(8)}
        if case == "missing-phase":
            phases.pop("prime3")
        return dict(phase_totals=phases, bundle_totals=dict(bundled_captures=3),
                    exact_bundle_switch_hits={} if case == "missing-switch-coverage" else {"(4, 5)": 1, "(5, 4)": 1})

    write = Path.write_bytes
    def writes(path, data):
        if case == "partial-install" and path == root / run.SOURCES[1] and data.startswith(b"bundle"):
            raise OSError("mock second source refusal before write")
        return write(path, data)

    with patch.object(run, "HERE", prep), patch.object(run, "ROOT", root), patch.object(run, "PYTHON", str(tool)), \
         patch.object(run.process, "Runner", Runner), patch.object(run.process, "absent", return_value=True), \
         patch.object(run.shutil, "disk_usage", return_value=SimpleNamespace(free=run.MIN_FREE+1)), \
         patch.object(run.observations, "extract_trace", extract), patch.object(run.trace_parser, "parse_file", parsed), \
         patch.object(Path, "write_bytes", writes), contextlib.redirect_stdout(io.StringIO()):
        code = run.main(out, authorization, authority)
    result = run.read(out / "RESULT.json")
    assert result == run.read(out / "RESTORATION.json")
    completed = case in ("success", "missing-switch-coverage")
    assert code == (0 if completed else 1)
    if completed:
        assert len(commands) == 18 and result["cost_comparison_coverage"] == (case == "success")
        assert result["cost_claim"] is False
    if case in ("unsafe-lifecycle", "concurrent-source-change"):
        assert "restoration_error" in result
        assert "restored-demand-build" not in [x["label"] for x in commands]
    else:
        assert all((root / name).read_bytes() == data for name, data in originals.items())
        assert not list((root / "testing/web-platform/tests/css/css-grid/alignment").glob("grid-bundle-work-local-*"))
    if case in ("tool-drift", "config-drift", "tool-resolution-drift", "config-resolution-drift", "tool-unavailable"):
        assert result["source_restored"] and result["owned_fixtures_removed"]
        assert result["runtime_restoration"].startswith("INCOMPLETE")
        assert not result.get("build_restored", False)
        assert commands[-1]["label"] == "instrumented-bundle-build"
        checks = run.read(out / "INPUT-CHECKS.json")
        assert checks[-2]["label"] == "instrumented-bundle-build:after" and checks[-2]["status"] == "FAIL"
        assert checks[-1]["label"] == "restored-demand-build:before" and checks[-1]["status"] == "FAIL"
    if case == "success":
        checks = run.read(out / "INPUT-CHECKS.json")
        assert len(checks) == 38 and all(x["status"] == "PASS" for x in checks)
    return dict(case=case, exit=code, result=result, commands=[x["label"] for x in commands], mock_only=True)


def main():
    with tempfile.TemporaryDirectory(prefix="grid-bundle-work-mock-") as tmp:
        scratch = Path(tmp)
        results = [exercise(case, scratch) for case in CASES]
        binding = dict(tools={run.PYTHON: {}, str(run.ROOT / "mach"): {}},
                       configs={str(run.ROOT / "mozconfig"): {}, str(run.ROOT / "objdir-full.noindex/config.status"): {}})
        missing = []
        for category in ("tools", "configs"):
            for name in binding[category]:
                bad = copy.deepcopy(binding)
                del bad[category][name]
                try:
                    run.validate_execution_binding(bad)
                except AssertionError:
                    missing.append(name)
                else:
                    raise AssertionError("missing mandatory pin accepted")
        assert len(missing) == 4
    assert not scratch.exists()
    value = dict(status="PASS source-only mock transaction checks", cases=results, scratch_removed=True, native_commands_executed=0, missing_required_pin_refusals=missing)
    run.save(HERE / "FAILURE-CHECK.json", value)
    print(run.json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
