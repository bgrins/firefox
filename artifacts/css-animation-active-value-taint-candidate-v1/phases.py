import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root, here, output, policy, env, verify, owned, cancelled):
    wpt = load("masked_controls_wpt", here / "wpt.py")
    initial = verify()
    wpt.save(output / "PHASES-PRE.json", initial)
    phase = output / "candidate-wpt"
    original = root / policy["baseline_binding"]["directory"] / "original-wpt"
    result = wpt.run(root, here, phase, "candidate", policy, env, verify, owned, cancelled, original)
    assessment = read(phase / "ASSESSMENT.json")
    assert assessment["complete"] and len(assessment["rows"]) == policy["wpt"]["expected_subtest_count"] and not owned
    original_rows = read(original / "ASSESSMENT.json")["rows"]
    by_name = {(row["test"], row["subtest"]): row for row in original_rows}
    pairs = [{"original": by_name[(row["test"], row["subtest"])], "candidate": row} for row in assessment["rows"]]
    wpt.save(output / "OUTCOMES.json", {
        "callbacks_passed": sum(row["status"] == "PASS" for row in assessment["rows"]),
        "callbacks_failed": sum(row["status"] == "FAIL" for row in assessment["rows"]),
        "all_callbacks_passed": all(row["status"] == "PASS" for row in assessment["rows"]),
        "comparison_gate_passed": assessment["comparison_gate_passed"],
        "comparison_errors": assessment["comparison_errors"], "rows": pairs,
        "original_endings": read(original / "ASSESSMENT.json")["ends"],
        "candidate_endings": assessment["ends"], "native_acceptance": False,
    })
    assert read(phase / "PRE.json") == read(phase / "POST.json") == initial
    assert read(phase / "APPLICATION-METADATA.json") == read(phase / "APPLICATION-METADATA-POST.json")
    assert read(phase / "BINARY-PINS.json") == read(output / "candidate-build/RESULT.json")["binaries"]
    assert verify() == initial
    wpt.save(output / "PHASES-POST.json", initial)
    return result
