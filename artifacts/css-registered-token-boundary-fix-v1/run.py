import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = "servo/components/style/properties_and_values/value.rs"
TEST = "testing/web-platform/tests/css/css-properties-values-api/registered-token-boundaries.html"

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def read(path):
    return json.loads(path.read_text())

def run(command, path):
    with path.open("w") as output:
        return subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
          env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode

baseline = read(ROOT / "artifacts/css-registered-token-boundary-expanded-v2/RUN.json")
assert baseline["phase"] == "done" and baseline["stable"] and baseline["metadata_absent"]
assert len(baseline["rows"]) == 37 and sum(r["status"] == "FAIL" for r in baseline["rows"]) == 10
pins = baseline["pins"].copy()
assert sha(HERE / "source/value.original.rs") == pins[SOURCE]
for name, digest in pins.items():
    if name != SOURCE:
        assert sha(ROOT / name) == digest, name
record = {"phase": "formatting", "complete": False, "baseline": "../css-registered-token-boundary-expanded-v2/RUN.json",
          "baseline_record_sha256": sha(ROOT / "artifacts/css-registered-token-boundary-expanded-v2/RUN.json"),
          "pins_before": pins.copy(), "scope": "Shared fix80 local tree; only typed serialization boundary construction changes."}
def save():
    (HERE / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
save()
command = ["./mach", "format", "--path", SOURCE]
status = run(command, HERE / "format.log")
record["format"] = {"command": command, "exit": status}; save()
assert status == 0
pins[SOURCE] = sha(ROOT / SOURCE)
(HERE / "source/value.candidate.rs").write_bytes((ROOT / SOURCE).read_bytes())
record.update(phase="building", candidate_source_sha256=pins[SOURCE]); save()
command = ["./mach", "build", "binaries"]
status = run(command, HERE / "build.log")
record["build"] = {"command": command, "exit": status}; save()
assert status == 0
for name in pins:
    if name.startswith("objdir-full.noindex/dist/Nightly.app/Contents/MacOS/"):
        pins[name] = sha(ROOT / name)
assert all(sha(ROOT / name) == digest for name, digest in pins.items())
record.update(phase="testing", pins_after=pins.copy()); save()
previous = read(ROOT / "artifacts/css-animation-interpolation-taint-paired-root-v1/PAIR.json")
segment = read(ROOT / "artifacts/css-animation-segment-provider-root-v1/RUN.json")
tests = [arg for arg in previous["candidate"]["command"] if arg.startswith("testing/")]
tests += [arg for arg in segment["command"] if arg.startswith("testing/")] + [TEST]
assert len(tests) == len(set(tests)) == 18
command = ["./mach", "wpt", "--headless", "--processes=1",
 "--setpref=layout.css.properties-and-values.enabled=true", "--log-raw=" + str(HERE / "raw.json"), *tests]
status = run(command, HERE / "wpt.log")
raw = [json.loads(line) for line in (HERE / "raw.json").read_text().splitlines()]
rows = [r for r in raw if r.get("action") == "test_status"]
ends = [r for r in raw if r.get("action") == "test_end"]
key = lambda r: (r["test"], r["subtest"])
before = {key(r): r["status"] for r in previous["candidate"]["rows"] + segment["rows"] + baseline["rows"]}
after = {key(r): r["status"] for r in rows}
stable = all(sha(ROOT / name) == digest for name, digest in pins.items())
record.update(phase="done", command=command, exit=status, rows=rows, harness=ends, stable=stable,
 changes=[{"identity": list(k), "before": before[k], "after": after.get(k)} for k in before if before[k] != after.get(k)])
record["complete"] = (status == 0 and len(before) == len(after) == len(rows) == 308 and before.keys() == after.keys()
 and all(r["status"] == "PASS" for r in rows) and len(ends) == 18 and all(r["status"] == "OK" for r in ends)
 and sum(r.get("action") == "suite_end" for r in raw) == 1 and stable)
save()
print(json.dumps({"complete": record["complete"], "exit": status, "statuses": {s: sum(r["status"] == s for r in rows) for s in {r["status"] for r in rows}},
 "failures": [r for r in rows if r["status"] != "PASS"], "changes": record["changes"]}, indent=2))
assert record["complete"]
