from collections import Counter
import json


def signature(event):
    return {"kind": event["action"], "test": event["test"],
            "subtest": event.get("subtest"), "status": event["status"],
            "expected": event.get("expected", event["status"]),
            "expected_field_present": "expected" in event,
            "known_intermittent": event.get("known_intermittent", []),
            "intermittent_field_present": "known_intermittent" in event,
            "message": event.get("message"), "message_field_present": "message" in event}


def bound_run_info(run_info, binding):
    return (isinstance(run_info, dict) and isinstance(binding, dict)
            and isinstance(binding.get("sha256"), str) and len(binding["sha256"]) == 64
            and isinstance(binding.get("path"), str) and bool(binding["path"])
            and isinstance(binding.get("resolved"), str) and bool(binding["resolved"])
            and isinstance(binding.get("browser_build_id"), str) and bool(binding["browser_build_id"])
            and isinstance(binding.get("revision"), str) and len(binding["revision"]) == 40
            and run_info.get("browser_build_id") == binding["browser_build_id"]
            and isinstance(binding.get("harness_revision"), str) and len(binding["harness_revision"]) == 40
            and binding.get("build_revision") == binding["revision"]
            and run_info.get("revision") == binding["harness_revision"])


def bound_phase(run_info, binding, policy, role):
    if role not in ("original", "candidate") or not bound_run_info(run_info, binding):
        return False
    lineage = policy.get("phase_lineages", {}).get(role)
    expected = policy.get("phase_metadata", {}).get(role)
    return (isinstance(lineage, dict) and binding == expected
            and binding.get("source_role") == role
            and binding.get("revision") == binding.get("build_revision") == lineage.get("build_revision")
            and binding.get("revision") == policy.get("phase_revisions", {}).get(role)
            and binding.get("harness_revision") == lineage.get("harness_revision"))


def assess(events, code, policy, checks, original=None, run_binding=None):
    tests = policy["tests"]
    targets = policy["target_subtests"]
    held = policy["held_subtests"]
    rows = [e for e in events if e.get("action") == "test_status"]
    starts = [e for e in events if e.get("action") == "test_start"]
    ends = [e for e in events if e.get("action") == "test_end"]
    suites = [e for e in events if e.get("action") == "suite_start"]
    errors = []
    expected_ids = {(test, name) for test, names in policy['expected_subtests'].items() for name in names}
    target_ids = {(test, name) for test, names in targets.items() for name in names}
    declared_controls = {(test, name) for test, names in policy['regression_subtests'].items() for name in names}
    if (len(tests) != policy['expected_page_count'] or len(expected_ids) != policy['expected_subtest_count']
            or len(target_ids) != policy['expected_target_count']
            or len(expected_ids - target_ids) != policy['expected_control_count']
            or not target_ids <= expected_ids or declared_controls != expected_ids - target_ids
            or held):
        errors.append('declared min/max roster partition/counts differ')
    fixture_setup_errors = [signature(row) for row in rows
                            if row.get("test") in policy["fixture_target_pages"]
                            and row.get("status") == "FAIL"
                            and any(token in (row.get("message") or "") for token in
                                    ("Unhandled rejection", "TypeError:", "ReferenceError:", "SyntaxError:", "RangeError:"))]
    if fixture_setup_errors:
        errors.append("new target fixture has an uncaught setup/runtime exception")
    config = {"expected_subtests": {t: [] for t, kind in tests.items() if kind == "testharness"},
              "reftests": [t for t, kind in tests.items() if kind == "reftest"]}
    if not checks.lifecycle(events, config):
        errors.append("incomplete or invalid ordered lifecycle")
    if len(starts) != len(tests) or len(ends) != len(tests):
        errors.append("each selected test must start and end exactly once")
    identities = [(r.get("test"), r.get("subtest")) for r in rows]
    if len(identities) != len(set(identities)):
        errors.append("duplicate subtest identity")
    if any(not isinstance(r.get("subtest"), str) or
           tests.get(r.get("test")) != "testharness" or r.get("status") not in ("PASS", "FAIL")
           for r in rows):
        errors.append("invalid subtest identity or non-completed status")
    for test, kind in tests.items():
        test_rows = [r for r in rows if r.get("test") == test]
        if kind == "testharness" and not test_rows:
            errors.append("selected testharness has no subtests: " + test)
    for end in ends:
        allowed = ("OK",) if tests.get(end.get("test")) == "testharness" else ("PASS", "FAIL")
        if end.get("status") not in allowed:
            errors.append("non-completed test end: " + str(end.get("test")))
    candidate = [r for r in rows if (r.get("test"), r.get("subtest")) in target_ids]
    if len(rows) != policy['expected_subtest_count'] or len(candidate) != policy['expected_target_count']:
        errors.append('observed callback/target counts differ from the declared lane')
    for test, expected in policy["expected_subtests"].items():
        if Counter(r.get("subtest") for r in rows if r.get("test") == test) != Counter(expected):
            errors.append("fixture identities/cardinality differ: " + test)
    run_info = suites[0].get("run_info") if len(suites) == 1 else None
    if not isinstance(run_info, dict) or not {"os", "debug"} <= set(run_info):
        errors.append("missing platform/build run_info")
    if (not isinstance(run_binding, dict)
            or not bound_phase(run_info, run_binding, policy, run_binding.get("source_role"))
            or run_binding.get("harness_revision") != policy["harness_revision"]):
        errors.append("independent harness HEAD or application build lineage mismatch")
    if not bound_run_info(run_info, run_binding):
        errors.append("run_info BuildID/revision not bound to phase application metadata and epoch")
    faults = checks.infrastructure_faults(events)
    if faults:
        errors.append("infrastructure faults")
    if not checks.exit_matches_results(code, rows + ends):
        errors.append("exit status inconsistent with observed outcomes")
    unexpected = [e for e in rows + ends
                  if e["status"] != e.get("expected", e["status"])
                  and e["status"] not in e.get("known_intermittent", [])]
    held_signature = []
    for event in rows + ends:
        if event.get("test") not in held:
            continue
        item = signature(event)
        item.update(message=event.get("message"), message_field_present="message" in event)
        held_signature.append(item)
        if event.get("action") == "test_status" and event.get("status") == "FAIL":
            try:
                message = event["message"]
                observations, _ = json.JSONDecoder().raw_decode(message.split("observed=", 1)[1])
                if not isinstance(observations, list) or len(observations) != 2 or not all(isinstance(item, dict) and item for item in observations):
                    raise ValueError("two nonempty snapshots required")
            except (KeyError, IndexError, TypeError, ValueError):
                errors.append("held failure lacks complete mutation observation: " + event["subtest"])
    held_signature.sort(key=lambda e: (e["test"], e["kind"], e["subtest"] or ""))
    regression = [signature(e) for e in rows + ends if (e.get("action") == "test_end" or (e.get("test"), e.get("subtest")) not in target_ids) and e.get("test") not in held]
    regression.sort(key=lambda e: (e["test"], e["kind"], e["subtest"] or ""))
    if len(regression) != policy['expected_regression_signature_count']:
        errors.append('min/max control/ending signature count differs')
    comparison_errors = []
    if original is not None:
        if not original.get("complete"):
            comparison_errors.append("original observation incomplete")
        if held_signature != original.get("held_signature"):
            comparison_errors.append("held scheduling observations/status/messages changed")
        if regression != original.get("regression_signature"):
            comparison_errors.append("regression identities/status/expectations/intermittents changed")
        if not bound_run_info(original.get("run_info"), original.get("run_binding")):
            comparison_errors.append("original run_info lacks matching metadata/epoch binding")
        pair_bound = (bound_phase(original.get("run_info"), original.get("run_binding"), policy, "original")
                      and bound_phase(run_info, run_binding, policy, "candidate"))
        if not pair_bound:
            comparison_errors.append("phase metadata differs from authenticated per-role build/harness lineage")
        if isinstance(run_info, dict) and isinstance(original.get("run_info"), dict):
            ignored = {"browser_build_id", "revision"} if pair_bound else {"browser_build_id"}
            current_stable = {k: v for k, v in run_info.items() if k not in ignored}
            original_stable = {k: v for k, v in original["run_info"].items() if k not in ignored}
            if current_stable != original_stable:
                comparison_errors.append("run_info changed outside independently bound phase metadata")
        current_rows = {(r.get("test"), r.get("subtest")): signature(r) for r in rows}
        for row in original.get("rows", []):
            if row.get("status") == "PASS" and current_rows.get((row.get("test"), row.get("subtest"))) != signature(row):
                comparison_errors.append("originally passing callback signature changed: " + row["subtest"])
        if any(r.get("status") != "PASS" for r in rows if r.get("test") in policy["candidate_required_pass_pages"]):
            comparison_errors.append("all callbacks on declared required-pass pages must pass")
        if any(r.get("status") != "PASS" for r in candidate):
            comparison_errors.append("candidate target fixture still fails")
    return {"complete": not errors, "errors": errors, "fixture_setup_errors": fixture_setup_errors, "run_info": run_info, "run_binding": run_binding,
            "observed_subtest_count": len(rows), "rows": rows, "starts": starts, "ends": ends,
            "per_test": {test: {"type": kind,
                        "subtests": dict(Counter(r["status"] for r in rows if r["test"] == test)),
                        "completion": [e["status"] for e in ends if e["test"] == test]}
                         for test, kind in tests.items()},
            "unexpected": unexpected, "infrastructure_faults": faults,
            "regression_signature": regression, "held_signature": held_signature, "comparison_errors": comparison_errors,
            "comparison_gate_passed": original is not None and not errors and not comparison_errors,
            "subtest_cardinality_policy": policy["cardinality_description"],
            "oracle_caveat": "When an original is supplied, declared targets and required-pass pages must pass; declared control callbacks and all page endings preserve original full signatures. This candidate-only run supplies no original to the assessor; independent saved comparison is required. Original assertion failures remain observations, not infrastructure failures."}
