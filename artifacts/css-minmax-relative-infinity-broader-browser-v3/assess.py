from collections import Counter
import copy
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("minmax_discovery_base", Path(__file__).with_name("assess-base.py"))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
signature = base.signature
bound_run_info = base.bound_run_info


def assess(events, code, policy, checks, original=None, run_binding=None):
    assert original is None, "Discovery cannot authorize a candidate comparison"
    assert policy["roster_mode"] == "original-discovery"
    assert isinstance(run_binding, dict) and run_binding.get("source_role") == "original"
    known = policy["known_subtests"]
    unknown = policy["discovery_pages"]
    pages = set(policy["tests"])
    assert len(pages) == 12 and len(known) == 5 and len(unknown) == len(set(unknown)) == 7
    assert set(known).isdisjoint(unknown) and set(known) | set(unknown) == pages
    assert all(names and len(names) == len(set(names)) for names in known.values())
    assert all(policy["expected_subtests"][page] == known.get(page, []) for page in pages)
    assert all(policy[key] is None for key in ("expected_subtest_count", "expected_control_count", "expected_regression_signature_count"))
    rows = [event for event in events if event.get("action") == "test_status"]
    observed = {page: [row.get("subtest") for row in rows if row.get("test") == page] for page in pages}
    resolved = copy.deepcopy(policy)
    resolved["expected_subtests"] = {page: list(known[page]) if page in known else
                                     [name for name in observed[page] if isinstance(name, str)]
                                     for page in policy["tests"]}
    targets = {(page, name) for page, names in policy["target_subtests"].items() for name in names}
    assert len(targets) == policy["expected_target_count"] == 14
    assert all(page in known and name in known[page] for page, name in targets)
    expected = {(page, name) for page, names in resolved["expected_subtests"].items() for name in names}
    resolved["regression_subtests"] = {page: [name for name in names if (page, name) not in targets]
                                      for page, names in resolved["expected_subtests"].items()}
    resolved["expected_subtest_count"] = len(expected)
    resolved["expected_control_count"] = len(expected - targets)
    resolved["expected_regression_signature_count"] = len(expected - targets) + len(pages)
    result = base.assess(events, code, resolved, checks, run_binding=run_binding)
    if any(Counter(observed[page]) != Counter(names) for page, names in known.items()):
        result["errors"].append("known authored roster changed")
    if any(not observed[page] for page in unknown):
        result["errors"].append("a DOM-discovered page has no completed callbacks")
    result["complete"] = not result["errors"]
    result["comparison_gate_passed"] = False
    result["discovered_subtests"] = observed if result["complete"] else None
    result["roster_requires_seal_before_candidate"] = True
    result["subtest_cardinality_policy"] = "Five exact authored rosters; seven original-browser-discovered rosters; no predeclared aggregate count."
    result["oracle_caveat"] = "Original observation only. Twelve complete page lifecycles and known rosters are required. An omitted callback on a previously unknown page cannot be detected by an independent count yet. Seal and review actual names and full signatures before candidate comparison."
    return result
