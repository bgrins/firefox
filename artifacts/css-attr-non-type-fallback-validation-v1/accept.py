import hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / "artifacts/css-attr-non-type-fallback-native-runtime-v2"
spec = importlib.util.spec_from_file_location("fallback_state", RUNTIME / "state.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
def ref(name):
    p = ROOT / name
    return {"path": name, "sha256": s.sha(p)}
epoch = s.read(RUNTIME / "CURRENT-EPOCH.json")
s.a.verify_current(s.h, ROOT, s.ENV, epoch)
original = s.read(ROOT / "artifacts/css-attr-non-type-fallback-wpt-runtime-original-1/ASSESSMENT.json")
candidate = s.read(ROOT / "artifacts/css-attr-non-type-fallback-wpt-runtime-candidate-1/ASSESSMENT.json")
assert original["complete"] and original["execution_preserved"]
assert candidate["complete"] and candidate["execution_preserved"] and candidate["comparison_gate_passed"]
assert original["regression_signature"] == candidate["regression_signature"]
review = s.read(ROOT / "artifacts/css-attr-non-type-fallback-candidate-review-v1/AUDIT.json")
assert review["status"] == "SAVED_CANDIDATE_AND_COMPARISON_INTERNALLY_CONSISTENT"
assert review["new_test_statuses"] == {"PASS": 34}
assert len(review["changed_subtests_fail_to_pass"]) == 19
assert review["existing_subtests_passed"] == 154 and review["reftests_passed"] == 6
assert s.read(RUNTIME / "candidate-build-1/RESULT.json")["command_success"]
assert s.read(HERE / "MACH-LINT.json")["exit"] == 0
assert s.read(HERE / "INSTALL.json")["sha256"] == "6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3"
assert epoch["attribute_fallback_transition"]["role"] == "candidate" and epoch["attribute_fallback_transition"]["compiled"]
assert candidate["native_sources"] == {n: epoch["pins"][n] for n in candidate["native_sources"]}
result = {"status": "READY_FOR_STANDALONE_SIGNED_COMMIT", "fix": 137, "title": "Include used non-type attr fallbacks in dependency cycles", "phase_order": ["original-1", "candidate-1"], "phase_counts": [[15, 19], [34, 0]], "observed_repairs": 19, "unchanged_controls": 15, "existing_regressions": {"subtests_PASS": 154, "reftests_PASS": 6, "exact_both_phases": True}, "terminal_review": ref("artifacts/css-attr-non-type-fallback-candidate-review-v1/AUDIT.json"), "native_paths": ["servo/components/style/custom_properties.rs", "servo/components/style/properties/cascade.rs", "testing/web-platform/tests/css/css-values/attr-non-type-used-fallback-cycle.html"], "validated_patch": ref("artifacts/css-attr-non-type-fallback-repair-v3/fix-head.patch"), "upstream_export": ref("artifacts/css-attr-non-type-fallback-upstream-v1/upstream-self-contained.patch"), "upstream_build_validated": False, "numeric_overlap_commit": "499c0c6b72ac4bc0a6396bffa3fa0d71665409ce", "canonical_lean_increment": 0, "native_refinement_proved": False, "discovery": "Source audit and browser reproduction during formal-verification work", "epoch_at_acceptance_sha256": s.sha(RUNTIME / "CURRENT-EPOCH.json"), "head_at_validation": candidate["run_info"]["revision"]}
s.save(HERE / "ACCEPTANCE.json", result)
print("Fix 137 ready for standalone signed native-plus-WPT commit", flush=True)
