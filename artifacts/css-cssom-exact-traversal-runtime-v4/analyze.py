#!/usr/bin/env python3
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ["baseline-before-1", "baseline-before-2", "candidate-1", "candidate-2", "baseline-after-1", "baseline-after-2"]
CONFIG = {"iterations": 100000, "samples": 11, "warmup": 10000, "startupMs": 3000, "depths": [8, 128]}
REPO = ROOT.parents[1]
PROPOSAL = REPO / "artifacts/css-cssom-exact-traversal-proposal-v4/capsule"
SOURCES = ["layout/generic/nsIFrame.cpp", "layout/generic/nsIFrame.h",
           "layout/base/nsLayoutUtils.cpp", "layout/base/nsLayoutUtils.h"]

def read(name):
    return json.loads((ROOT / name).read_text())

def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

def analyze():
    inputs = read("INPUTS.json")
    for name, expected in inputs["pins"].items():
        assert hashlib.sha256((REPO / name).read_bytes()).hexdigest() == expected, name
    state = read("STATE.json")
    assert state["status"] == "terminal" and state["accepted"] is False
    for key in ["wpt_lint_exit", "baseline_build_exit", "format_check_exit", "candidate_build_exit", "restore_build_exit"]:
        assert state[key] == 0
    for key in ["source_restored", "other_native_unchanged", "head_unchanged", "index_unchanged"]:
        assert state[key] is True
    for name in ["wpt-lint", "baseline-build", "format-check", "candidate-build", "restore-build"]:
        assert read(name + ".json")["exit"] == 0
    before, restored = read("BEFORE.json"), read("RESTORED.json")
    final = read("FINAL.json")
    for key in ["head", "index_diff_sha256", "index_entries_sha256"]:
        assert before[key] == final[key] == inputs[key], key
    for key in ["sources", "fixed_native_pins"]:
        assert before[key] == final[key], key
    assert final["temporary_tests_absent"] is True
    baseline_sources = {**before["sources"], **before["fixed_native_pins"]}
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
        candidate_phase = run.startswith("candidate")
        for name in SOURCES:
            snapshot = PROPOSAL / ("candidate" if candidate_phase else "original") / Path(name).name
            assert pin(name) == hashlib.sha256(snapshot.read_bytes()).hexdigest(), name
        for name, expected in before["fixed_native_pins"].items():
            assert pin(name) == expected, name
        binaries = {name: pin("Contents/MacOS/" + name) for name in ["firefox", "XUL"]}
        if not run.startswith("baseline-after"):
            wpt_run = read(("candidate" if candidate_phase else "baseline") + "/RUN.json")
            for name, digest in binaries.items():
                assert wpt_run["before"]["objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + name] == digest
        o = r["observations"][0]
        assert o["valid"] and o["config"] == CONFIG and o["totalMeasuredCalls"] == 6600000
        assert len(o["visibility"]) == 68 and set(o["visibility"]) == {"visible"}
        assert len(o["cases"]) == 6 and len(o["order"]) == 66
        names = [f"{mode}-{depth}" for depth in [8, 128] for mode in ["ordinary", "transform-near-leaf", "transform-near-root"]]
        assert [c["name"] for c in o["cases"]] == names
        assert o["order"] == [names[(slot + sample) % 6] for sample in range(11) for slot in range(6)]
        run_summary = {}
        for index, c in enumerate(o["cases"]):
            depth = [8, 128][index // 3]
            transformed = index % 3 != 0
            expected = {"x": depth + (3 if transformed else 0), "y": depth + (5 if transformed else 0), "width": 20, "height": 10}
            assert c["depth"] == depth and c["name"] == c["mode"] + "-" + str(depth)
            assert c["before"] == c["after"] == c["expected"] == expected and c["stable"]
            assert c["warmupChecksum"] == sum(expected.values()) * 10000
            assert len(c["batches"]) == 11
            elapsed = []
            for sample, b in enumerate(c["batches"]):
                assert b["sample"] == sample and b["slot"] == (index - sample) % 6
                assert b["calls"] == 100000 and b["elapsedMs"] > 0
                assert b["checksumMatches"] and b["checksum"] == b["expectedChecksum"] == sum(expected.values()) * 100000
                assert b["nanosecondsPerCall"] == b["elapsedMs"] * 10
                elapsed.append(b["elapsedMs"])
            timings.extend(elapsed)
            median = statistics.median(elapsed) * 10
            assert median == c["medianNanosecondsPerCall"]
            row = {"elapsed_ms": elapsed, "median_ns_per_call": median, "min_ns_per_call": min(elapsed) * 10, "max_ns_per_call": max(elapsed) * 10}
            case_results.setdefault(c["name"], {})[run] = row
            run_summary[c["name"]] = median
        records.append({"run": run, "raw_sha256": sha(run + "/RESULT.json"), "binaries": binaries,
                        "layout_source_sha256": pin("layout/base/nsLayoutUtils.cpp"), "medians_ns_per_call": run_summary})
        environments.append({k: o[k] for k in ["userAgent", "devicePixelRatio", "viewport"]})
    assert all(e == environments[0] for e in environments)
    for a, b in [(0, 1), (2, 3), (4, 5)]:
        assert records[a]["binaries"] == records[b]["binaries"]
    comparisons = {}
    for name, runs in case_results.items():
        baseline = [runs[r]["median_ns_per_call"] for r in RUNS if r.startswith("baseline")]
        candidate = [runs[r]["median_ns_per_call"] for r in RUNS if r.startswith("candidate")]
        b, c = statistics.median(baseline), statistics.median(candidate)
        comparisons[name] = {"baseline_run_medians_ns": baseline, "candidate_run_medians_ns": candidate,
                             "baseline_median_of_run_medians_ns": b, "candidate_median_of_run_medians_ns": c,
                             "candidate_change_percent_descriptive": (c - b) * 100 / b}
    return {"decision": "DESCRIPTIVE_RESULTS_REQUIRE_REVIEW", "runs": records, "cases": case_results,
            "descriptive_comparisons": comparisons, "environment": environments[0],
            "checks": {"stable_before_after_pins": 6, "calibrated_cases": 36, "checked_batches": 396,
                       "measured_calls": 39600000, "source_restored_receipt": True,
                       "all_elapsed_values_integer_ms": all(float(x).is_integer() for x in timings),
                       "observed_batch_ms_min": min(timings), "observed_batch_ms_max": max(timings),
                       "one_ms_per_call_equivalent_ns": 10},
            "authentication_limit": "Retained inputs and source bytes authenticated; historical binaries are identified by stable contemporaneous SHA-256 receipts, not archived or rebuilt by reviewer.",
            "interpretation": "Six headless exploratory runs, fixed phase order with builds between phases; no CI, statistical significance, or broad performance claim."}

result = analyze()
text = json.dumps(result, indent=2, sort_keys=True) + "\n"
if sys.argv[1:] == ["--check"]:
    assert (ROOT / "PERFORMANCE-COMPARISON.json").read_text() == text
    print(json.dumps({"comparison_reproduced": True, "checks": result["checks"]}))
elif not sys.argv[1:]:
    (ROOT / "PERFORMANCE-COMPARISON.json").write_text(text)
    print(json.dumps({"written": "PERFORMANCE-COMPARISON.json", "decision": result["decision"]}))
else:
    raise SystemExit("Usage: analyze.py [--check]")
