import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NATIVE = "servo/components/style/custom_properties.rs"
TEST = "testing/web-platform/tests/css/css-values/attr-taint-touching-url-boundary.html"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


pair_path = ROOT / "artifacts/css-custom-properties-map-taint-root-v1/paired/PAIR.json"
pair = read(pair_path)
baseline = read(HERE / "RUN.json")
assert pair["complete"] and pair["candidate_binary_validated"] and baseline["stable_after"]
assert [r["status"] for r in baseline["rows"]] == ["FAIL", "FAIL", "PASS", "PASS", "PASS", "PASS", "PASS"]
pins = {**pair["stable_pins"], **pair["source_pins"]["candidate"], TEST: digest(HERE / "test.html")}
for name, pin in pins.items():
    assert digest(ROOT / name) == pin, name
binaries = ROOT / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS"
for name, pin in pair["final_binaries"].items():
    assert digest(binaries / name) == pin, name

candidate = ROOT / "artifacts/css-attr-taint-range-proof-v1/source/candidate/custom_properties.rs"
assert pins[NATIVE] == "757f4f19f5fbd463afa7f93844a4139ef86865440517eee6088dc576ac4b6f22"
assert digest(candidate) == "18b61124b705887b6a103c015bfedec7bfdea63873248e067701c6097c90e56f"
out = HERE / "candidate"
out.mkdir(exist_ok=False)
record = {"baseline_receipt_sha256": digest(HERE / "RUN.json"),
          "prior_82_pair_sha256": digest(pair_path), "original_pins": pins.copy(),
          "baseline_binaries": pair["final_binaries"], "driver_sha256": digest(Path(__file__)),
          "complete": False, "scope": "Shared local tree. Reused validated baseline binaries and separate 82-case/7-case receipts; no isolated upstream runtime."}
(ROOT / NATIVE).write_bytes(candidate.read_bytes())
pins[NATIVE] = digest(candidate)
record["candidate_pins"] = pins


def stable():
    return all(digest(ROOT / name) == pin for name, pin in pins.items())


def save():
    (out / "RESULT.json").write_text(json.dumps(record, indent=2) + "\n")


def run(command, filename):
    with (out / filename).open("w") as log:
        return subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                              env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode


save()
build = ["./mach", "build", "binaries"]
record["build"] = {"command": build, "exit": run(build, "build.log"), "sources_stable": stable()}
record["candidate_binaries"] = {name: digest(binaries / name) for name in pair["final_binaries"]}
save()
assert record["build"]["exit"] == 0 and record["build"]["sources_stable"]
assert record["candidate_binaries"]["XUL"] != record["baseline_binaries"]["XUL"]
command = [a for a in pair["phases"][-1]["command"] if not a.startswith("--log-raw=")]
command.insert(5, "--log-raw=" + str(out / "raw.json"))
command.append(TEST)
record["wpt"] = {"command": command, "exit": run(command, "wpt.log")}
events = [json.loads(line) for line in (out / "raw.json").read_text().splitlines()]
rows = [e for e in events if e.get("action") == "test_status"]
ends = [e for e in events if e.get("action") == "test_end"]
prior_events = [json.loads(line) for line in (pair_path.parent / "candidate/raw.json").read_text().splitlines()]
expected = {(e["test"], e["subtest"]) for e in prior_events if e.get("action") == "test_status"}
expected |= {(e["test"], e["subtest"]) for e in baseline["rows"]}
actual = [(e["test"], e["subtest"]) for e in rows]
suite = [i for i, e in enumerate(events) if e.get("action") == "suite_end"]
record.update(rows=rows, harness=ends, source_stable_after=stable(),
              binary_stable_after=all(digest(binaries / n) == h for n, h in record["candidate_binaries"].items()),
              exact_identities=len(actual) == len(expected) == 89 and set(actual) == expected,
              suite_end_positions=suite)
record["complete"] = (record["wpt"]["exit"] == 0 and record["exact_identities"]
                      and all(e["status"] == "PASS" for e in rows)
                      and len(ends) == 10 and all(e["status"] == "OK" for e in ends)
                      and record["source_stable_after"] and record["binary_stable_after"]
                      and len(suite) == 1 and max(i for i, e in enumerate(events)
                          if e.get("action") in {"test_status", "test_end"}) < suite[0])
save()
assert record["complete"]
print("Candidate: 89 PASS, 10 harnesses OK; sources and binaries stable")
