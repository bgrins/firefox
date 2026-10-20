import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TEST = "testing/web-platform/tests/css/css-values/animation-interpolation-attribute-taint-probe.html"
PROBE = ROOT / "artifacts/css-animation-interpolation-taint-oracle-v1/probe.html"

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

prior = json.loads((ROOT / "artifacts/css-animation-base-metadata-paired-root-v1/PAIR.json").read_text())
assert prior["complete"]
pins = prior["pins_after"].copy()
assert all(sha(ROOT / name) == digest for name, digest in pins.items())
assert not (ROOT / TEST).exists()
assert not (ROOT / TEST.replace("/tests/", "/meta/")).with_suffix(".html.ini").exists()
(ROOT / TEST).write_bytes(PROBE.read_bytes())
(HERE / "probe.html").write_bytes(PROBE.read_bytes())
pins[TEST] = sha(ROOT / TEST)
pins[str(PROBE.relative_to(ROOT))] = sha(PROBE)
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(HERE / "raw.json"), TEST]
record = {"phase":"running", "pins":pins, "command":command,
          "scope":"Current shared-tree fix79 candidate binaries; no native changes or new build.",
          "expected_subtests":40,"diagnostic_boundary_cases":2}
(HERE / "RUN.json").write_text(json.dumps(record,indent=2)+"\n")
with (HERE / "wpt.log").open("w") as log:
    status = subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                            env={**os.environ,"MOZ_SKIP_PATH_PERFORMANCE_CHECK":"1"}).returncode
raw = [json.loads(line) for line in (HERE / "raw.json").read_text().splitlines()]
rows = [r for r in raw if r.get("action")=="test_status"]
ends = [r for r in raw if r.get("action")=="test_end"]
stable = all(sha(ROOT / name)==digest for name,digest in pins.items())
record.update(phase="done",exit=status,rows=rows,harness=ends,stable=stable,
              suite_ends=sum(r.get("action")=="suite_end" for r in raw))
(HERE / "RUN.json").write_text(json.dumps(record,indent=2)+"\n")
assert stable and len(rows)==40 and len(ends)==1 and ends[0]["status"]=="OK" and record["suite_ends"]==1
print(json.dumps({"exit":status,"statuses":{s:sum(r["status"]==s for r in rows) for s in {r["status"] for r in rows}},"failures":[r for r in rows if r["status"]!="PASS"]},indent=2))
