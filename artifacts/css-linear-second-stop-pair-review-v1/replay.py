import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PAIR = ROOT / "artifacts/css-linear-second-position-reversible-pair-runtime-2"
CAPSULE = ROOT / "artifacts/css-linear-second-stop-wpt-runner-v2"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def authenticate(directory, digest):
    assert sha(directory / "FILES.json") == digest
    manifest = read(directory / "FILES.json")
    for name, item in manifest.items():
        path = directory / name
        assert path.is_file() and not path.is_symlink()
        wanted = item if isinstance(item, str) else item["sha256"]
        assert sha(path) == wanted
        if isinstance(item, dict):
            assert path.stat().st_size == item["bytes"]
    return manifest

manifest = authenticate(PAIR, "42d67cdc877eba11b58976a2fe4dab387527ba940cb9f4969c17d5aceb5042c0")
links = read(PAIR / "SYMLINKS.json")
actual_files, actual_links = set(), {}
for directory, dirs, files in os.walk(PAIR, followlinks=False):
    for name in dirs[:] + files:
        path = Path(directory) / name
        relative = str(path.relative_to(PAIR))
        if path.is_symlink():
            actual_links[relative] = os.readlink(path)
            if name in dirs:
                dirs.remove(name)
        elif path.is_file():
            actual_files.add(relative)
assert actual_files == set(manifest) | {"FILES.json"}
assert actual_links == links and len(links) == 3
capsule_sha = "177a372c08633facdbb56f22b6f308528afe75b4368f46dd0a29563a6a731a9b"
authenticate(CAPSULE, capsule_sha)
runner = load("review_linear_runner", CAPSULE / "run.py")
bindings = load("review_linear_bindings", CAPSULE / "bindings.py")
assessor = load("review_linear_assessor", CAPSULE / "assess.py")
fixed = read(CAPSULE / "POLICY.json")
checks = load("review_linear_checks", ROOT / fixed["helpers"]["checks"])
owner = read(PAIR / "RESULT.json")
assert owner["success"] and owner["restoration_verified"] and owner["runtime_controls_unchanged"]
assert owner["empty_staging_preserved"] and owner["backups_removed_after_verification"]
assert owner["error"] is None and owner["publication_errors"] == []
assert read(PAIR / "ROOT-TERMINAL.json") == {"session": 68786, "terminal": "b5860c", "exit": 0}
observations, raw, saved = {}, {}, {}
for phase, label, count in [("original-baseline-1", "original-baseline-wpt", 42), ("original-crash-1", "original-crash-wpt", 0), ("candidate-1", "candidate-wpt", 48)]:
    directory = PAIR / label
    policy, epoch = read(directory / "POLICY.json"), read(directory / "EPOCH.json")
    bindings.validate_phase(ROOT, CAPSULE, policy, epoch, runner)
    original = bindings.validate_original(ROOT, CAPSULE, policy, runner)
    result = read(directory / "RESULT.json")
    assert result["execution_error"] is None and result["preservation_error"] is None
    assert result["phase_gate_passed"] and result["observation_gate_passed"]
    events = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
    assessment = assessor.assess(events, result["exit"], policy, checks, original=original,
                                 run_binding=read(directory / "APPLICATION-METADATA.json"))
    publication = runner.augment_assessment(assessment, phase=phase, capsule_sha=capsule_sha,
        epoch_sha=policy["epoch_sha256"], policy=policy, capsule_directory=str(CAPSULE.relative_to(ROOT)),
        experiment_sha=sha(CAPSULE / "EXPERIMENT.json"), execution_preserved=True)
    assert json.loads(json.dumps(publication)) == read(directory / "ASSESSMENT.json")
    statuses = [e for e in events if e.get("action") == "test_status"]
    ends = [e for e in events if e.get("action") == "test_end"]
    assert len(statuses) == count == assessment["observed_subtest_count"]
    assert assessment["phase_gate_passed"] and not assessment["errors"]
    assert assessment["infrastructure_faults"] == (assessment["crashes"] if phase == "original-crash-1" else [])
    assert read(directory / "PRE.json") == read(directory / "POST.json")
    assert read(directory / "APPLICATION-METADATA.json") == read(directory / "APPLICATION-METADATA-POST.json")
    cleanup = read(directory / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    assert read(PAIR / (phase + "-WRAPPER-CLEANUP.json"))["restoration_safe"]
    assert owner["phase_results"][phase] == {"wrapper_exit": 0, "assessment_sha256": sha(directory / "ASSESSMENT.json")}
    observations[phase] = {"rows": len(statuses), "pass": sum(e["status"] == "PASS" for e in statuses),
        "fail": sum(e["status"] == "FAIL" for e in statuses), "end_statuses": [e["status"] for e in ends],
        "complete": assessment["complete"], "wpt_exit": result["exit"], "wrapper_exit": 0}
    raw[phase] = events
    saved[phase] = assessment
assert observations["original-baseline-1"]["pass"] == 30
assert observations["original-baseline-1"]["fail"] == 12
assert observations["candidate-1"]["pass"] == 36 and observations["candidate-1"]["fail"] == 12
assert saved["candidate-1"]["comparison_gate_passed"]
assert saved["original-baseline-1"]["regression_signature"] == saved["candidate-1"]["regression_signature"]
crash = saved["original-crash-1"]["crashes"]
assert len(crash) == 1 and not saved["original-crash-1"]["complete"]
stack = [x.get("function", "") for x in crash[0]["crashing_thread_stack"]]
assert any("parse_linear_function" in s for s in stack)
assert any("unwrap" in s for s in stack)
for role in ("original", "candidate"):
    build = PAIR / (role + "-build")
    outer, inner = read(build / "RESULT.json"), read(build / "build-RESULT.json")
    assert outer["command_success"] and outer["preservation_verified"] and outer["browser_build_performed"]
    assert outer["error"] is None and outer["owned_processes"] == {} and outer["publication_errors"] == []
    assert inner["exit"] == 0 and inner["error"] is None and inner["stop_reason"] is None
    assert inner["owned_group_absent"] and inner["cleanup_errors"] == []
before, after = read(PAIR / "PRE.json"), read(PAIR / "POST.json")
normalized = copy.deepcopy(after)
normalized["index"]["raw_index"] = before["index"]["raw_index"]
assert normalized == before
pre, post = read(PAIR / "PRE-OBSERVATION-EPOCH.json"), read(PAIR / "POST-OBSERVATION-EPOCH.json")
normalized = copy.deepcopy(post)
normalized["raw_index_observation"]["current"] = pre["raw_index_observation"]["current"]
assert normalized == pre
canonical = read(PAIR / "PRE-CURRENT-EPOCH.json")
source = "servo/components/style/values/specified/easing.rs"
normalized = copy.deepcopy(pre)
assert source not in canonical["installed_identities"]
assert normalized["installed_identities"].pop(source)
normalized["counts"]["installed_identities"] -= 1
assert normalized == canonical
restore = read(PAIR / "RESTORATION.json")
assert restore["errors"] == [] and restore["owned_processes"] == {}
assert restore["source_sha256"][source] == canonical["pins"][source]
cleanup = read(PAIR / "BACKUP-CLEANUP.json")
assert cleanup["removed"] and cleanup["verified_original_restoration"]
assert cleanup["inventory_sha256"] == sha(PAIR / "BACKUPS.json")
assert not (PAIR / "backups").exists()
print(json.dumps({"status":"PASS", "regular_payloads":len(manifest), "symlinks":len(links), "phases":observations,
    "full_publication_replay":True, "regression_and_calibration_signatures_exact":True,
    "actual_original_stack":stack, "saved_restoration_verified":True,
    "canonical_projection":"remove only experiment easing identity and its count; refresh only raw observation separately",
    "live_process_or_current_checks_performed":False, "native_acceptance":False}, indent=2))
