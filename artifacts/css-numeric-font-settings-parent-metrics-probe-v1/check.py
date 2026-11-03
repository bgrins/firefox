import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

for name, record in json.loads((HERE / "REFERENCES.json").read_text()).items():
    data = (ROOT / name).read_bytes()
    assert len(data) == record["bytes"]
    assert hashlib.sha256(data).hexdigest() == record["sha256"]

source_map = json.loads((HERE / "SOURCE-MAP.json").read_text())
for source in source_map["sources"]:
    data = (ROOT / source["path"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == source["sha256"]
    lines = data.decode().splitlines(keepends=True)
    for excerpt in source["excerpts"]:
        assert "".join(lines[excerpt["first"] - 1:excerpt["last"]]) == excerpt["text"]

for index in range(1, 7):
    assert json.loads((HERE / "evidence" / f"ANCHOR-{index}.log").read_text())["exists"] is True

subprocess.run(["node", "--check", str(HERE / "probe.js")], check=True)
print(json.dumps({"source_files": len(source_map["sources"]), "references": 4,
                  "valid_anchors": 6, "javascript_syntax": "passed",
                  "browser_executed": False, "native_executed": False}))
