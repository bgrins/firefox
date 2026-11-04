import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    roots = [ROOT / ("artifacts/css-rollback-c-" + role + "-runtime-v1") for role in ("baseline", "candidate")]
    tables = []
    expected = None
    for role, runtime in zip(("baseline", "candidate"), roots):
        owner = read(runtime / "RESULT.json")
        assert owner["error"] is None and owner["restoration_verified"]
        primary, controls = [read(runtime / lane / "RESULT.json") for lane in ("browser", "controls")]
        assert primary["source_role"] == controls["source_role"] == role
        assert primary["complete_observation"] and primary["supplemental_audit_passed"] and primary["safe_to_continue"]
        assert controls["complete_observation"] and controls["supplemental_audit_passed"] and controls["controls_unchanged"]
        roster = read(runtime / "browser/EXPECTED.json")
        if expected is None:
            expected = roster
        assert roster == expected
        assessment = read(runtime / "browser/ASSESSMENT.json")
        table = {(row["test"], row["subtest"]): row["status"] for row in assessment["rows"]}
        wanted = {(page, name) for page, names in expected.items() for name in names}
        assert len(table) == len(assessment["rows"]) == len(wanted) == 190 and set(table) == wanted
        tables.append(table)
    controls = [read(p / "controls/ASSESSMENT.json") for p in roots]
    assert controls[0]["signatures"] == controls[1]["signatures"]
    before, after = tables
    repairs = [key for key in sorted(before) if before[key] == "FAIL" and after[key] == "PASS"]
    regressions = [key for key in sorted(before) if before[key] == "PASS" and after[key] != "PASS"]
    remaining = [key for key in sorted(after) if after[key] != "PASS"]
    result = {"callbacks": 190, "repaired": repairs, "regressions": regressions, "remaining_failures": remaining,
              "all_prior_passes_preserved": not regressions, "all_candidate_pass": not remaining,
              "controls_identical": True,
              "evidence": {str(f.relative_to(ROOT)): sha(f) for p in roots for lane in ("browser", "controls")
                           for f in [p / lane / n for n in ("PINS.json", "RESULT.json", "ASSESSMENT.json", "raw.jsonl")]},
              "native_fix_acceptance": False,
              "scope": "AB(D) versus AB(D)+coldC; source review, performance and independent restoration audits remain separate obligations."}
    with (Path(__file__).parent / "RESULT.json").open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps({k:v for k,v in result.items() if k != "evidence"}, indent=2))
    return 0 if not regressions and not remaining else 1


if __name__ == "__main__":
    raise SystemExit(main())
