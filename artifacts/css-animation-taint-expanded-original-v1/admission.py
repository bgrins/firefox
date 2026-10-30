import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(directory, digest):
    assert sha(directory / "FILES.json") == digest
    for name, record in read(directory / "FILES.json").items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        target = directory / name
        assert not target.is_symlink() and target.is_file(), name
        assert sha(target) == (record if isinstance(record, str) else record["sha256"]), name
        if isinstance(record, dict):
            assert target.stat().st_size == record["bytes"], name


def check_binding(policy):
    for name, digest in policy["references"].items():
        assert name.startswith("artifacts/") and ".." not in Path(name).parts
        assert not (ROOT / name).is_symlink() and sha(ROOT / name) == digest, name
    predecessor = policy["implementation_predecessor"]
    directory = ROOT / predecessor["directory"]
    authenticate(directory, predecessor["manifest_sha256"])
    old = read(directory / "POLICY.json")
    spec = importlib.util.spec_from_file_location("original106_saved_binding", directory / "check.py")
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    previous.check_binding(old)
    for key in ("accepted_calc_sha256", "accepted_current_payloads", "build_epoch", "build_unpinned_sources", "deferred_nonartifact_references", "head", "original_only", "candidate_execution_enabled", "rebuilt_binaries", "source_admission", "source_role_pins", "state_helper", "wpt_helper"):
        assert policy[key] == old[key], key
    assert policy["original_only"] and policy["candidate_execution_enabled"] is False
    assert policy["activation_pending"] == ([] if policy["execution_enabled"] else ["root saved review and activation"])
    mutable = {"expected_control_count", "expected_page_count", "expected_regression_signature_count", "expected_subtest_count", "expected_subtests", "fixture_target_pages", "manifest", "metadata", "resources"}
    assert {k:v for k,v in policy["wpt"].items() if k not in mutable} == {k:v for k,v in old["wpt"].items() if k not in mutable}
    suite = ROOT / policy["suite"]["directory"]
    authenticate(suite, policy["suite"]["manifest_sha256"])
    union = read(suite / "UNION.json")
    roster = read(suite / "UNION-ROSTER.json")
    settings = policy["wpt"]
    assert roster == settings["expected_subtests"] == read(ROOT / policy["source_roster"])
    assert sum(map(len, roster.values())) == 120 and len(roster) == 16
    assert all(roster[page] == names for page, names in old["wpt"]["expected_subtests"].items())
    assert settings["resources"] == union["resources"]
    assert settings["target_subtests"] == {} and set(settings["fixture_target_pages"]) == set(roster)
    assert read(ROOT / settings["manifest"]["path"]) == read(suite / "UNION-MANIFEST.json")
    assert sha(ROOT / settings["manifest"]["path"]) == settings["manifest"]["sha256"]
    expected_metadata = copy.deepcopy(union["metadata_for_future_local_owner"])
    assert expected_metadata == old["wpt"]["metadata"]
    for page in read(suite / "ROSTER.json"):
        name = page.lstrip("/") + ".ini"
        expected_metadata[name] = {"path": "testing/web-platform/meta/" + name, "sha256": None, "status": "authored fixture metadata must remain absent at execution"}
    assert settings["metadata"] == expected_metadata
    for record in settings["resources"].values():
        assert sha(ROOT / record["path"]) == record["sha256"]
    verify_handoff(policy, old)


def verify_handoff(policy, old):
    binding = policy["restoration_handoff"]
    runtime = ROOT / binding["runtime"]
    authenticate(runtime, binding["manifest_sha256"])
    owner = ROOT / binding["owner"]
    authenticate(owner, binding["owner_manifest_sha256"])
    prior_policy = read(owner / "POLICY.json")
    terminal = read(runtime / "ROOT-TERMINAL.json")
    assert {k:terminal[k] for k in binding["terminal"]} == binding["terminal"]
    assert binding["terminal"] == {"owner_session": 46619, "owner_terminal": "b8e540", "owner_exit": 0, "review_session": 12635, "review_terminal": "298695", "review_exit": 0}
    review = read(runtime / "ROOT-REVIEW.json")
    assert terminal["review_sha256"] == sha(runtime / "ROOT-REVIEW.json")
    assert terminal["native_acceptance"] is False and review["native_acceptance"] is False
    assert review["owner_manifest_sha256"] == binding["owner_manifest_sha256"]
    assert review["actual_terminal"] == {"session": 46619, "terminal_chunk": "b8e540", "exit": 0, "result_sha256": sha(runtime / "CANDIDATE-RESULT.json")}
    for name, digest in review["input_hashes"].items():
        assert sha(runtime / name) == digest, name
    result = read(runtime / "CANDIDATE-RESULT.json")
    assert review["owner_result"] == result
    assert result["success"] and result["restoration_verified"] and result["error"] is None
    assert result["publication_errors"] == [] and result["native_fix_acceptance"] is False
    assert review["restoration_independently_verified"]
    assert review["backup"] == read(runtime / "BACKUP-CLEANUP.json") == {"owned_backup_bytes": 1008605176, "removed": True, "retained_after_failure": False, "verified_original_restoration": True}
    restoration = read(runtime / "RESTORATION.json")
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    before = read(runtime / "CANDIDATE-PRE.json")
    for name, record in before["sources"].items():
        expected = {"sha256": record["base_sha256"], "identity": record["identity"]}
        assert restoration["sources"][name] == review["source_identities"][name] == expected
        assert record["base_sha256"] == policy["source_role_pins"][name]
    assert set(before["sources"]) == set(restoration["sources"]) == set(review["source_identities"])
    refresh = read(runtime / "ROOT-EPOCH-REFRESH.json")
    assert refresh["independent_review_sha256"] == terminal["review_sha256"]
    assert refresh["independent_review_terminal"] == "12635/298695/0"
    assert refresh["only_changed_field"] == "raw_index_observation.current" and refresh["semantic_index_unchanged"]
    assert refresh["previous_epoch_sha256"] == before["controls"]["CURRENT-EPOCH.json"] == prior_policy["controls"]["CURRENT-EPOCH.json"]
    assert refresh["other_controls_unchanged"] == {k:v for k,v in before["controls"].items() if k != "CURRENT-EPOCH.json"}
    assert policy["controls"] == dict(refresh["other_controls_unchanged"], **{"CURRENT-EPOCH.json": refresh["new_epoch_sha256"]})
    after = read(runtime / "POST.json")
    assert after == review["snapshot"] and after["index"]["head"] == policy["head"]
    assert before["snapshot"]["index"]["raw_index"] == refresh["raw_index_before"]
    assert after["index"]["raw_index"] == refresh["raw_index_after"]
    adjusted = copy.deepcopy(before["snapshot"])
    adjusted["index"]["raw_index"] = refresh["raw_index_after"]
    assert adjusted == after
    assert prior_policy["baseline_capsule"] == {"directory": policy["implementation_predecessor"]["directory"], "sha256": policy["implementation_predecessor"]["manifest_sha256"]}
    baseline = prior_policy["baseline_binding"]
    assert baseline["directory"] == old["output"]
    authenticate(ROOT / baseline["directory"], baseline["manifest_sha256"])
    historical = read(ROOT / old["output"] / "POST.json")
    historical["index"]["raw_index"] = refresh["raw_index_after"]
    assert historical == after
    app = dict(review["restored_application_metadata"], build_revision=policy["wpt"]["phase_revisions"]["original"], harness_revision=policy["head"], source_role="original")
    assert app == policy["prepared_application_metadata"]
    without_identity = lambda value: {k:v for k,v in value.items() if k not in ("identity", "entry_identity")}
    assert without_identity(app) == without_identity(old["prepared_application_metadata"])
    assert app["revision"] == app["build_revision"]
    observation = review["observation"]
    assert observation["browser_executed"] and observation["observation_complete"]
    assert observation["build_exit"] == observation["browser_exit"] == 0
    assert observation["outcomes"] == read(runtime / "OUTCOMES.json")
    assert observation["outcomes"]["callbacks_passed"] == 106 and observation["outcomes"]["callbacks_failed"] == 0
    cohorts = observation["research_cohorts"]
    targets = cohorts["original_fail_research_targets"]
    preserved = cohorts["original_pass_controls"]
    assert len(targets) == 8 and len(preserved) == 98
    assert all(r["original"]["status"] == "FAIL" and r["candidate"]["status"] == "PASS" for r in targets)
    assert all(r["original"]["status"] == r["candidate"]["status"] == "PASS" and r["full_signature_unchanged"] for r in preserved)
