import ast
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for name, digest in json.loads((HERE / "PARENTS.json").read_text()).items():
        assert sha(Path(name)) == digest
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text())
    author = BASE / "css-grid-baseline-grid-bundle-candidate-20261112-v1"
    followup = BASE / "css-grid-baseline-grid-bundle-provider-followup-preparation-20261112-v2"
    correct = BASE / "css-grid-baseline-grid-bundle-validation-plan-20261112-v1"
    assert (HERE / "parse.py").read_bytes() == (followup / "work_parse.py").read_bytes()
    assert (HERE / "process.py").read_bytes() == (correct / "process.py").read_bytes()
    assert (HERE / "BUNDLE.patch").read_bytes() == (author / "CHANGES.patch").read_bytes()
    assert (HERE / "WORK.patch").read_bytes() == (followup / "work/DIAGNOSTIC.patch").read_bytes()
    for path in (HERE / "fixtures").iterdir():
        assert path.read_bytes() == (followup / "work-fixtures" / path.name).read_bytes()
    for name in ("FOCUSED.json", "EXPECTED-FOCUSED.json", "EXPECTED-ALIGNMENT.json"):
        assert (HERE / name).read_bytes() == (correct / name).read_bytes()
    configs = json.loads((HERE / "CONFIGS.json").read_text())
    source_configs = json.loads((BASE / "css-grid-baseline-measurement-work-trace-plan-20261112-v2/SCENARIOS.json").read_text())["initial"]
    assert configs == source_configs and len(configs) == 4
    predecessor = BASE / "css-grid-baseline-grid-bundle-work-execution-template-20261112-v1"
    for name in ("demand", "bundle", "instrumented", "fixtures"):
        old_files = {str(x.relative_to(predecessor / name)): x.read_bytes() for x in (predecessor / name).rglob("*") if x.is_file()}
        new_files = {str(x.relative_to(HERE / name)): x.read_bytes() for x in (HERE / name).rglob("*") if x.is_file()}
        assert old_files == new_files
    for name in ("CONFIGS.json", "BUNDLE.patch", "WORK.patch", "AUTHORIZATION-TEMPLATE.json", "parse.py", "observations.py", "process.py"):
        assert (HERE / name).read_bytes() == (predecessor / name).read_bytes()
    commands = []
    with tempfile.TemporaryDirectory(prefix="grid-work-source-") as tmp:
        scratch = Path(tmp)
        shutil.copytree(HERE / "demand", scratch, dirs_exist_ok=True)
        for patch, reverse, side in [("BUNDLE.patch", False, "bundle"), ("WORK.patch", False, "instrumented"),
                                      ("WORK.patch", True, "bundle"), ("BUNDLE.patch", True, "demand")]:
            argv = ["/usr/bin/patch", "--batch", "-p1"] + (["-R"] if reverse else [])
            result = subprocess.run(argv, cwd=scratch, input=(HERE / patch).read_bytes(), capture_output=True)
            commands.append(dict(patch=patch, argv=argv, exit=result.returncode, stdout=result.stdout.decode(), stderr=result.stderr.decode()))
            assert result.returncode == 0
            for path in (HERE / side).rglob("*"):
                if path.is_file():
                    assert path.read_bytes() == (scratch / path.relative_to(HERE / side)).read_bytes()
    assert not scratch.exists()
    assert json.loads((HERE / "AUTHORITY-PENDING.json").read_text())["ready"] is False
    assert json.loads((HERE / "AUTHORIZATION-TEMPLATE.json").read_text())["authorized"] is False
    result = dict(status="PASS source-only template checks", patch_commands=commands, scratch_removed=True,
                  configs=4, flushes_per_config=29, planned_commands=18, authority_bound=False,
                  compiler_browser_commands_executed=0)
    (HERE / "SOURCE-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
