import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / "artifacts/css-custom-properties-animation-taint-repair-v1"
FILES = ["dom/animation/KeyframeEffect.cpp",
         "servo/components/style/properties_and_values/value.rs",
         "servo/ports/geckolib/glue.rs"]
TYPED = "testing/web-platform/tests/css/css-values/animation-equal-payload-taint.html"
CSSWIDE = "testing/web-platform/tests/css/css-values/animation-csswide-equal-payload-taint.html"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


assert digest(PROPOSAL / "FREEZE.json") == "15000e7ba5e31072934bd59ab124d18d0876082b5e62e578531eb0d9dfabdde5"
assert digest(PROPOSAL / "MANIFEST.json") == "ad253012e5c2aab47932b163508241d6103271c18d6f352b914a682d93cd0e40"
manifest = read(PROPOSAL / "MANIFEST.json")
for name, pin in manifest.items():
    assert digest(PROPOSAL / name) == pin, name

association = ROOT / "artifacts/css-attr-taint-touching-ranges-final-root-v1/candidate/RESULT.json"
prior = read(association)
wide_path = ROOT / "artifacts/css-animation-csswide-taint-root-v1/RUN.json"
wide = read(wide_path)
assert prior["complete"] and wide["stable_after"]
pins = {**prior["candidate_pins"],
        **{name: manifest["source/original/" + name] for name in FILES},
        TYPED: manifest["typed-endpoint-taint.html"],
        CSSWIDE: manifest["csswide-endpoint-taint.html"]}
for name, pin in pins.items():
    assert digest(ROOT / name) == pin, name
binary_dir = ROOT / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS"
for name, pin in prior["candidate_binaries"].items():
    assert digest(binary_dir / name) == pin
    assert wide["pins"][str(binary_dir.relative_to(ROOT) / name)] == pin
assert [r["status"] for r in wide["rows"]] == ["FAIL", "PASS", "PASS", "FAIL", "PASS", "PASS"]
old_typed = read(ROOT / "artifacts/css-custom-properties-animation-taint-root-v1/RUN.json")
record = {"phase": "baseline", "complete": False, "driver_sha256": digest(Path(__file__)),
          "range_association_sha256": digest(association), "wide_receipt_sha256": digest(wide_path),
          "original_pins": pins.copy(), "baseline_binaries": prior["candidate_binaries"],
          "scope": "Combined local tree; joined 89-case and CSS-wide6 baselines on identical binaries, plus fresh typed6. Standalone upstream not executed."}


def save():
    (HERE / "PAIR.json").write_text(json.dumps(record, indent=2) + "\n")


def stable():
    return all(digest(ROOT / name) == pin for name, pin in pins.items())


def run(command, log):
    with log.open("w") as stream:
        return subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                              env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode


def collect(folder):
    raw = events(folder / "raw.json")
    rows = [e for e in raw if e.get("action") == "test_status"]
    ends = [e for e in raw if e.get("action") == "test_end"]
    suite = [i for i, e in enumerate(raw) if e.get("action") == "suite_end"]
    assert len(suite) == 1 and max(i for i, e in enumerate(raw)
        if e.get("action") in {"test_status", "test_end"}) < suite[0]
    return rows, ends


typed = HERE / "typed-baseline"
typed.mkdir(exist_ok=False)
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(typed / "raw.json"), TYPED]
save()
record["typed_baseline"] = {"command": command, "exit": run(command, typed / "wpt.log")}
typed_rows, typed_ends = collect(typed)
record["typed_baseline"].update(rows=typed_rows, harness=typed_ends, sources_stable=stable())
save()
assert [e["subtest"] for e in typed_rows] == [e["subtest"] for e in old_typed["rows"]]
assert [e["status"] for e in typed_rows] == ["FAIL", "PASS", "PASS", "FAIL", "PASS", "PASS"]
assert all("Updated effect URL taint" in e.get("message", "") for e in typed_rows if e["status"] == "FAIL")
assert len(typed_ends) == 1 and typed_ends[0]["status"] == "OK" and stable()
assert all(digest(binary_dir / n) == h for n, h in record["baseline_binaries"].items())

for name in FILES:
    assert digest(ROOT / name) == pins[name]
    (ROOT / name).write_bytes((PROPOSAL / "source/candidate" / name).read_bytes())
    pins[name] = manifest["source/candidate/" + name]
record.update(phase="building", candidate_pins=pins.copy())
save()
candidate = HERE / "candidate"
candidate.mkdir(exist_ok=False)
command = ["./mach", "build", "binaries"]
record["build"] = {"command": command, "exit": run(command, candidate / "build.log"),
                   "sources_stable": stable()}
record["candidate_binaries"] = {name: digest(binary_dir / name) for name in record["baseline_binaries"]}
save()
assert record["build"]["exit"] == 0 and record["build"]["sources_stable"]
assert record["candidate_binaries"]["XUL"] != record["baseline_binaries"]["XUL"]

command = [a for a in prior["wpt"]["command"] if not a.startswith("--log-raw=")]
command.insert(5, "--log-raw=" + str(candidate / "raw.json"))
command.extend([TYPED, CSSWIDE])
record["phase"] = "candidate-wpt"
save()
record["candidate_wpt"] = {"command": command, "exit": run(command, candidate / "wpt.log")}
rows, ends = collect(candidate)
record["candidate_wpt"].update(rows=rows, harness=ends)
baseline = prior["rows"] + wide["rows"] + typed_rows
key = lambda e: (e["test"], e["subtest"])
before, after = {key(e): e["status"] for e in baseline}, {key(e): e["status"] for e in rows}
record["exact_identities"] = len(rows) == len(baseline) == len(before) == len(after) == 101 and before.keys() == after.keys()
record["changes"] = [{"test": k[0], "subtest": k[1], "before": before[k], "after": after.get(k)}
                     for k in before if before[k] != after.get(k)]
record["sources_stable_after"] = stable()
record["binaries_stable_after"] = all(digest(binary_dir / n) == h for n, h in record["candidate_binaries"].items())
record["complete"] = (record["exact_identities"] and len(ends) == 12
                      and all(e["status"] == "OK" for e in ends)
                      and all(e["status"] == "PASS" for e in rows)
                      and record["candidate_wpt"]["exit"] == 0
                      and record["sources_stable_after"] and record["binaries_stable_after"])
record["phase"] = "done"
save()
assert record["complete"]
print("101 PASS, 12 harnesses OK; source and binary pins stable")
