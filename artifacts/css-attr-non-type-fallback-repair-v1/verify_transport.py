import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
pins = json.loads((here / "SOURCE-PINS.json").read_text())
wpt = (here / "WPT-PATH.txt").read_text().strip()
report = {}
for role in ("head", "live"):
    with tempfile.TemporaryDirectory(prefix="attr-fallback-transport-", dir="/private/tmp") as directory:
        work = Path(directory)
        for name in pins["paths"]:
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(here / ("base-" + role) / name, destination)
        patch = here / "fix-head.patch"
        commands = []
        for arguments in (["--check"], [], ["--reverse", "--check"], ["--reverse"], []):
            command = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                       "apply", *arguments, str(patch)]
            result = subprocess.run(command, cwd=work, text=True, capture_output=True)
            commands.append({"arguments": arguments, "exit": result.returncode,
                             "stdout": result.stdout, "stderr": result.stderr})
            assert result.returncode == 0, commands[-1]
            if arguments in ([], ["--reverse"]):
                candidate = not arguments
                expected = set(pins["paths"]) | ({wpt} if candidate else set())
                actual = {str(path.relative_to(work)) for path in work.rglob("*") if path.is_file()}
                assert actual == expected, (actual, expected)
                for name in expected:
                    wanted = here / (("candidate-" if candidate else "base-") + role) / name
                    assert (work / name).read_bytes() == wanted.read_bytes(), name
        report[role] = {"commands": commands, "exact_postimage": True,
                        "reverse_restores_exact_preimage": True,
                        "scratch": str(work)}
    report[role]["scratch_removed"] = not work.exists()
print(json.dumps(report, indent=2))
