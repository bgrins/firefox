import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("terminal_review", HERE / "review.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
config, owner = r.authenticate()
assert not config["execution_enabled"] and config["actual_terminal"] is None
policy = r.read(owner / "POLICY.json")
assert len(policy["wpt"]["expected_subtests"]) == 18
assert sum(map(len, policy["wpt"]["expected_subtests"].values())) == 125
assert set(policy["wpt"]["fixture_target_pages"]) == set(policy["wpt"]["expected_subtests"])
assert len(policy["wpt"]["fixture_target_pages"]) == 18

def reject(fn):
    try:
        fn()
    except AssertionError:
        return
    raise AssertionError("negative control accepted")

for passes in (0, 61, 125):
    replay = {"complete": True, "rows": [{"status": "PASS" if i < passes else "FAIL"} for i in range(125)], "ends": [{} for _ in range(18)]}
    result = r.observed_outcomes(replay)
    assert result["callbacks_passed"] == passes and result["callbacks_failed"] == 125 - passes
    assert not result["native_acceptance"]
for key, value in [("complete", False), ("rows", []), ("ends", []), ("rows", [{"status": "TIMEOUT"}] * 125)]:
    bad = copy.deepcopy(replay)
    bad[key] = value
    reject(lambda: r.observed_outcomes(bad))

snapshot = {"index": {"head": policy["head"], "entries": "saved-index", "cached_diff": r.hashlib.sha256(b"").hexdigest(), "working_diff": r.hashlib.sha256(b"").hexdigest()}, "nested_index": {"saved": True}, "working_sources_binaries_research_preserved": True, "current_raw_stable_during_check": True}
binaries = {name: "new-build-hash" for name in policy["rebuilt_binaries"]}
metadata = {"revision": policy["head"], "build_revision": policy["head"], "harness_revision": policy["head"], "source_role": "original"}
built = {"snapshot": snapshot, "binaries": binaries, "browser_build_performed": True}
args = [policy, {"snapshot": copy.deepcopy(snapshot)}, built, metadata, copy.deepcopy(metadata), [copy.deepcopy(snapshot) for _ in range(4)], copy.deepcopy(binaries)]
r.validate_build_phase(*args)
for field in ("revision", "build_revision", "harness_revision", "source_role"):
    bad = copy.deepcopy(args)
    bad[3][field] = bad[4][field] = "wrong-historical-or-role"
    reject(lambda: r.validate_build_phase(*bad))
for change in ("binary", "snapshot", "diff", "build", "index", "nested"):
    bad = copy.deepcopy(args)
    if change == "binary": bad[6][next(iter(binaries))] = "old-build-hash"
    if change == "snapshot": bad[5][0]["current_raw_stable_during_check"] = False
    if change == "diff": bad[2]["snapshot"]["index"]["working_diff"] = "held-provider-diff"
    if change == "build": bad[2]["browser_build_performed"] = False
    if change == "index": bad[1]["snapshot"]["index"]["entries"] = "different-index"
    if change == "nested": bad[1]["snapshot"]["nested_index"] = {"wrong": True}
    reject(lambda: r.validate_build_phase(*bad))
for path in HERE.glob("*.py"):
    compile(path.read_text(), str(path), "exec")
print(json.dumps({"observation_positives": 3, "observation_negatives": 4, "build_phase_positive": 1, "build_phase_negatives": 10, "owner_payloads_authenticated": True, "terminal_null": True, "live_checks_executed": False}))
