import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read(name):
    return json.loads((ROOT / name).read_text())

for row in read("INPUTS.json"):
    assert hashlib.sha256((ROOT / row["file"]).read_bytes()).hexdigest() == row["sha256"]
for row in read("SPEC-INPUTS.json"):
    assert hashlib.sha256((ROOT / row["file"]).read_bytes()).hexdigest() == row["sha256"]

baseline = read("inputs/baseline-RUN.json")
candidate = read("inputs/candidate-RUN.json")
for stem, receipt in [("baseline", baseline), ("candidate", candidate)]:
    raw = [json.loads(line) for line in (ROOT / f"inputs/{stem}-raw.json").read_text().splitlines()]
    assert [r for r in raw if r.get("action") == "test_status"] == receipt["rows"]
    assert [r for r in raw if r.get("action") == "test_end"] == receipt["harness"]
    assert not [r for r in raw if r.get("action") in ("crash", "process_crash")]
    assert receipt["stable"]
    assert len({(r["test"], r["subtest"]) for r in receipt["rows"]}) == len(receipt["rows"])

name = "/css/css-properties-values-api/registered-token-boundaries.html"
expected = read("PREDICTIONS.json")
assert len(expected) == 37 and len({x["name"] for x in expected}) == 37
for receipt, field in [(baseline, "original_expected"), (candidate, "candidate_expected")]:
    actual = {r["subtest"]: r["status"] for r in receipt["rows"] if r["test"] == name}
    assert actual == {r["name"]: r[field] for r in expected}
assert candidate["build"]["exit"] == 0 and candidate["exit"] == 0 and candidate["complete"]
assert collections.Counter(r["status"] for r in candidate["rows"]) == {"PASS": 308}
assert collections.Counter(r["status"] for r in candidate["harness"]) == {"OK": 18}
assert len(candidate["pins_before"]) == len(candidate["pins_after"]) == 68
changed = {k for k in candidate["pins_before"] if candidate["pins_before"][k] != candidate["pins_after"][k]}
assert changed == {"servo/components/style/properties_and_values/value.rs", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL"}
assert candidate["candidate_source_sha256"] == hashlib.sha256((ROOT / "inputs/value.candidate.rs").read_bytes()).hexdigest()
assert baseline["pins"]["testing/web-platform/tests/css/css-properties-values-api/registered-token-boundaries.html"] == hashlib.sha256((ROOT / "inputs/probe-v2.html").read_bytes()).hexdigest()
old = (ROOT / "inputs/probe-v1.html").read_text()
new = (ROOT / "inputs/probe-v2.html").read_text()
assert old.replace('    target.style.setProperty("--result", `@var(${c.property})`);', '    target.style.setProperty("--prefix", "@");\n    target.style.setProperty("--result", `var(--prefix)var(${c.property})`);') == new
prior = read("inputs/prior253.json")["candidate"]["rows"] + read("inputs/prior18.json")["rows"]
assert len(prior) == 271
old_map = {(x["test"], x["subtest"]): x["status"] for x in prior}
assert len(old_map) == 271
new_map = {(x["test"], x["subtest"]): x["status"] for x in candidate["rows"] if x["test"] != name}
assert old_map == new_map

import difflib
original = (ROOT / "inputs/value.original.rs").read_text().splitlines(True)
updated = (ROOT / "inputs/value.candidate.rs").read_text().splitlines(True)
upstream = (ROOT / "inputs/value.upstream.rs").read_text()
for tag, a, b, c, d in difflib.SequenceMatcher(None, original, updated, autojunk=False).get_opcodes():
    if tag == "equal":
        continue
    # Context makes insertions and deletions unambiguous in each complete source.
    start = max(0, a - 3)
    end = min(len(original), b + 3)
    before = "".join(original[start:end])
    after = "".join(original[start:a] + updated[c:d] + original[b:end])
    assert upstream.count(before) == 1
    upstream = upstream.replace(before, after)
assert upstream == (ROOT / "inputs/value.upstream-candidate.rs").read_text()
packaging = read("inputs/packaging.json")
for label, fname in [("stack", "stack.patch"), ("standalone", "standalone.patch")]:
    data = (ROOT / "inputs" / fname).read_bytes()
    assert hashlib.sha256(data).hexdigest() == packaging[label]["sha256"]
    assert packaging[label]["exact_apply_reverse"]
    assert len(packaging[label]["paths"]) == 2
    assert data.count(b"diff --git ") == 2
assert packaging["standalone"]["pins"]["servo/components/style/properties_and_values/value.rs"] == hashlib.sha256(upstream.encode()).hexdigest()
print(json.dumps({"status": "PASS", "new_cases": 37, "repaired": 10, "candidate_subtests": 308, "candidate_harnesses": 18, "pins": 68, "unchanged_prior_cases": 271, "excluded_invalid_v1_cases": 5, "upstream_delta_transfer": "exact"}, sort_keys=True))
