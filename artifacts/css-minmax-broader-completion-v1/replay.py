import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-v5"
RUNTIME = ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-runtime-1"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, pin):
    assert sha(directory / "FILES.json") == pin
    for name, record in read(directory / "FILES.json").items():
        path = directory / name
        assert not path.is_symlink()
        assert sha(path) == (record["sha256"] if isinstance(record, dict) else record)


authenticate(OWNER, "0fe5f7417772211591e1a47bbc67b30432e360dd5da0cafca9a623e940c2528a")
policy = read(OWNER / "POLICY.json")
authenticate(RUNTIME, policy["baseline_binding"]["manifest_sha256"])
comparison = load("completion_comparison", OWNER / "comparison.py")
assessor = load("completion_assessor", OWNER / "assess.py")
checks = load("completion_checks", ROOT / policy["wpt"]["checks_helper"])
original = comparison.replay_original(ROOT, policy, assessor, checks)
phase = RUNTIME / "candidate-wpt"
phase_result = read(phase / "RESULT.json")
saved_policy = read(phase / "ASSESSMENT-POLICY.json")
assert saved_policy == comparison.phase_policy(policy["wpt"])
events = [json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines()]
candidate = assessor.assess(events, phase_result["exit"], saved_policy, checks,
                            original=original, run_binding=read(phase / "APPLICATION-METADATA.json"))
assert candidate == read(phase / "ASSESSMENT.json")
assert candidate["complete"] and candidate["comparison_gate_passed"]
assert len(candidate["rows"]) == 472
assert sum(row["status"] == "PASS" for row in candidate["rows"]) == 470
assert sum(row["status"] == "FAIL" for row in candidate["rows"]) == 2
assert candidate["regression_signature"] == original["regression_signature"]
assert len(candidate["regression_signature"]) == 470
targets = {(page, name) for page, names in policy["wpt"]["target_subtests"].items() for name in names}
assert len(targets) == 14
assert all(row["status"] == "FAIL" for row in original["rows"] if (row["test"], row["subtest"]) in targets)
assert all(row["status"] == "PASS" for row in candidate["rows"] if (row["test"], row["subtest"]) in targets)
authored = [row for row in candidate["rows"] if row["test"] in policy["wpt"]["candidate_required_pass_pages"]]
assert len(authored) == 32 and all(row["status"] == "PASS" for row in authored)
assert read(phase / "PRE.json") == read(phase / "POST.json")
assert read(phase / "APPLICATION-METADATA.json") == read(phase / "APPLICATION-METADATA-POST.json")
outer = read(RUNTIME / "CANDIDATE-RESULT.json")
assert sha(RUNTIME / "CANDIDATE-RESULT.json") == "37a8eaa2abded29949bc9bdebc6de9dad17341f79a5009e6dfedf49a30168920"
for key, name in (("assessment_sha256", "ASSESSMENT.json"), ("raw_sha256", "raw.jsonl"), ("result_sha256", "RESULT.json")):
    assert outer["candidate_phase"][key] == sha(phase / name)
assert outer["success"] and outer["restoration_verified"] and not outer["error"] and not outer["publication_errors"]
terminal = read(RUNTIME / "CANDIDATE-ROOT-REPORTED-TERMINAL.json")
assert (terminal["session_id"], terminal["terminal_chunk"], terminal["exit"]) == (87739, "38759f", 0)
assert terminal["result_sha256"] == sha(RUNTIME / "CANDIDATE-RESULT.json")
restoration = read(RUNTIME / "RESTORATION.json")
assert restoration["errors"] == [] and restoration["owned_processes"] == {}
for path, role in read(OWNER / "SOURCE-ROLES.json").items():
    assert restoration["sources"][path]["sha256"] == role["base_sha256"]
cleanup = read(RUNTIME / "BACKUP-CLEANUP.json")
assert cleanup["removed"] and cleanup["verified_original_restoration"] and not cleanup["retained_after_failure"]
assert cleanup["owned_backup_bytes"] == 1008605176
observation = read(RUNTIME / "RAW-INDEX-OBSERVATION.json")
assert observation["semantic_index_unchanged"] and observation["canonical_updated"] is False
print(json.dumps({"original_discovery_replay_exact": True, "strict_projection_exact": True,
                  "candidate_replay_exact": True, "callbacks": 472, "target_repairs": 14,
                  "authored_pass": 32, "candidate_pass": 470, "legacy_fail": 2,
                  "strict_signatures": 470, "endings": len(candidate["ends"]),
                  "restoration_receipts_verified": True, "raw_index_observation": observation,
                  "native_acceptance": False, "browser_or_owner_executed": False}, indent=2))
