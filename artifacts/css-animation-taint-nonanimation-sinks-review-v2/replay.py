import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
owner = ROOT / "artifacts/css-taint-nonanimation-installed-browsers-v2"
assert sha(owner / "FILES.json") == "36df3fdb014f74e06b94fec1dcb65d644761d3619158ed5bf53e39a7caef1e47"
for name, record in read(owner / "FILES.json").items():
    assert sha(owner / name) == (record if isinstance(record, str) else record["sha256"])
spec = importlib.util.spec_from_file_location("saved_taint_runner", owner / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
references = {}
results = {}
for browser, folder, pin, session, terminal in [
    ("firefox", "css-taint-nonanimation-stock-firefox-runtime-2", "7fb93eff39557d78c3c77fba6069c6bd61bb082ace3f6bca84883c7676f91870", 91631, "754135"),
    ("chrome", "css-taint-nonanimation-chrome-runtime-2", "5573fe33afc26fb522ab472ed45d20325e928eb6495f47e04679078aa260133c", 44118, "69384c"),
]:
    runtime = ROOT / "artifacts" / folder
    assert sha(runtime / "FILES.json") == pin
    for name, record in read(runtime / "FILES.json").items():
        path = runtime / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == record["sha256"] and path.stat().st_size == record["bytes"]
        references[str(path.relative_to(ROOT))] = record
    references[str((runtime / "FILES.json").relative_to(ROOT))] = {"sha256": pin, "bytes": (runtime / "FILES.json").stat().st_size}
    policy, binding = read(runtime / "POLICY.json"), read(runtime / "BINDING.json")
    assert policy == read(owner / "POLICY.json")
    pages = [read(runtime / f"page-{i}.json") for i in (1, 2)]
    requests = [read(path) for path in sorted(runtime.glob("request-*.json"))]
    assert len(requests) == 2 and all(requests.count(page) == 1 for page in pages)
    for page, name in zip(pages, policy["roster"]):
        runner.validate(page, policy, binding["run_id"], name, browser)
    assessment = runner.assessment(pages, policy)
    assert assessment == read(runtime / "ASSESSMENT.json")
    assert (assessment["pass"], assessment["fail"], assessment["pages"]) == ((2, 4, 2) if browser == "firefox" else (4, 2, 2))
    assert assessment["all_endings_ok"] and not assessment["suite_pass"]
    resources = dict(policy["resources"])
    resources["/resources/testharnessreport.js"] = policy["bridge"]
    served = read(runtime / "RESOURCES.json")
    assert set(served) == set(resources)
    for name, row in resources.items():
        path = ROOT / row["path"]
        assert sha(path) == row["sha256"] == served[name]["sha256"]
        assert path.stat().st_size == served[name]["bytes"]
        references[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
    result, end, cleanup = (read(runtime / name) for name in ("RESULT.json", "ROOT-TERMINAL.json", "CLEANUP.json"))
    assert (end["session_id"], end["terminal_chunk"], end["exit"]) == (session, terminal, 0)
    assert end["result_sha256"] == sha(runtime / "RESULT.json")
    assert end["owner_manifest_sha256"] == sha(owner / "FILES.json")
    assert result["execution_complete"] and result["error"] is None
    assert cleanup["temporary_removed"] and cleanup["remaining_profile_commands"] == []
    assert cleanup["initial_group"]["owned_group_absent"]
    assert read(runtime / "SERVER-ERRORS.json") == []
    traces = {}
    for row in assessment["rows"]:
        prop = "writing-mode" if "writing-mode" in row["name"] else "direction"
        mode = next(mode for mode in ("direct", "alias", "literal") if f" {mode}:" in row["name"])
        expected_status = int(mode != "literal" and (browser == "firefox" or prop == "direction"))
        assert row["status"] == expected_status
        if not expected_status:
            assert row["message"] is None
            continue
        start = row["message"].index('{"property":')
        trace, _ = json.JSONDecoder().raw_decode(row["message"][start:])
        assert trace["property"] == prop and trace["mode"] == mode
        assert [sample["phase"] for sample in trace["samples"]] == ["first-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"]
        assert trace["membership"] == {"count": 1, "sameAnimation": True, "sameEffect": True}
        assert trace["beforeMembership"] == trace["afterMembership"]
        animated = "rtl" if prop == "direction" else "vertical-rl"
        for stage in ("initial", "beforeMembership", "afterMembership"):
            value = trace[stage]
            assert value["variable"] == value["alias"] == animated
            assert value["duration"] == value["computedDuration"] == 2000
            assert value["cssDuration"] == "2s" and value["progress"] == .375
            assert value["time"] == 750 and value["state"] == "paused" and value["effectSame"] is True
        assert trace["initial"]["sink"] == ("ltr" if browser == "chrome" else animated)
        assert trace["beforeMembership"]["sink"] == animated
        assert all(sample["value"] == animated for sample in trace["samples"])
        traces[prop + ":" + mode] = trace
    results[browser] = {"terminal": end, "failure_traces": traces,
        "assessment": assessment, "cleanup": cleanup,
        "served_resources_sha256": sha(runtime / "RESOURCES.json")}
assert results["firefox"]["served_resources_sha256"] == results["chrome"]["served_resources_sha256"]
for path in [owner / "FILES.json", owner / "run.py", ROOT / "artifacts/css-animation-taint-nonanimation-sinks-probe-v2/FILES.json", ROOT / "artifacts/css-contextual-duration-animation-taint-interop-reassessment-v1/FILES.json"]:
    references[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
local = ROOT / "artifacts/css-animation-taint-nonanimation-original-runtime-1"
assert sha(local / "FILES.json") == "08bf4282478f125fc45df5d084eed0e7bfae65e0d4d3e82e2814c2105be6688a"
for name, record in read(local / "FILES.json").items():
    path = local / name
    assert path.is_file() and not path.is_symlink()
    assert sha(path) == record["sha256"] and path.stat().st_size == record["bytes"]
    references[str(path.relative_to(ROOT))] = record
local_owner = ROOT / "artifacts/css-animation-taint-nonanimation-original-v1"
assert sha(local_owner / "FILES.json") == "5558ab8dd59c6649fccd39cc52015b8388d6bb4b2287d7c2bc8d57aba913bd67"
for name, pin in read(local_owner / "FILES.json").items():
    assert sha(local_owner / name) == pin
policy = read(local_owner / "POLICY.json")
for name, pin in policy["references"].items():
    assert sha(ROOT / name) == pin
phase = local / "original-wpt"
events = [json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines() if line.strip()]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
assessor = load("local_assessor", local_owner / "assess.py")
checks = load("local_checks", ROOT / policy["wpt"]["checks_helper"])
saved = read(phase / "ASSESSMENT.json")
actual = assessor.assess(events, 1, read(phase / "ASSESSMENT-POLICY.json"), checks, run_binding=saved["run_binding"])
assert actual == saved and actual["complete"]
rows = [event for event in events if event.get("action") == "test_status"]
assert sum(row["status"] == "PASS" for row in rows) == 2
assert sum(row["status"] == "FAIL" for row in rows) == 4
assert [event["status"] for event in events if event.get("action") == "test_end"] == ["OK", "OK"]
traces = {}
for row in rows:
    if row["status"] != "FAIL": continue
    start = row["message"].index('{"property":')
    trace, _ = json.JSONDecoder().raw_decode(row["message"][start:])
    traces[trace["property"] + ":" + trace["mode"]] = trace
assert traces == results["firefox"]["failure_traces"]
terminal = read(local / "ROOT-TERMINAL.json")
assert (terminal["session_id"], terminal["terminal_chunk"], terminal["exit"], terminal["browser_exit"]) == (84398, "58bdc0", 0, 1)
assert terminal["result_sha256"] == sha(local / "RESULT.json")
assert terminal["owner_sha256"] == sha(local_owner / "FILES.json")
result = read(local / "RESULT.json")
assert result["observation_complete"] and result["preservation_verified"] and not result["all_callbacks_passed"]
assert read(local / "PRE.json") == read(local / "POST.json")
for key, name in [("assessment_sha256", "ASSESSMENT.json"), ("raw_sha256", "raw.jsonl"), ("result_sha256", "RESULT.json")]:
    assert result["phase"][key] == sha(phase / name)
results["local_original_v1"] = {"terminal": terminal, "result": result, "failure_traces": traces, "matches_v2_installed_firefox_failure_traces": True}
for path in (local / "FILES.json", local_owner / "FILES.json", local_owner / "assess.py"):
    references[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
(HERE / "OBSERVATIONS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
(HERE / "REFERENCES.json").write_text(json.dumps(references, indent=2, sort_keys=True) + "\n")
print("Frozen runtimes/raw requests/assessments/resources authenticated; Firefox2PASS4FAIL2OK, Chrome4PASS2FAIL2OK; six failure traces/calibrations checked; local V1 raw2PASS4FAIL2OK replay and exact failure traces match; no live operations")
