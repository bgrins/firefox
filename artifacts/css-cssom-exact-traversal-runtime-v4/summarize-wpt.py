import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires python3 -I -S without optimization")
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
runs = {}
for phase in ["baseline", "candidate"]:
    raw = [json.loads(line) for line in (ROOT / phase / "raw.json").read_text().splitlines()]
    record = json.loads((ROOT / phase / "RUN.json").read_text())
    assert record["rows"] == [e for e in raw if e.get("action") == "test_status"]
    assert record["ends"] == [e for e in raw if e.get("action") == "test_end"]
    assert sum(e.get("action") == "suite_end" for e in raw) == 1
    assert record["complete"] and record["before"] == record["after"]
    assert len(record["rows"]) == 74 and len(record["ends"]) == 23
    runs[phase] = record

def keyed(rows):
    return {(r["test"], r["subtest"]): (r["status"], r.get("expected", r["status"])) for r in rows}

a, b = (keyed(runs[phase]["rows"]) for phase in ["baseline", "candidate"])
assert len(a) == len(b) == 74 and a.keys() == b.keys()
new = "/css/cssom-view/getBoundingClientRect-untransformed-edge-precision.html"
assert sum(k[0] == new for k in b) == 4
assert all(b[k] == (("PASS", "PASS") if k[0] == new else a[k]) for k in b)
ends = [{e["test"]: (e["status"], e.get("expected", e["status"])) for e in runs[p]["ends"]}
        for p in ["baseline", "candidate"]]
assert len(ends[0]) == 23 and ends[0] == ends[1]
changed = [{"test": k[0], "subtest": k[1], "baseline": a[k], "candidate": b[k]}
           for k in sorted(a) if a[k] != b[k]]
assert len(changed) == 2
assert all(r["baseline"] == ("FAIL", "PASS") and r["candidate"] == ("PASS", "PASS") for r in changed)
result = {
    "files": 23, "subtests": 74, "changed": changed,
    "other_subtests_unchanged": 70, "new_test_passes": 4,
    "counts": {p: dict(collections.Counter(r["status"] for r in run["rows"])) for p, run in runs.items()},
    "expected_failures": [{"test": r["test"], "subtest": r["subtest"], "status": r["status"],
                           "expected": r.get("expected", r["status"])}
                          for r in runs["candidate"]["rows"] if r["status"] == "FAIL"],
    "DOMRect_captured_in_each_run": all("dom/base/DOMRect.cpp" in r["before"] for r in runs.values()),
    "run_sha256": {p: hashlib.sha256((ROOT / p / "RUN.json").read_bytes()).hexdigest() for p in runs},
}
assert all(r["expected"] == "FAIL" for r in result["expected_failures"])
assert result["DOMRect_captured_in_each_run"]
text = json.dumps(result, indent=2) + "\n"
if sys.argv[1:] == ["--check"]:
    assert (ROOT / "WPT-COMPARISON.json").read_text() == text
elif not sys.argv[1:]:
    (ROOT / "WPT-COMPARISON.json").write_text(text)
else:
    raise SystemExit("Usage: summarize-wpt.py [--check]")
print(json.dumps({"files": 23, "subtests": 74, "fixed_failures": len(changed)}))
