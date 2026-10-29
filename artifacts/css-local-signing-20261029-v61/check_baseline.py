import hashlib
import importlib.util
import json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phase_policy(settings):
    expected, targets = settings["expected_subtests"], settings["target_subtests"]
    result = dict(settings, tests={test: "testharness" for test in expected}, held_subtests={})
    result["regression_subtests"] = {test: [name for name in names if name not in targets.get(test, [])]
                                    for test, names in expected.items()}
    result["cardinality_description"] = "Exact sealed target and control names; existing control failures retain full signatures."
    return result


def verify(root, policy):
    binding = policy["baseline"]
    assert binding and binding["ready"]
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name, pin in {**binding["evidence"], **binding["local_references"]}.items():
        assert sha(root / name) == pin, name
    runtime = root / binding["runtime"]
    phase = runtime / "original-wpt"
    result = read(runtime / "BASELINE-RESULT.json")
    assert result["success"] and result["preservation_verified"]
    assert result["canonical_updated"] is False and result["browser_build_performed"] is False
    terminal = read(root / binding["terminal"])
    assert terminal == binding["terminal_record"] and terminal["exit_code"] == 0
    assert terminal["session_id"] == binding["session"] and terminal["terminal_chunk"] == binding["terminal_tool"]
    assert terminal["baseline_result_sha256"] == sha(runtime / "BASELINE-RESULT.json")
    assert terminal["exact_raw_replay"] and terminal["pre_post_equal"] and terminal["application_metadata_unchanged"]
    assert terminal["canonical_epoch_unchanged"]
    record = read(phase / "RESULT.json")
    assert record["success"] and record["preservation_verified"] and record["execution_error"] is None
    assert record["native_fix_acceptance"] is False
    assert read(phase / "PRE.json") == read(phase / "POST.json")
    cleanup = read(phase / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    owner = read(root / binding["owner_policy"])
    assert owner["head"] == policy["head"]
    before = read(runtime / "BASELINE-PRE.json")
    assert before["controls"] == owner["controls"]
    assert before["source_roles"] == read(root / binding["source_roles"])
    roles = before["source_roles"]
    source = "servo/components/style/values/generics/calc.rs"
    assert set(roles) == {source} and roles[source]["base_sha256"] == binding["source_sha256"]
    assert owner["accepted_current_payloads"][source]["sha256"] == binding["source_sha256"]
    assessment_policy = read(phase / "ASSESSMENT-POLICY.json")
    assert assessment_policy == phase_policy(owner["wpt"])
    assert assessment_policy["expected_subtest_count"] == 147
    assert assessment_policy["expected_target_count"] == 18
    assert assessment_policy["expected_control_count"] == 129
    assert assessment_policy["expected_page_count"] == 2
    assert assessment_policy["expected_regression_signature_count"] == 131
    assert sha(phase / "tests/css/css-values/pow-special-value-context.html") == binding["fixture_sha256"]
    assessor = load("checkpoint_pow_assessor", root / binding["assessor"])
    checks = load("checkpoint_pow_checks", root / binding["checks_helper"])
    ownership = load("checkpoint_pow_ownership", root / binding["ownership_helper"])
    ownership.group_absent(read(phase / "PROCESS.json")["pgid"])
    replay = assessor.assess([json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines()],
        record["exit"], assessment_policy, checks,
        run_binding=read(phase / "APPLICATION-METADATA.json"))
    assert json.loads(json.dumps(replay)) == read(phase / "ASSESSMENT.json")
    assert replay["complete"] and replay["errors"] == [] and replay["fixture_setup_errors"] == []
    assert replay["observed_subtest_count"] == len(replay["rows"]) == 147
    assert len(replay["regression_signature"]) == 131
    assert len(replay["ends"]) == 2 and all(row["status"] == "OK" for row in replay["ends"])
    assert result["phase"] == {"assessment_sha256": sha(phase / "ASSESSMENT.json"),
        "raw_sha256": sha(phase / "raw.jsonl"), "result_sha256": sha(phase / "RESULT.json")}
    statuses = {status: sum(row["status"] == status for row in replay["rows"]) for status in ("PASS", "FAIL")}
    return {"result_sha256": sha(runtime / "BASELINE-RESULT.json"),
        "assessment_sha256": sha(phase / "ASSESSMENT.json"), "raw_sha256": sha(phase / "raw.jsonl"),
        "source_sha256": binding["source_sha256"], "fixture_sha256": binding["fixture_sha256"],
        "callbacks": 147, "observed_statuses": statuses, "control_and_ending_signatures": 131,
        "candidate_execution": False, "native_acceptance": False}
