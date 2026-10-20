import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
paths = ["dom/animation/KeyframeEffect.cpp",
         "testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html"]


def pin():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}


before = pin()
results = []
for name, command in [("format", ["./mach", "format", "--path", *paths]),
                      ("lint", ["./mach", "lint", *paths])]:
    with (HERE / (name + ".log")).open("w") as stream:
        status = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode
    results.append({"command": command, "exit": status})
    (HERE / "FORMAT-LINT.json").write_text(json.dumps({"before": before, "after": pin(), "commands": results}, indent=2) + "\n")
    assert status == 0 and pin() == before, name
print("Format and lint exit 0; source bytes unchanged")
