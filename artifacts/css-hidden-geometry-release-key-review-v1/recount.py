import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import itertools
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(root / "source/FILES.json") == "da3d097cdc8e64917127532a4e2504aa757d0b46584b66b84880bcc81d2ce84b"
source = json.loads((root / "source/FILES.json").read_text())
for name, expected in source.items():
    assert sha(root / "source" / name) == expected
run = json.loads((root / "runtime/RESULT.json").read_text())
assert run["before"] == run["after"] and run["stable"] is True
assert run["errors"] == [] and run["profile_removed"] is True
assert run["terminated_owned_parents"] == [86844] and run["launcher_exit"] == 0
assert len(run["observations"]) == 1
observation = run["observations"][0]
assert set(observation) == {"rows", "userAgent"}
assert "Firefox/158.0" in observation["userAgent"]
binary = json.loads((root / "source/RELEASE-PINS.json").read_text())
expected_pins = dict(binary)
for name, expected in {**source, "FILES.json": sha(root / "source/FILES.json")}.items():
    expected_pins[str(root.parents[1] / "artifacts/css-hidden-geometry-release-key-probe-v1" / name)] = expected
# Captured paths are absolute to the producer workspace, so compare their suffixes for relocation.
assert len(run["before"]) == len(expected_pins)
for path, expected in run["before"].items():
    if path in binary:
        assert expected == binary[path]
    else:
        suffix = path.split("/css-hidden-geometry-release-key-probe-v1/", 1)[1]
        assert expected == ({**source, "FILES.json": sha(root / "source/FILES.json")})[suffix]

expected_keys = set(itertools.product((False, True), ("append", "prepend"),
                    ("shrink", "no-shrink", "zero-sibling"), (False, True), ("bounding", "offset")))
keys = set()
failures = []
stages = 0
for row in observation["rows"]:
    assert set(row) == {"nested", "insertion", "mode", "hidden", "api", "stages"}
    assert type(row["nested"]) is bool and type(row["hidden"]) is bool
    key = tuple(row[n] for n in ("nested", "insertion", "mode", "hidden", "api"))
    assert key in expected_keys and key not in keys
    keys.add(key)
    assert [s["phase"] for s in row["stages"]] == ["warm", "visibility", "insert", "remove", "show"]
    for stage in row["stages"]:
        stages += 1
        assert set(stage) == {"phase", "outer", "first", "second", "third", "visible", "expected"}
        assert stage["outer"] == [1, 200 if row["mode"] == "no-shrink" and not row["hidden"] and stage["phase"] == "insert" else 100, 64]
        wanted = [50 if row["mode"] == "shrink" and stage["phase"] == "insert" else 100, 32]
        assert stage["visible"] == wanted and stage["expected"] == wanted
        for name in ("first", "second", "third"):
            value = stage[name]
            assert isinstance(value, list) and len(value) == 2
            assert all(type(n) in (int, float) and math.isfinite(n) for n in value)
        assert stage["first"] == stage["second"] == stage["third"]
        if stage["first"] != wanted:
            failures.append({"configuration": list(key), **stage})
assert keys == expected_keys and stages == 240
assert len(failures) == 12
direct = [r for r in failures if r["configuration"][0] is False]
nested = [r for r in failures if r["configuration"][0] is True]
assert len(direct) == 8 and len(nested) == 4
assert all(r["first"] == [0, 0] and r["phase"] in ("insert", "remove") for r in direct)
assert all(r["first"] == [100, 32] and r["phase"] == "insert" for r in nested)
assert all(r["configuration"][2:4] == ["shrink", True] for r in failures)
summary = json.loads((root / "runtime/SUMMARY.json").read_text())
assert summary == {"rows": 48, "stages": 240, "differences": failures,
                   "calibration_failures": [], "repeated_changes": []}
print(json.dumps({"status": "PASS", "rows": 48, "stages": 240, "matching_stages": 228,
                  "direct_zero_stages": 8, "descendant_stale_stages": 4,
                  "calibration_failures": 0, "repeated_changes": 0,
                  "outer_flush_counts": {"1,100,64": 232, "1,200,64": 8}}))
