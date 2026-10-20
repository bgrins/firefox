import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TEST = "testing/web-platform/tests/css/css-properties-values-api/registered-token-boundaries.html"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


prior = json.loads((ROOT / "artifacts/css-animation-segment-provider-root-v1/RUN.json").read_text())
assert prior["phase"] == "done" and prior["exit"] == 0 and prior["stable"]
pins = prior["pins"].copy()
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
assert not (ROOT / TEST).exists()
metadata = (ROOT / TEST.replace("/tests/", "/meta/")).with_suffix(".html.ini")
assert not metadata.exists()
(ROOT / TEST).write_bytes((HERE / "probe.html").read_bytes())
pins[TEST] = sha(HERE / "probe.html")
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(HERE / "raw.json"), TEST]
record = {"phase": "running", "pins": pins, "command": command,
          "scope": "Unchanged fix80 candidate; expanded token-boundary oracle with font, margin, and token serialization controls.",
          "expected_subtests": 37}
(HERE / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
with (HERE / "wpt.log").open("w") as log:
    status = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode
raw = [json.loads(line) for line in (HERE / "raw.json").read_text().splitlines()]
rows = [r for r in raw if r.get("action") == "test_status"]
ends = [r for r in raw if r.get("action") == "test_end"]
stable = all(sha(ROOT / name) == digest for name, digest in pins.items())
record.update(phase="done", exit=status, rows=rows, harness=ends, stable=stable,
              metadata_absent=not metadata.exists(),
              suite_ends=sum(r.get("action") == "suite_end" for r in raw))
(HERE / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
assert stable and not metadata.exists()
assert len(rows) == 37 and len({r["subtest"] for r in rows}) == 37
assert len(ends) == 1 and ends[0]["status"] == "OK" and record["suite_ends"] == 1
print(json.dumps({"exit": status, "statuses": {s: sum(r["status"] == s for r in rows)
      for s in {r["status"] for r in rows}},
      "failures": [r for r in rows if r["status"] != "PASS"]}, indent=2))
