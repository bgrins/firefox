import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import run

HERE = Path(__file__).resolve().parent
CASES = ("success", "baseline-focused", "baseline-alignment", "candidate-build",
         "candidate-focused", "candidate-alignment", "restored-build",
         "restored-focused", "restored-alignment", "unsafe-lifecycle",
         "concurrent-source-change", "partial-install", "wrong-final-count")


def exercise(case, base):
    root = base.resolve() / case
    prep = root / "artifacts/preparation"
    prep.mkdir(parents=True)
    for name in ("EXPECTED-FOCUSED.json", "EXPECTED-ALIGNMENT.json", "FOCUSED.json"):
        shutil.copyfile(HERE / name, prep / name)
    originals = {}
    candidates = {}
    for i, name in enumerate(run.SOURCES):
        originals[name] = f"original source {i}\n".encode()
        candidates[name] = f"candidate source {i}\n".encode()
        for side, content in (("original", originals[name]), ("candidate", candidates[name])):
            path = prep / side / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        live = root / name
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(originals[name])
    for name in ("PARENTS.json", "TOOL-PINS.json"):
        run.save(prep / name, {})
    run.save(prep / "LIVE-PINS.json", {name: run.sha(root / name) for name in run.SOURCES})
    bins = {}
    for name in ("firefox", "XUL"):
        path = root / name
        path.write_text("mock binary original")
        bins[str(path)] = dict(sha256=run.sha(path), bytes=path.stat().st_size)
    run.save(prep / "BINARY-AUTHORITY.json", bins)
    run.save(prep / "FILES.json", {"files": {str(path.relative_to(prep)): {"sha256": run.sha(path)}
             for path in prep.rglob("*") if path.is_file()}})
    out = root / "output"
    auth = run.read(HERE / "AUTHORIZATION-TEMPLATE.json")
    auth.update(authorized=True, preparation_manifest_sha256=run.sha(prep / "FILES.json"), out=str(out))
    authorization = root / "authorization.json"
    run.save(authorization, auth)
    all_commands = []

    class MockRunner:
        def __init__(self, target):
            assert target == out
            self.commands = all_commands
            self.groups = []
            self.safe_cleanup = True

        def run(self, argv, cwd, env, label, timeout):
            assert cwd == root and argv[0] == run.PYTHON and argv[1] == "./mach"
            assert env["MOZ_OBJDIR"] == str(root / "objdir-full.noindex")
            if label.endswith("-build"):
                assert argv[2:] == ["build", "binaries", "-j2"] and timeout == 1800
                if case == "unsafe-lifecycle" and label == "candidate-build":
                    self.safe_cleanup = False
                    raise RuntimeError("injected uncertain process lifecycle")
                for name in bins:
                    Path(name).write_text("mock binary original" if label == "restored-build" else "mock binary candidate")
            else:
                assert argv[2] == "wpt" and timeout == 600
                assert argv[3:6] == ["--headless", "--no-pause-after-test", "--processes=1"]
                name = "EXPECTED-FOCUSED.json" if label.endswith("-focused") else "EXPECTED-ALIGNMENT.json"
                report = copy.deepcopy(run.read(prep / name))
                if case == label:
                    report["results"][0]["status"] = "ERROR"
                report_arg = next(arg for arg in argv if arg.startswith("--log-wptreport="))
                run.save(Path(report_arg.split("=", 1)[1]), report)
                if case == "concurrent-source-change" and label == "candidate-focused":
                    (root / run.SOURCES[0]).write_text("independent concurrent change")
            record = dict(label=label, argv=argv, exit=1 if case == label else 0,
                          group_absent=True, safe_cleanup=self.safe_cleanup)
            self.commands.append(record)
            if case == "wrong-final-count" and label == "restored-alignment":
                self.commands.append(dict(label="injected extra command"))
            return record, None

    write_bytes = Path.write_bytes
    failed_install = False

    def checked_write(path, data):
        nonlocal failed_install
        if case == "partial-install" and path == root / run.SOURCES[1] and data == candidates[run.SOURCES[1]]:
            failed_install = True
            raise OSError("injected second-source write failure before modification")
        return write_bytes(path, data)

    with patch.object(run, "HERE", prep), patch.object(run, "ROOT", root), \
         patch.object(run.process, "Runner", MockRunner), patch.object(run.process, "absent", return_value=True), \
         patch.object(sys, "argv", ["run.py", "--authorization", str(authorization), "--out", str(out)]), \
         patch.object(Path, "write_bytes", checked_write), contextlib.redirect_stdout(io.StringIO()):
        exit_code = run.main()
    result = run.read(out / "RESULT.json")
    assert run.read(out / "RESTORATION.json") == result
    if case == "success":
        assert exit_code == 0 and result["status"].startswith("COMPLETED")
        assert len(all_commands) == 8 and len(result["stages"]) == 3
    else:
        assert exit_code == 1 and not result["status"].startswith("COMPLETED")
    if case in ("unsafe-lifecycle", "concurrent-source-change"):
        assert "restoration_error" in result
        assert "restored-build" not in [r["label"] for r in all_commands]
        if case == "concurrent-source-change":
            assert (root / run.SOURCES[0]).read_text() == "independent concurrent change"
    else:
        assert all((root / name).read_bytes() == content for name, content in originals.items())
    if case == "partial-install":
        assert failed_install and result["build_restored"]
    return dict(case=case, exit=exit_code, status=result["status"],
                commands=[row["label"] for row in all_commands],
                source_restored=result.get("source_restored", False),
                restoration_error=result.get("restoration_error"),
                mock_only=True)


def main():
    with tempfile.TemporaryDirectory(prefix="grid-bundle-transaction-check-") as tmp:
        scratch = Path(tmp)
        results = [exercise(case, scratch) for case in CASES]
    assert not scratch.exists()
    result = dict(status="PASS mocked transaction/restoration checks", cases=results,
                  scratch_removed=True, native_commands_executed=0)
    run.save(HERE / "FAILURE-CHECK.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
