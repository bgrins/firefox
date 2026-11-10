import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Use python3 -I without -O")
    output = HERE / sys.argv[1]
    output.mkdir()
    toolchain = json.loads((HERE / "TOOLCHAIN.json").read_text())
    for path, digest in toolchain.items():
        assert sha(ROOT / path) == digest
    lean = ROOT / next(path for path in toolchain if path.endswith("/bin/lean"))
    references = json.loads((HERE / "REFERENCES.json").read_text())
    old = "artifacts/css-animation-obligation-conservation-20261110-v1/Obligations.lean"
    assert sha(HERE / "Accounting.lean") == references[old]["sha256"]
    names = re.findall(r"^theorem (\w+)", (HERE / "Renewal.lean").read_text(), re.M)
    with tempfile.TemporaryDirectory(prefix="css-drain-contract-") as directory:
        scratch = Path(directory)
        env = dict(os.environ, LEAN_PATH=directory)
        commands = []

        def run(name, success):
            command = [
                str(lean),
                "-o",
                str(scratch / (name + ".olean")),
                str(scratch / (name + ".lean")),
            ]
            result = subprocess.run(
                command,
                cwd=scratch,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            log = result.stdout + result.stderr
            (output / (name + ".log")).write_text(log)
            commands.append({"command": command, "exit_code": result.returncode})
            if success:
                assert (
                    result.returncode == 0
                    and "warning:" not in log
                    and "error:" not in log
                ), log
            else:
                assert result.returncode != 0 and log.count("error:") == 1
                assert (
                    "Tactic `decide` proved that the proposition" in log
                    and "is false" in log
                    and "warning:" not in log
                ), log
            return log

        for name in ["Accounting", "Renewal"]:
            shutil.copy2(HERE / (name + ".lean"), scratch / (name + ".lean"))
            run(name, True)
        (scratch / "Audit.lean").write_text(
            "import Renewal\n"
            + "\n".join("#print axioms DrainProgressContract." + name for name in names)
            + "\n"
        )
        audit = run("Audit", True)
        assert all("DrainProgressContract." + name in audit for name in names)
        for axioms in re.findall(r"depends on axioms: \[(.*?)\]", audit, re.S):
            assert set(axioms.replace("\n", " ").replace(" ", "").split(",")) <= {
                "propext",
                "Quot.sound",
                "Classical.choice",
            }
        controls = {
            "SameRankRenewal": "(key 1).lifetime < (key 0).lifetime",
            "ReadyPreventsRenewal": "settled (request (completed 1) (key 1)) (key 1) = true",
        }
        for name, claim in controls.items():
            (scratch / (name + ".lean")).write_text(
                "import Renewal\nopen AnimationObligations DrainProgressContract\n"
                + "example : "
                + claim
                + " := by decide +kernel\n"
            )
            run(name, False)
    assert not scratch.exists()
    (output / "RESULT.json").write_text(
        json.dumps(
            {
                "source_hashes": {
                    name: sha(HERE / name)
                    for name in ["Accounting.lean", "Renewal.lean", "check.py"]
                },
                "theorems": names,
                "negative_controls": list(controls),
                "commands": commands,
                "scratch_removed": True,
                "native_execution": False,
                "claim": "Counterexample: conserved installed fresh generations can renew forever at one native identity",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"{len(names)} theorem audits and {len(controls)} false controls passed")


if __name__ == "__main__":
    main()
