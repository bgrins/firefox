import hashlib
import json
from pathlib import Path
import subprocess

r = Path(__file__).resolve().parent
repo = r.parent.parent
m = json.loads((r / "SOURCES.json").read_text())
for path, expected in m["files"].items():
    data = (r / "source" / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    assert data == subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", m["revision"] + ":" + path], cwd=repo)
for record in json.loads((r / "INPUT-ORIGINS.json").read_text()).values():
    assert hashlib.sha256((r / record["copy"]).read_bytes()).hexdigest() == record["sha256"]
rows = json.loads((r / "FAILURES.json").read_text())
assert len(rows) == 11
for row in rows:
    meta = r / "source/testing/web-platform/meta" / (row["test"].lstrip("/") + ".ini")
    assert "  [" + row["subtest"] + "]\n    expected: FAIL" in meta.read_text()
print(json.dumps({"result": "PASS", "pinned_files": len(m["files"]), "exact_expected_failures": len(rows), "new_bug_count": 0}))
