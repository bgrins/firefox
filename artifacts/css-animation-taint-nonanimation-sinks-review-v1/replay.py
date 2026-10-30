import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
owner = ROOT / "artifacts/css-taint-nonanimation-installed-browsers-v1"
assert sha(owner / "FILES.json") == "91c5e544784caf3f2f8000a002f25ce739305d37404b4ba5f016ccf726c5b3b2"
for name, record in read(owner / "FILES.json").items():
    assert sha(owner / name) == (record if isinstance(record, str) else record["sha256"])
spec = importlib.util.spec_from_file_location("saved_taint_runner", owner / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
references = {}
results = {}
for browser, folder, pin, session, terminal in [
    ("firefox", "css-taint-nonanimation-stock-firefox-runtime-1", "1c980a5a3215bb99adcdcfebc0d2d150d92d39559e47ccd93e6e80703445c6f1", 10035, "512dd7"),
    ("chrome", "css-taint-nonanimation-chrome-runtime-1", "9543320cca57900f89539a2290a1c3d3720bbd9a7f2130764200540bd0ba6bbd", 53069, "ffd44c"),
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
for path in [owner / "FILES.json", owner / "run.py", ROOT / "artifacts/css-animation-taint-nonanimation-sinks-probe-v1/FILES.json", ROOT / "artifacts/css-contextual-duration-animation-taint-interop-reassessment-v1/FILES.json"]:
    references[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
(HERE / "OBSERVATIONS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
(HERE / "REFERENCES.json").write_text(json.dumps(references, indent=2, sort_keys=True) + "\n")
print("Frozen runtimes/raw requests/assessments/resources authenticated; Firefox2PASS4FAIL2OK, Chrome4PASS2FAIL2OK; six failure traces/calibrations checked; no live operations")
