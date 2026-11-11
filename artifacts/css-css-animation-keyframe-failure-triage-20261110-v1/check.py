import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "FILES.json").read_text())
for name, expected in manifest.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
sources = json.loads((ROOT / "SOURCES.json").read_text())
for name, expected in sources["files"].items():
    data = subprocess.check_output(
        ["git", "-c", "core.fsmonitor=false", "show", sources["revision"] + ":" + name],
        cwd=ROOT,
    )
    assert hashlib.sha256(data).hexdigest() == expected, name
    assert (ROOT / "source" / name).read_bytes() == data, name
observations = json.loads((ROOT / "BASELINE.json").read_text())
assert len(observations["failures"]) == 3
assert all(row["status"] == "FAIL" for row in observations["failures"])
anchors = json.loads((ROOT / "ANCHORS.json").read_text())
assert len(anchors) == 7
assert all(row["status"] == "fulfilled" and row["value"]["exit_code"] == 0 for row in anchors)
print(f"PASS: {len(manifest)} frozen files, {len(sources['files'])} Git source objects, three baseline failures, seven anchors")
