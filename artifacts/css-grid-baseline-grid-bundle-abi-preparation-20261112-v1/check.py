import ast
import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import layouts
import run

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def refused(action):
    try:
        action()
    except (AssertionError, KeyError):
        return
    raise AssertionError("expected refusal")


def main():
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text())
    for name, row in json.loads((HERE / "COPIES.json").read_text()).items():
        source = Path(row["origin"])
        assert run.sha(source) == row["sha256"]
        expected = source.read_bytes()
        if name.endswith(".cpp"):
            expected += (HERE / (name.split("/")[0] + "-probe.inc")).read_bytes()
        assert (HERE / name).read_bytes() == expected
    requests = json.loads((HERE / "REQUESTS.json").read_text())
    entry = json.loads((HERE / "COMPILE-DB-ENTRY.json").read_text())
    expected = list(entry["arguments"])
    offset = expected.index("-o")
    assert expected[offset + 1] == "/dev/null"
    del expected[offset:offset + 2]
    expected.remove("-c")
    for request in requests:
        label = request["label"]
        assert request["argv"] == expected + [
            "-fsyntax-only", "-Xclang", "-fdump-record-layouts", "-ivfsoverlay",
            str(HERE / (label + "-overlay.json")), "-MD", "-MF",
            "{OUT}/" + label + ".d", "-MT", "abi-" + label]
        assert request["cwd"] == entry["directory"]
        overlay = json.loads((HERE / (label + "-overlay.json")).read_text())
        assert overlay["use-external-names"] is False
        assert len(overlay["roots"]) == 5
        assert len({item["name"] for item in overlay["roots"]}) == 5
        aliases = {}
        for name in ("nsGridContainerFrame.cpp", "nsGridContainerFrame.h", "nsFrameStateBits.h"):
            contents = str(HERE / label / "layout/generic" / name)
            aliases[str(REPO / "layout/generic" / name)] = contents
            if name.endswith(".h"):
                aliases[str(REPO / "objdir-full.noindex/dist/include" / name)] = contents
        assert {item["name"]: item["external-contents"] for item in overlay["roots"]} == aliases
        assert "offsetof" not in (HERE / (label + "-probe.inc")).read_text()
    previous = REPO / "artifacts/css-grid-baseline-demand-snapshot-abi-20261112-v1"
    original_dump = (previous / "layout.stdout").read_text()
    types = requests[0]["types"]
    parsed = layouts.records(original_dump, set(types.values()))
    facts = "*** Dumping AST Record Layout\n         0 | struct GridBundleAbiFacts\n"
    for key, name in types.items():
        for metric in ("size", "align"):
            facts += f"         0 |   char[{parsed[name][metric]}] {key}_{metric}\n"
    facts += "           | [sizeof=1, dsize=1, align=1,\n           | nvsize=1, nvalign=1]\n"
    values = layouts.extract(original_dump + facts, types)
    assert values["cache"]["size"] == 52 and values["result"]["size"] == 40
    refused(lambda: layouts.extract(original_dump, types))
    refused(lambda: layouts.extract(original_dump + facts.replace("char[52] cache_size", "char[53] cache_size"), types))
    refused(lambda: layouts.extract(original_dump + facts.replace("frame_align", "wrong_align"), types))
    auth = json.loads((HERE / "AUTHORIZATION-TEMPLATE.json").read_text())
    with patch.object(run, "sha", return_value="sealed"):
        out = HERE / "never-created"
        refused(lambda: run.validate_authorization(auth, out))
        auth.update(authorized=True, preparation_manifest_sha256="sealed", out=str(out))
        run.validate_authorization(auth, out)
        for field, value in [("commands", 3), ("seconds_per_command", 181),
                             ("rss_bytes", 2147483649), ("stdout_stderr_bytes_per_command", 67108865),
                             ("preparation_manifest_sha256", "wrong"), ("out", str(out) + "-other")]:
            changed = copy.deepcopy(auth)
            changed[field] = value
            refused(lambda: run.validate_authorization(changed, out))
    checks = []
    with tempfile.TemporaryDirectory(prefix="grid-abi-source-check-") as tmp:
        scratch = Path(tmp)
        for label, launch_error, inspection_error in [("exit-failure", False, False),
                                                       ("launch-failure", True, False),
                                                       ("inspection-failure", False, True)]:
            class FakeProcess:
                pid = 987654

                def poll(self):
                    return None if inspection_error else 1

            def launch(*args, **kwargs):
                if launch_error:
                    raise OSError("injected launch failure")
                return FakeProcess()

            def inspect(pgid):
                raise OSError("injected process inspection failure")

            cleanup = dict(group_absent=True, inspection_errors=[], cleanup_signals=[])
            request = dict(label=label, argv=["not-executed"], cwd=str(scratch))
            with patch.object(run.subprocess, "Popen", side_effect=launch), patch.object(run.lifecycle, "inspect_group", side_effect=inspect), patch.object(run.lifecycle, "settle_group", return_value=cleanup):
                refused(lambda: run.command(request, scratch))
            receipt = json.loads((scratch / (label + "-COMMAND.json")).read_text())
            assert receipt["exit"] != 0
            if launch_error or inspection_error:
                assert receipt["termination_reason"] is not None
            checks.append(label)
    assert not scratch.exists()
    resource_checks = []
    with tempfile.TemporaryDirectory(prefix="grid-abi-resource-check-") as tmp:
        scratch = Path(tmp)
        for mode in ("rss", "time", "output"):
            class RunningProcess:
                pid = 987655

                def poll(self):
                    return None

            ticks = [0]

            def clock():
                value = ticks[0]
                ticks[0] = 181 if mode == "time" else 0
                return value

            def launch(*args, **kwargs):
                if mode == "output":
                    kwargs["stdout"].truncate(67108865)
                return RunningProcess()

            def inspect(pgid):
                return [(987655, 2147483649 if mode == "rss" else 0)]

            request = dict(label=mode, argv=["not-executed"], cwd=str(scratch))
            cleanup = dict(group_absent=True, inspection_errors=[], cleanup_signals=["mock-only"])
            with patch.object(run.subprocess, "Popen", side_effect=launch), patch.object(run.lifecycle, "inspect_group", side_effect=inspect), patch.object(run.lifecycle, "settle_group", return_value=cleanup), patch.object(run.time, "monotonic", side_effect=clock):
                refused(lambda: run.command(request, scratch))
            receipt = json.loads((scratch / (mode + "-COMMAND.json")).read_text())
            assert receipt["termination_reason"] and receipt["group_absent"]
            resource_checks.append(mode)
    assert not scratch.exists()
    dependency_checks = []
    with tempfile.TemporaryDirectory(prefix="grid-abi-dependency-check-") as tmp:
        scratch = Path(tmp)
        admitted = scratch / "admitted.h"
        admitted.write_text("admitted input\n")
        pins = {str(admitted): {"sha256": run.sha(admitted)}}
        request = dict(label="baseline", cwd=str(scratch))
        depfile = scratch / "baseline.d"
        depfile.write_text("abi: " + str(admitted) + "\n")
        run.dependencies(request, scratch, pins)
        dependency_checks.append("admitted dependency")
        depfile.write_text("abi: " + str(scratch / "unknown.h") + "\n")
        refused(lambda: run.dependencies(request, scratch, pins))
        dependency_checks.append("unknown dependency refused")
        depfile.write_text("abi: " + str(admitted) + "\n")
        admitted.write_text("changed input\n")
        refused(lambda: run.dependencies(request, scratch, pins))
        dependency_checks.append("changed dependency refused")
        depfile.write_text("abi:\n")
        refused(lambda: run.dependencies(request, scratch, pins))
        dependency_checks.append("empty dependency refused")
    assert not scratch.exists()
    pins = json.loads((HERE / "INPUTS.json").read_text())
    for name, row in pins.items():
        assert str(Path(name).resolve()) == row["resolved"]
        assert run.sha(Path(name)) == row["sha256"], name
    result = dict(status="PASS source-only preparation checks", pinned_inputs=len(pins),
                  exact_commands=2, copied_sources=6, overlay_aliases_per_command=5,
                  prior_real_layouts_checked=list(values), parser_refusals=3,
                  authorization_refusals=7, injected_failure_receipts=checks,
                  dependency_checks=dependency_checks,
                  injected_resource_refusals=resource_checks,
                  scratch_removed=True, compiler_executed=False)
    (HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
