import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
owner = ROOT / "artifacts/css-taint-preservation-installed-browsers-v1"
assert sha(owner / "FILES.json") == "19752f427545aa797505188c086cf487bd17c53f2bd503243be5d25ca6dc83f8"
for name, record in read(owner / "FILES.json").items():
    assert sha(owner / name) == (record if isinstance(record, str) else record["sha256"])
spec = importlib.util.spec_from_file_location("saved_taint_runner", owner / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
references = {}
results = {}
for browser, folder, pin, session, terminal in [
    ("firefox", "css-taint-preservation-stock-firefox-runtime-1", "e26a298d1c9b5187f55285a68d7a62df4ada4b254e211d0a5a43b71e485cb14e", 95237, "2c555a"),
    ("chrome", "css-taint-preservation-chrome-runtime-1", "3588ae81d3331ac9ff4ae9fb549ca9112057eb2c44f805da7c03ba931746cc59", 29381, "41f9aa"),
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
    assert (assessment["pass"], assessment["fail"], assessment["pages"]) == (4, 2, 2)
    assert assessment["all_endings_ok"] and not assessment["suite_pass"]
    resources = dict(policy["resources"])
    resources["/resources/testharnessreport.js"] = policy["bridge"]
    served = read(runtime / "RESOURCES.json")
    assert set(served) == set(resources)
    for name, row in resources.items():
        path = ROOT / row["path"]
        assert sha(path) == row["sha256"] == served[name]["sha256"]
        assert path.stat().st_size == served[name]["bytes"]
    result, end, cleanup = (read(runtime / name) for name in ("RESULT.json", "ROOT-TERMINAL.json", "CLEANUP.json"))
    assert (end["session_id"], end["terminal_chunk"], end["exit"]) == (session, terminal, 0)
    assert end["result_sha256"] == sha(runtime / "RESULT.json")
    assert end["owner_manifest_sha256"] == sha(owner / "FILES.json")
    assert result["execution_complete"] and result["error"] is None
    assert cleanup["temporary_removed"] and cleanup["remaining_profile_commands"] == []
    assert cleanup["initial_group"]["owned_group_absent"]
    assert read(runtime / "SERVER-ERRORS.json") == []
    failure = next(row for row in assessment["rows"] if "variable tainted:" in row["name"])
    assert failure["status"] == 1
    start = failure["message"].index('{"mode":')
    trace, _ = json.JSONDecoder().raw_decode(failure["message"][start:])
    assert [sample["phase"] for sample in trace["samples"]] == ["first-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"]
    assert trace["mode"] == "tainted" and trace["membership"] == {"count": 2, "retained": [True, True]}
    assert trace["beforeMembership"] == trace["afterMembership"]
    for stage in ("initial", "beforeMembership", "afterMembership"):
        row = trace[stage]
        assert row["customD"] == "2.5s" and all(t["time"] == 750 and t["state"] == "paused" for t in row["timings"])
        assert row["timings"][0]["duration"] == 2000
    assert trace["initial"]["timings"][1]["duration"] == 1000
    assert trace["initial"]["opacity"] == .75
    target = 1000 if browser == "firefox" else 2000
    assert trace["beforeMembership"]["timings"][1]["duration"] == target
    assert trace["beforeMembership"]["timings"][1]["progress"] == 750 / target
    assert all(sample["opacity"] == 750 / target for sample in trace["samples"])
    results[browser] = {"terminal": end, "tainted_trace": trace,
        "other_failure": [row for row in assessment["rows"] if row["status"] == 1 and row is not failure],
        "passes": [row["name"] for row in assessment["rows"] if row["status"] == 0],
        "cleanup": cleanup, "served_resources_sha256": sha(runtime / "RESOURCES.json")}
assert results["firefox"]["served_resources_sha256"] == results["chrome"]["served_resources_sha256"]
for path in [owner / "FILES.json", owner / "run.py"]:
    references[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
(HERE / "OBSERVATIONS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
(HERE / "REFERENCES.json").write_text(json.dumps(references, indent=2, sort_keys=True) + "\n")
print("Both frozen 17-file runtimes/raw requests/assessments/resources authenticated; 4PASS2FAIL2OK each; no live application/process checks")
