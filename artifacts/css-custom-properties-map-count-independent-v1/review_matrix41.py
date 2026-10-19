from pathlib import Path
import collections
import hashlib
import json

r = Path(__file__).resolve().parent
folder = r / "matrix41"
build = json.loads((folder / "BUILD-MATRIX.json").read_text())
assert build["combined_source_restored"] is True
builds = {x["variant"]: x for x in build["runs"]}
assert list(builds) == ["original", "count-only", "combined"]
sources = json.loads((folder / "SOURCE-PINS.json").read_text())
expected_counts = {
    "/css/css-variables/invalid-custom-property-enumeration.html": 10,
    "/css/css-variables/resurrected-custom-property-enumeration.html": 2,
    "/css/css-variables/custom-property-enumeration-shadowing.html": 7,
    "/css/cssom/cssstyledeclaration-custom-properties.html": 1,
    "/css/cssom/cssstyledeclaration-registered-custom-properties.html": 2,
    "/css/css-properties-values-api/registered-inherit-invalid.html": 12,
    "/css/css-properties-values-api/registered-substituted-inherit-restyle.html": 7,
}
summary = {}
identity = None
stable = None
for variant in builds:
    rows = [json.loads(line) for line in (folder / (variant + "-raw.json")).read_text().splitlines()]
    tests = [x for x in rows if x["action"] == "test_status"]
    ends = [x for x in rows if x["action"] == "test_end"]
    keys = {(x["test"], x["subtest"]) for x in tests}
    assert len(tests) == len(keys) == 41
    assert dict(collections.Counter(x["test"] for x in tests)) == expected_counts
    assert len(ends) == 7 and {x["test"] for x in ends} == set(expected_counts)
    assert all(x["status"] == "OK" for x in ends)
    assert all(x["status"] in {"PASS", "FAIL"} for x in tests)
    assert sum(x["action"] == "suite_end" for x in rows) == 1
    terminal = next(i for i, x in enumerate(rows) if x["action"] == "suite_end")
    assert all(i < terminal for i, x in enumerate(rows) if x["action"] in {"test_status", "test_end"})
    if identity is not None:
        assert identity == keys
    identity = keys
    run = json.loads((folder / (variant + "-RUN.json")).read_text())
    assert run["variant"] == variant and run["stable_after"] is True
    assert run["head"] == build["head"]
    assert run["exit"] in {0, 1}
    native = "servo/components/style/custom_properties_map.rs"
    assert run["pins"][native] == sources[variant] == builds[variant]["source"]
    assert builds[variant]["build_exit"] == builds[variant]["runner_exit"] == 0
    for name in ("firefox", "XUL"):
        assert run["pins"]["objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + name] == builds[variant]["binaries"][name]
    other = {p: h for p, h in run["pins"].items() if p != native and not p.startswith("objdir-full.noindex/")}
    if stable is not None:
        assert other == stable
    stable = other
    assert all(run["pins"][p] == h for p, h in build["stable_sources_tests"].items())
    summary[variant] = {"statuses": dict(collections.Counter(x["status"] for x in tests)), "harnesses": 7,
                        "failures": [{"test": x["test"], "subtest": x["subtest"], "message": x.get("message")} for x in tests if x["status"] == "FAIL"],
                        "source": sources[variant], "wpt_exit": run["exit"]}
assert summary["combined"]["statuses"] == {"PASS": 41}
assert summary["combined"]["wpt_exit"] == 0
original_fail = {(x["test"], x["subtest"]) for x in summary["original"]["failures"]}
count_fail = {(x["test"], x["subtest"]) for x in summary["count-only"]["failures"]}
assert count_fail <= original_fail
print(json.dumps({"runs": summary, "same_41_case_roster": True, "same_nonvariant_pins": True,
                  "all_builds_exit_zero": True, "count_only_no_new_failing_row": True,
                  "source_pin_present_in_all_variants": True,
                  "limits": "Local shared-tree association, not isolated upstream runtime or universal behavior."}, indent=2))
