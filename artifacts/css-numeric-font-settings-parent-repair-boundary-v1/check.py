import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for name, record in json.loads((HERE / "REFERENCES.json").read_text()).items():
    data = (ROOT / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == record["sha256"]
    assert len(data) == record["bytes"]
source = json.loads((HERE / "SOURCE.json").read_text())
count = 0
for record in source["sources"]:
    data = (ROOT / record["path"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == record["sha256"]
    lines = data.decode().splitlines(keepends=True)
    for excerpt in record["excerpts"]:
        assert "".join(lines[excerpt["first"] - 1:excerpt["last"]]) == excerpt["text"]
        count += 1
print(json.dumps({"references": 6, "source_files": len(source["sources"]),
                  "exact_excerpts": count, "native_implementation": False,
                  "browser_executed": False}))
