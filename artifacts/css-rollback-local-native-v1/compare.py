import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def compare(baseline, candidate):
    before, after = read(baseline / "RESULT.json"), read(candidate / "RESULT.json")
    assert before["source_role"] == "baseline" and after["source_role"] == "candidate"
    assert before["complete_observation"] and after["complete_observation"]
    assert before["safe_to_continue"] and after["safe_to_continue"]
    expected = read(baseline / "EXPECTED.json")
    assert expected == read(candidate / "EXPECTED.json")
    wanted = {(page, name) for page, names in expected.items() for name in names}
    assert len(wanted) == 80
    assessments = [read(p / "ASSESSMENT.json") for p in (baseline, candidate)]
    rows = []
    for assessment in assessments:
        assert assessment["complete_observation"] and not assessment["errors"]
        table = {(row["test"], row["subtest"]): row for row in assessment["rows"]}
        assert len(assessment["rows"]) == len(table) == 80 and set(table) == wanted
        rows.append(table)
    repaired = [key for key in sorted(wanted) if rows[0][key]["status"] == "FAIL" and rows[1][key]["status"] == "PASS"]
    regressions = [key for key in sorted(wanted) if rows[0][key]["status"] == "PASS" and rows[1][key]["status"] != "PASS"]
    remaining = [key for key in sorted(wanted) if rows[1][key]["status"] != "PASS"]
    assert before["counts"] == {"PASS": 74, "FAIL": 6}
    assert after["counts"] == {"PASS": 80} and after["all_pass"]
    assert len(repaired) == 6 and not regressions and not remaining
    return {"baseline_counts": before["counts"], "candidate_counts": after["counts"],
            "repaired_callbacks": repaired, "regressions": regressions,
            "all_prior_passes_preserved": True,
            "evidence": {str((p / n).relative_to(ROOT)): sha(p / n)
                         for p in (baseline, candidate)
                         for n in ("PINS.json", "RESULT.json", "ASSESSMENT.json", "raw.jsonl")},
            "scope": "Exact A16+B16+D48 assertions; controls, independent raw audit, restoration, source review and standalone publication are separate gates.",
            "native_fix_acceptance": False}


if __name__ == "__main__":
    baseline = ROOT / "artifacts/css-rollback-local-baseline-runtime-v1"
    candidate = ROOT / "artifacts/css-rollback-local-native-runtime-v1/browser"
    result = compare(baseline, candidate)
    with (candidate.parent / "COMPARISON.json").open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))
