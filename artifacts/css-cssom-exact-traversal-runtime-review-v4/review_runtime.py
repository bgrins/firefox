import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / "css-cssom-exact-traversal-runtime-v4"
PROPOSAL = HERE.parent / "css-cssom-exact-traversal-proposal-v4" / "capsule"
RUNS = [f"{phase}-{n}" for phase in ["baseline-before", "candidate", "baseline-after"] for n in [1, 2]]
SOURCES = ["layout/generic/nsIFrame.cpp", "layout/generic/nsIFrame.h", "layout/base/nsLayoutUtils.cpp", "layout/base/nsLayoutUtils.h"]
NAMES = [f"{mode}-{depth}" for depth in [8, 128] for mode in ["ordinary", "transform-near-leaf", "transform-near-root"]]

def load(path):
    def pairs(items):
        out = {}
        for k, v in items:
            assert k not in out
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=pairs)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pin(pins, suffix):
    values = [v for k, v in pins.items() if k.endswith("/" + suffix) or k == suffix]
    assert len(values) == 1, suffix
    return values[0]

def outcomes(rows):
    result = {(r["test"], r["subtest"]): [r["status"], r.get("expected", r["status"])] for r in rows}
    assert len(result) == len(rows)
    return result

def review():
    state = load(RUNTIME / "STATE.json")
    assert state["status"] == "terminal"
    for name in ["baseline-build", "candidate-build", "restore-build", "format-check", "wpt-lint"]:
        assert load(RUNTIME / (name + ".json"))["exit"] == 0
    for name in ["source_restored", "other_native_unchanged", "head_unchanged", "index_unchanged"]:
        assert state[name] is True
    inputs = load(RUNTIME / "INPUTS.json")
    assert len(inputs["pins"]) == 378
    for name, expected in inputs["pins"].items():
        retained = HERE.parents[1] / name if name.startswith("artifacts/") else RUNTIME / "baseline/inputs" / name
        assert sha(retained) == expected, name
    final = load(RUNTIME / "FINAL.json")
    original = load(RUNTIME / "BEFORE.json")
    for key in ['head','index_diff_sha256','index_entries_sha256']:
        assert inputs[key] == original[key] == final[key], key
    assert original['sources'] == final['sources']
    assert original['fixed_native_pins'] == final['fixed_native_pins']
    assert final['temporary_tests_absent'] is True
    restored = load(RUNTIME / "RESTORED.json")
    assert all(restored[k] == v for k, v in {**original["sources"], **original["fixed_native_pins"]}.items())
    tests = load(RUNTIME / "TESTS.json")
    test_paths = {"/" + t.split("testing/web-platform/tests/", 1)[1] for t in tests}
    wpt, maps = {}, {}
    for phase in ["baseline", "candidate"]:
        r = load(RUNTIME / phase / "RUN.json")
        for name, expected in r['before'].items():
            if expected is None or name.startswith('objdir-full.noindex/'):
                continue
            assert sha(RUNTIME / phase / 'inputs' / name) == expected, name
        events = [json.loads(s) for s in (RUNTIME / phase / "raw.json").read_text().splitlines()]
        rows = [e for e in events if e.get("action") == "test_status"]
        ends = [e for e in events if e.get("action") == "test_end"]
        assert rows == r["rows"] and ends == r["ends"]
        assert len(rows) == 74 and len(ends) == 23 and {e["test"] for e in ends} == test_paths
        assert sum(e.get("action") == "suite_end" for e in events) == 1
        assert r["complete"] and r["before"] == r["after"]
        for source in SOURCES:
            assert r["before"][source] == sha(PROPOSAL / ("original" if phase == "baseline" else "candidate") / Path(source).name)
        wpt[phase], maps[phase] = r, outcomes(rows)
    assert set(maps["baseline"]) == set(maps["candidate"])
    changed = [{"key": list(k), "before": maps["baseline"][k], "after": v} for k, v in maps["candidate"].items() if maps["baseline"][k] != v]
    assert len(changed) == 2
    assert all(c["before"] == ["FAIL", "PASS"] and c["after"] == ["PASS", "PASS"] and c["key"][0].endswith("getBoundingClientRect-untransformed-edge-precision.html") for c in changed)
    expected_fails = [{"key": list(k), "outcome": v} for k, v in maps["candidate"].items() if v[0] == "FAIL"]
    assert len(expected_fails) == 2 and all(r["outcome"] == ["FAIL", "FAIL"] for r in expected_fails)
    end_map = lambda phase: {e["test"]: [e["status"], e.get("expected", e["status"])] for e in wpt[phase]["ends"]}
    assert end_map("baseline") == end_map("candidate")
    historical = load(HERE.parent / "css-cssom-rectangle-standalone-runtime-v1/dom-only/RUN.json")
    assert maps["baseline"] == outcomes(historical["rows"])
    assert end_map("baseline") == {e["test"]: [e["status"], e.get("expected", e["status"])] for e in historical["ends"]}
    rows, environment, binaries = {}, [], {}
    for run in RUNS:
        r = load(RUNTIME / run / "RESULT.json")
        assert load(RUNTIME / (run + "-driver.json"))["exit"] == 0
        assert r["run_kind"] == run and r["stable"] and r["before"] == r["after"] and r["profile_removed"]
        assert r["exit_after_termination"] == -15 and len(r["observations"]) == 1
        assert "-headless" in r["command"] and "-no-remote" in r["command"]
        role = "candidate" if run.startswith("candidate") else "original"
        for source in SOURCES:
            assert pin(r["before"], source) == sha(PROPOSAL / role / Path(source).name)
        for source, expected in original["fixed_native_pins"].items():
            assert pin(r["before"], source) == expected
        for name in ["probe.html", "benchmark.js", "capture.js", "run_browser.py"]:
            assert pin(r["before"], name) == sha(RUNTIME / name)
        binaries[run] = {n: pin(r["before"], "Contents/MacOS/" + n) for n in ["firefox", "XUL"]}
        if not run.startswith("baseline-after"):
            phase = "candidate" if role == "candidate" else "baseline"
            assert all(pin(wpt[phase]["before"], "Contents/MacOS/" + n) == h for n, h in binaries[run].items())
        o = r["observations"][0]
        assert o["valid"] and o["totalMeasuredCalls"] == 6600000
        assert o["config"] == {"iterations": 100000, "samples": 11, "warmup": 10000, "startupMs": 3000, "depths": [8, 128]}
        assert len(o["visibility"]) == 68 and set(o["visibility"]) == {"visible"}
        assert [c["name"] for c in o["cases"]] == NAMES
        assert o["order"] == [NAMES[(slot + sample) % 6] for sample in range(11) for slot in range(6)]
        environment.append({k: o[k] for k in ["userAgent", "devicePixelRatio", "viewport"]})
        for index, c in enumerate(o["cases"]):
            depth = [8, 128][index // 3]
            expected = {"x": depth + (3 if index % 3 else 0), "y": depth + (5 if index % 3 else 0), "width": 20, "height": 10}
            assert c["before"] == c["after"] == c["expected"] == expected and c["stable"]
            assert c["warmupChecksum"] == sum(expected.values()) * 10000
            assert len(c["batches"]) == 11
            ns = []
            for sample, b in enumerate(c["batches"]):
                assert b["sample"] == sample and b["slot"] == (index - sample) % 6 and b["calls"] == 100000
                assert math.isfinite(b["elapsedMs"]) and b["elapsedMs"] > 0
                assert b["checksum"] == b["expectedChecksum"] == sum(expected.values()) * 100000 and b["checksumMatches"]
                assert b["nanosecondsPerCall"] == b["elapsedMs"] * 10
                ns.append(b["nanosecondsPerCall"])
            assert statistics.median(ns) == c["medianNanosecondsPerCall"]
            rows.setdefault(c["name"], {})[run] = {"ns_per_call_batches": ns, "median": statistics.median(ns), "range": [min(ns), max(ns)]}
    assert all(e == environment[0] for e in environment)
    for phase in ["baseline-before", "candidate", "baseline-after"]:
        assert binaries[phase + "-1"] == binaries[phase + "-2"]
    comparisons = {}
    for name, runs in rows.items():
        medians = {phase: [runs[phase + "-" + str(n)]["median"] for n in [1, 2]] for phase in ["baseline-before", "candidate", "baseline-after"]}
        center = {k: statistics.median(v) for k, v in medians.items()}
        comparisons[name] = {"run_medians_ns": medians, "candidate_vs_before_percent": 100 * (center["candidate"] / center["baseline-before"] - 1), "candidate_vs_restored_percent": 100 * (center["candidate"] / center["baseline-after"] - 1), "restored_vs_before_percent": 100 * (center["baseline-after"] / center["baseline-before"] - 1)}
    return {"input_join": {"pins":378,"head":inputs["head"],"index_diff_sha256":inputs["index_diff_sha256"],"index_entries_sha256":inputs["index_entries_sha256"],"final_matches":True}, "correctness": {"changed": changed, "unchanged_subtests": 72, "retained_expected_failures": expected_fails, "file_outcomes": end_map("candidate"), "baseline_matches_historical_dom_only": True}, "timings": rows, "comparisons": comparisons, "environment": environment[0], "binaries": binaries, "limits": "Six fresh-profile headless processes; fixed phase order; eleven quantized repeated batches per case, not independent user samples. Historical binaries identified by contemporaneous hashes, not archived/rebuilt here. No statistical significance or broad performance conclusion."}

if __name__ == "__main__":
    result = review()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--check"]:
        assert (HERE / "INDEPENDENT-RESULT.json").read_text() == text
        print("Independent raw outcome and timing comparison reproduced")
    elif not sys.argv[1:]:
        (HERE / "INDEPENDENT-RESULT.json").write_text(text)
        print(json.dumps(result["comparisons"], indent=2))
    else:
        raise SystemExit("Usage: review_runtime.py [--check]")
