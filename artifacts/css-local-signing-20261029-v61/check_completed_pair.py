import hashlib
import importlib.util
import json
import os


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy):
    binding = policy["completed_pair"]
    assert binding and binding["ready"]
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name, pin in {**binding["evidence"], **binding["local_references"]}.items():
        assert sha(root / name) == pin, name
    baseline = load("pow_checkpoint_baseline", root / binding["baseline_checker"])
    original_check = baseline.verify(root, policy)
    runtime = root / binding["runtime"]
    result = read(runtime / "RESULT.json")
    assert result["success"] and result["restoration_verified"] and result["runtime_controls_unchanged"]
    assert result["empty_staging_preserved"] and result["error"] is None and result["publication_errors"] == []
    assert result["native_fix_acceptance"] is False
    terminal = read(root / binding["terminal"])
    assert terminal == binding["terminal_record"] and terminal["exit_code"] == 0
    assert terminal["session_id"] == binding["session"] and terminal["terminal_chunk"] == binding["terminal_tool"]
    assert terminal["result_sha256"] == sha(runtime / "RESULT.json")
    restoration = read(runtime / "RESTORATION.json")
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    source = "servo/components/style/values/generics/calc.rs"
    assert restoration["sources"][source]["sha256"] == binding["source_base_sha256"]
    assert restoration["sources"][source]["identity"] == policy["accepted_current_payloads"][source]["identity"]
    cleanup = read(runtime / "BACKUP-CLEANUP.json")
    assert cleanup["removed"] and cleanup["verified_original_restoration"] and not cleanup["retained_after_failure"]
    assert cleanup["owned_backup_bytes"] == read(runtime / "CANDIDATE-PRE.json")["owned_backup_bytes"]
    assert not os.path.lexists(runtime / "backups")
    owner = read(root / binding["owner_policy"])
    original_owner = read(root / policy["baseline"]["owner_policy"])
    assert owner["head"] == policy["head"] and owner["wpt"] == original_owner["wpt"]
    assert owner["candidate"] == original_owner["candidate"]
    assert read(root / binding["source_roles"])[source]["candidate_sha256"] == binding["source_candidate_sha256"]
    assert read(root / binding["source_roles"])[source]["base_sha256"] == binding["source_base_sha256"]
    assessor = load("pow_checkpoint_assessor", root / binding["assessor"])
    checks = load("pow_checkpoint_checks", root / binding["checks_helper"])
    ownership = load("pow_checkpoint_ownership", root / binding["ownership_helper"])
    build = runtime / "candidate-build"
    built = read(build / "RESULT.json")
    inner = read(build / "build-RESULT.json")
    assert built["command_success"] and built["preservation_verified"] and built["error"] is None
    assert built["native_sources"] == {source: binding["source_candidate_sha256"]}
    assert inner["exit"] == 0 and inner["owned_group_absent"] and inner["cleanup_errors"] == []
    assert inner["error"] is None and inner["stop_reason"] is None
    for name in ("build-PROCESS.json", "WAKE-PROCESS.json"):
        ownership.group_absent(read(build / name)["pgid"])
    original = read(runtime / "original-wpt/ASSESSMENT.json")
    phase = runtime / "candidate-wpt"
    record = read(phase / "RESULT.json")
    assert record["success"] and record["preservation_verified"] and record["execution_error"] is None
    assert record["comparison_gate_passed"] and record["native_fix_acceptance"] is False
    assert read(phase / "APPLICATION-METADATA.json") == read(phase / "APPLICATION-METADATA-POST.json")
    assert read(phase / "PRE.json") == read(phase / "POST.json")
    cleanup = read(phase / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    ownership.group_absent(read(phase / "PROCESS.json")["pgid"])
    assessment_policy = read(phase / "ASSESSMENT-POLICY.json")
    assert assessment_policy == baseline.phase_policy(owner["wpt"])
    assert sha(phase / "tests/css/css-values/pow-special-value-context.html") == binding["fixture_sha256"]
    replay = assessor.assess([json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines()],
        record["exit"], assessment_policy, checks, original=original,
        run_binding=read(phase / "APPLICATION-METADATA.json"))
    assert json.loads(json.dumps(replay)) == read(phase / "ASSESSMENT.json")
    assert replay["complete"] and replay["errors"] == [] and replay["fixture_setup_errors"] == []
    assert replay["comparison_gate_passed"] and replay["comparison_errors"] == []
    assert replay["observed_subtest_count"] == len(replay["rows"]) == 147
    assert replay["regression_signature"] == original["regression_signature"] and len(replay["regression_signature"]) == 131
    assert len(replay["ends"]) == 2 and all(row["status"] == "OK" for row in replay["ends"])
    assert result["candidate_phase"] == {"assessment_sha256": sha(phase / "ASSESSMENT.json"),
        "raw_sha256": sha(phase / "raw.jsonl"), "result_sha256": sha(phase / "RESULT.json")}
    return {"result_sha256": sha(runtime / "RESULT.json"), "baseline": original_check,
        "candidate_assessment_sha256": sha(phase / "ASSESSMENT.json"), "candidate_raw_sha256": sha(phase / "raw.jsonl"),
        "source_base_sha256": binding["source_base_sha256"], "source_candidate_sha256": binding["source_candidate_sha256"],
        "fixture_sha256": binding["fixture_sha256"], "comparison_gate_passed": True,
        "restoration_verified": True, "native_acceptance": False}
