import ast
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
AUTHOR = ROOT / "artifacts/css-grid-baseline-grid-bundle-candidate-20261112-v1"
PRIOR = ROOT / "artifacts/css-grid-baseline-demand-snapshot-native-20261112-v1"


def main():
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text())
    for name, digest in run.read(HERE / "PARENTS.json").items():
        assert run.sha(name) == digest, name
    for name, row in run.read(HERE / "TOOL-PINS.json").items():
        assert str(Path(name).resolve()) == row["resolved"]
        assert run.sha(name) == row["sha256"]
    for name, digest in run.read(HERE / "LIVE-PINS.json").items():
        assert run.sha(ROOT / name) == digest, name
    for name, row in run.read(HERE / "BINARY-AUTHORITY.json").items():
        assert run.sha(name) == row["sha256"]
        assert Path(name).stat().st_size == row["bytes"]
    assert (HERE / "process.py").read_bytes() == (ROOT / "artifacts/css-grid-baseline-measurement-work-completion-plan-20261112-v1/process.py").read_bytes()
    for side in ("original", "candidate"):
        for name in run.SOURCES:
            assert (HERE / side / name).read_bytes() == (AUTHOR / side / name).read_bytes()
    assert (HERE / "CHANGES.patch").read_bytes() == (AUTHOR / "CHANGES.patch").read_bytes()
    for local, prior in (("EXPECTED-FOCUSED.json", "candidate-regression-wptreport.json"),
                         ("EXPECTED-ALIGNMENT.json", "candidate-alignment-wptreport.json")):
        assert (HERE / local).read_bytes() == (PRIOR / prior).read_bytes()
    focused = run.read(HERE / "EXPECTED-FOCUSED.json")
    alignment = run.read(HERE / "EXPECTED-ALIGNMENT.json")
    assert len(focused["results"]) == 3
    assert sum(len(item["subtests"]) for item in focused["results"]) == 700
    assert len(alignment["results"]) == 457
    assert len(run.outcomes(alignment)) == 2947
    for name, row in run.read(HERE / "FOCUSED.json").items():
        assert run.sha(ROOT / name) == run.sha(HERE / row["fixture"]) == row["sha256"]
        result = next(item for item in focused["results"] if Path(item["test"]).name == Path(name).name)
        assert len(result["subtests"]) == row["subtests"]
    assert run.read(HERE / "AUTHORIZATION-TEMPLATE.json")["authorized"] is False
    commands = []
    with tempfile.TemporaryDirectory(prefix="grid-bundle-correctness-patch-") as tmp:
        scratch = Path(tmp)
        shutil.copytree(HERE / "original", scratch, dirs_exist_ok=True)
        for reverse, expected in ((False, "candidate"), (True, "original")):
            argv = ["/usr/bin/patch", "-p1", "--batch"]
            if reverse:
                argv.append("-R")
            argv += ["-i", str(HERE / "CHANGES.patch")]
            completed = subprocess.run(argv, cwd=scratch, capture_output=True, text=True)
            commands.append(dict(argv=argv, exit=completed.returncode,
                                 stdout=completed.stdout, stderr=completed.stderr))
            assert completed.returncode == 0
            for name in run.SOURCES:
                assert (scratch / name).read_bytes() == (HERE / expected / name).read_bytes()
    assert not scratch.exists()
    failure = run.read(HERE / "FAILURE-CHECK.json")
    assert failure["status"].startswith("PASS") and len(failure["cases"]) == 13
    assert failure["scratch_removed"] and failure["native_commands_executed"] == 0
    result = dict(status="PASS correctness preparation source and patch checks",
                  live_pins=517, tool_pins=5, native_changed_files=3,
                  focused_subtests=700, alignment_files=457, alignment_outcomes=2947,
                  patch_commands=commands, mock_transaction_cases=13,
                  scratch_removed=True, compiler_browser_or_native_install=False)
    run.save(HERE / "SOURCE-CHECK.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
