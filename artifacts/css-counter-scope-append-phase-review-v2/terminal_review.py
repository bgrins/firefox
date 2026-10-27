import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / "artifacts/css-counter-scope-append-comparison-execution-v1"
seen = {}

def read(path):
    body = path.read_bytes()
    seen[str(path.relative_to(ROOT))] = hashlib.sha256(body).hexdigest()
    return json.loads(body)

def authenticate(directory):
    for name, item in read(directory / "FILES.json").items():
        path = directory / name
        digest = item["sha256"] if isinstance(item, dict) else item
        body = path.read_bytes()
        assert hashlib.sha256(body).hexdigest() == digest, str(path)
        seen[str(path.relative_to(ROOT))] = digest

result = read(RUNTIME / "RESULT.json")
assert not (RUNTIME / "FAILURE.json").exists()
assert result["success"] and result["error"] is None and not result["recovery_errors"]
phases = ["original-initial", "candidate-first", "original-restored", "candidate-final"]
assert result["captured_phases"] == result["phase_order"] == phases
assert result["final_variant"] == "candidate" and result["accepted_fix"] is False
assert result["outstanding_processes"] == {} and result["wpt_group"] is None
assert result["mutation_started"] and result["build_attempted"]
pins = read(ROOT / "artifacts/css-counter-scope-append-comparison-inputs-v1/SOURCE-PINS.json")
expected_transitions = [{"path": name, "variant": phase} for phase in phases[1:] for name in pins]
assert result["source_transitions"] == expected_transitions
assert set(result["owned_inputs"]) == set(pins)
for name, item in result["owned_inputs"].items():
    assert item["path"] == name and item["owned_sha256"] == pins[name]["candidate_sha256"]
    path = ROOT / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["owned_sha256"]
    info = path.lstat()
    assert [info.st_dev, info.st_ino] == item["identity"]
for phase in phases:
    directory = (ROOT / "artifacts/css-counter-scope-append-phase-review-v1/original-initial"
                 if phase == "original-initial" else HERE / phase)
    authenticate(directory)
    check = read(directory / "CHECK.json")
    assert check["status"] == "COUNTER_OCOC_PHASE_ARCHIVE_REVIEW_PASS" and check["phase"] == phase
    assert check["rows"] == 88 and check["ends"] == 10 and check["guarded_roles"] == 1223
    assert check["row_counts"] == ({"PASS": 76, "FAIL": 12} if phase.startswith("original") else {"PASS": 88, "FAIL": 0})
    assert check["wpt_exit"] == (1 if phase.startswith("original") else 0)
final = read(RUNTIME / "FINAL.json")
post = read(RUNTIME / "candidate-final-POST.json")
assert final["pins"] == post["pins"]
assert final["modified_native_paths"] == post["modified_native_paths"]
assert all(final["index"][key] == post["index"][key] for key in ["head", "entries", "cached_diff"])
for obs in final["index_observations"].values():
    assert obs["semantic_equal"] and obs["flags_before"] == obs["flags_after"]
ps = subprocess.run(["ps", "-p", "91626", "-o", "pid=,ppid=,stat=,etime=,command="], capture_output=True, text=True)
assert ps.returncode == 1 and not ps.stdout.strip() and not ps.stderr.strip(), (ps.returncode, ps.stdout, ps.stderr)
assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in seen.items())
output = HERE / "terminal"
output.mkdir()
(output / "REFERENCES.json").write_text(json.dumps(seen, indent=2) + "\n")
check = {"status": "COUNTER_OCOC_ARCHIVE_AND_PROCESS_REVIEW_PASS", "outer_exit_observed": False,
         "outer_exit": None, "driver_pid_absent": 91626, "process_observation": {"exit": ps.returncode, "stdout": ps.stdout, "stderr": ps.stderr},
         "driver_result_success": True, "four_phases_verified": phases, "candidate_sources_live_verified": True,
         "driver_final_guards_match_last_capture": True, "full_live_epoch_verification": False,
         "native_acceptance": False, "required_next_step": "Fresh full final-state verification under an observable tool session before publication"}
(output / "CHECK.json").write_text(json.dumps(check, indent=2) + "\n")
print(json.dumps(check))
