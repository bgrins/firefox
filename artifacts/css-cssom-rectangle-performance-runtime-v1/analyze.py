#!/usr/bin/env python3
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ["baseline-before-1", "baseline-before-2", "integer-only-1", "integer-only-2", "baseline-after-1", "baseline-after-2"]
PRODUCER_FILES = "c868deed8af05bdf101008fdfa5066cd3c67ab207f756e8b540c99f241e6bc42"
CONFIG = {"iterations": 20000, "samples": 7, "warmup": 3000, "startupMs": 3000, "depths": [8, 128]}
PINNED_INPUTS = {
    "probe.html": "a6e63c4335935f5522743dab5d6795f2453cfc613b2e33581d88fcc3ef5de999",
    "benchmark.js": "d4aa4bb6e23f6f533d2b8b15321817cfacbb8bbc78fc7d7bdbd687393d93035c",
    "original-nsLayoutUtils.cpp": "4c8af5a446595014cbd2718436af2da40ac33721a24f987cb3ef0ea16a5fc6e1",
    "candidate-nsLayoutUtils.cpp": "01f0dc868e393e6918ffbaa22be647538df96df289ef178bce5d648d94750a20",
    "original-DOMRect.cpp": "7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5",
}

def read(name):
    return json.loads((ROOT / name).read_text())

def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

def analyze():
    for name, expected in PINNED_INPUTS.items():
        assert sha(name) == expected, name
    bridge = read("SOURCE-BRIDGE.json")
    candidate = (ROOT / "candidate-nsLayoutUtils.cpp").read_text()
    assert candidate.count(bridge["runtime_text"]) == 1
    recovered = candidate.replace(bridge["runtime_text"], bridge["proposal_text"])
    assert hashlib.sha256(recovered.encode()).hexdigest() == bridge["proposal_sha256"]
    assert sha("candidate-nsLayoutUtils.cpp") == bridge["runtime_sha256"]
    inputs = read("INPUTS.json")
    assert inputs["producer_FILES_sha256"] == PRODUCER_FILES
    assert inputs["runs"] == RUNS and inputs["calls_per_run"] == 840000
    state = read("STATE.json")
    assert state["status"] == "terminal" and state["accepted"] is False
    for key in ["format_check_exit", "candidate_build_exit", "restore_build_exit"]:
        assert state[key] == 0
    for key in ["source_restored", "head_unchanged", "index_unchanged"]:
        assert state[key] is True
    for name in ["format-check", "candidate-build", "restore-build"]:
        assert read(name + ".json")["exit"] == 0
    before, restored = read("BEFORE.json"), read("RESTORED.json")
    assert before["candidate"] == PINNED_INPUTS["candidate-nsLayoutUtils.cpp"]
    baseline_sources = {k: v for k, v in before["baseline"].items() if not k.startswith("objdir-")}
    assert all(restored[k] == v for k, v in baseline_sources.items())
    records, case_results, timings = [], {}, []
    common_sources = None
    environments = []
    for run in RUNS:
        assert read(run + "-driver.json")["exit"] == 0
        r = read(run + "/RESULT.json")
        assert r["run_kind"] == run and r["stable"] and r["before"] == r["after"]
        assert r["profile_removed"] and r["exit_after_termination"] == -15
        assert "-headless" in r["command"] and len(r["observations"]) == 1
        pinned = r["before"]
        def pin(suffix):
            found = [v for k, v in pinned.items() if k.endswith("/" + suffix)]
            assert len(found) == 1, suffix
            return found[0]
        for name in ["probe.html", "benchmark.js", "capture.js", "run_browser.py"]:
            assert pin(name) == sha(name)
        expected_cpp = "candidate-nsLayoutUtils.cpp" if run.startswith("integer-") else "original-nsLayoutUtils.cpp"
        assert pin("layout/base/nsLayoutUtils.cpp") == sha(expected_cpp)
        assert pin("dom/base/DOMRect.cpp") == sha("original-DOMRect.cpp")
        other_sources = {k: v for k, v in pinned.items() if k.endswith((".cpp", ".h")) and not k.endswith("/nsLayoutUtils.cpp")}
        if common_sources is None:
            common_sources = other_sources
        assert other_sources == common_sources
        for name, expected in baseline_sources.items():
            if name != "layout/base/nsLayoutUtils.cpp":
                assert pin(name) == expected
        binaries = {name: pin("Contents/MacOS/" + name) for name in ["firefox", "XUL"]}
        if run.startswith("baseline-"):
            source = before["baseline"] if run.startswith("baseline-before") else restored
            assert all(binaries[n] == source["objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + n] for n in binaries)
        o = r["observations"][0]
        assert o["valid"] and o["config"] == CONFIG and o["totalMeasuredCalls"] == 840000
        assert len(o["visibility"]) == 44 and set(o["visibility"]) == {"visible"}
        assert len(o["cases"]) == 6 and len(o["order"]) == 42
        names = [f"{mode}-{depth}" for depth in [8, 128] for mode in ["ordinary", "transform-near-leaf", "transform-near-root"]]
        assert [c["name"] for c in o["cases"]] == names
        assert o["order"] == [names[(slot + sample) % 6] for sample in range(7) for slot in range(6)]
        run_summary = {}
        for index, c in enumerate(o["cases"]):
            depth = [8, 128][index // 3]
            transformed = index % 3 != 0
            expected = {"x": depth + (3 if transformed else 0), "y": depth + (5 if transformed else 0), "width": 20, "height": 10}
            assert c["depth"] == depth and c["name"] == c["mode"] + "-" + str(depth)
            assert c["before"] == c["after"] == c["expected"] == expected and c["stable"]
            assert c["warmupChecksum"] == sum(expected.values()) * 3000
            assert len(c["batches"]) == 7
            elapsed = []
            for sample, b in enumerate(c["batches"]):
                assert b["sample"] == sample and b["slot"] == (index - sample) % 6
                assert b["calls"] == 20000 and b["elapsedMs"] > 0
                assert b["checksumMatches"] and b["checksum"] == b["expectedChecksum"] == sum(expected.values()) * 20000
                assert b["nanosecondsPerCall"] == b["elapsedMs"] * 50
                elapsed.append(b["elapsedMs"])
            timings.extend(elapsed)
            median = statistics.median(elapsed) * 50
            assert median == c["medianNanosecondsPerCall"]
            row = {"elapsed_ms": elapsed, "median_ns_per_call": median, "min_ns_per_call": min(elapsed) * 50, "max_ns_per_call": max(elapsed) * 50}
            case_results.setdefault(c["name"], {})[run] = row
            run_summary[c["name"]] = median
        records.append({"run": run, "raw_sha256": sha(run + "/RESULT.json"), "binaries": binaries,
                        "layout_source_sha256": pin("layout/base/nsLayoutUtils.cpp"), "medians_ns_per_call": run_summary})
        environments.append({k: o[k] for k in ["userAgent", "devicePixelRatio", "viewport"]})
    assert all(e == environments[0] for e in environments)
    for a, b in [(0, 1), (2, 3), (4, 5)]:
        assert records[a]["binaries"] == records[b]["binaries"]
    assert len({tuple(r["binaries"].values()) for r in records}) == 3
    comparisons = {}
    for name, runs in case_results.items():
        baseline = [runs[r]["median_ns_per_call"] for r in RUNS if r.startswith("baseline")]
        candidate = [runs[r]["median_ns_per_call"] for r in RUNS if r.startswith("integer")]
        b, c = statistics.median(baseline), statistics.median(candidate)
        comparisons[name] = {"baseline_run_medians_ns": baseline, "candidate_run_medians_ns": candidate,
                             "baseline_median_of_run_medians_ns": b, "candidate_median_of_run_medians_ns": c,
                             "candidate_change_percent_descriptive": (c - b) * 100 / b}
    return {"decision": "HOLD_INTEGER_NATIVE_REPAIR", "runs": records, "cases": case_results,
            "descriptive_comparisons": comparisons, "environment": environments[0],
            "checks": {"stable_before_after_pins": 6, "calibrated_cases": 36, "checked_batches": 252,
                       "measured_calls": 5040000, "source_restored_receipt": True,
                       "all_elapsed_values_integer_ms": all(float(x).is_integer() for x in timings),
                       "observed_batch_ms_min": min(timings), "observed_batch_ms_max": max(timings),
                       "one_ms_per_call_equivalent_ns": 50},
            "authentication_limit": "Retained inputs and source bytes authenticated; historical binaries are identified by stable contemporaneous SHA-256 receipts, not archived or rebuilt by reviewer.",
            "interpretation": "Six headless exploratory runs, fixed phase order with builds between phases; no CI, statistical significance, or broad performance claim."}

result = analyze()
text = json.dumps(result, indent=2, sort_keys=True) + "\n"
if sys.argv[1:] == ["--check"]:
    assert (ROOT / "COMPARISON.json").read_text() == text
    print(json.dumps({"comparison_reproduced": True, "checks": result["checks"]}))
elif not sys.argv[1:]:
    (ROOT / "COMPARISON.json").write_text(text)
    print(json.dumps({"written": "COMPARISON.json", "decision": result["decision"]}))
else:
    raise SystemExit("Usage: analyze.py [--check]")
