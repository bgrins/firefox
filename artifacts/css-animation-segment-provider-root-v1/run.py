import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ORACLE = ROOT / "artifacts/css-animation-segment-provider-oracle-v1"
TEST = "testing/web-platform/tests/css/css-values/animation-segment-mixed-iteration-probe.html"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


assert sha(ORACLE / "INPUTS.json") == "c80d4acb5b1f2907943998590423d89a1ad866906a55c59161df86ad848e04da"
inputs = json.loads((ORACLE / "INPUTS.json").read_text())
for name, digest in inputs.items():
    assert sha(ORACLE / name) == digest, name
prior = json.loads((ROOT / "artifacts/css-animation-interpolation-taint-paired-root-v1/PAIR.json").read_text())
assert prior["complete"] and prior["stable_after"]
pins = prior["pins_after"].copy()
landing = "testing/web-platform/tests/css/css-values/registered-number-interpolation-attr-taint.html"
assert pins[landing] == "c48a34cac0e4afce1bc52fb6f0614db057c0150a63e771863fe655705a6313e4"
pins[landing] = "5d4b616f048f17ac8a7cd1bdc56b15a4a7854eb20333fdfc52f6d33203dcf2cd"
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
assert not (ROOT / TEST).exists()
metadata = (ROOT / TEST.replace("/tests/", "/meta/")).with_suffix(".html.ini")
assert not metadata.exists()
(ROOT / TEST).write_bytes((ORACLE / "probe.html").read_bytes())
(HERE / "probe.html").write_bytes((ORACLE / "probe.html").read_bytes())
pins[TEST] = inputs["probe.html"]
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(HERE / "raw.json"), TEST]
record = {"phase": "running", "pins": pins, "command": command,
          "oracle_inputs_sha256": sha(ORACLE / "INPUTS.json"),
          "scope": "Unchanged fix80 candidate binaries and shared tree; no build or native mutation.",
          "prior_help_transfer": "css-animation-interpolation-taint-final-root-v1/HELP-LINK-TRANSFER.json",
          "expected_subtests": 18, "expected_status": "PASS"}
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
assert len(rows) == 18 and len({r["subtest"] for r in rows}) == 18
assert len(ends) == 1 and ends[0]["status"] == "OK" and record["suite_ends"] == 1
print(json.dumps({"exit": status, "statuses": {s: sum(r["status"] == s for r in rows)
      for s in {r["status"] for r in rows}},
      "failures": [r for r in rows if r["status"] != "PASS"]}, indent=2))
