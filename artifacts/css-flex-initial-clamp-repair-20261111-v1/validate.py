import hashlib
import json
from pathlib import Path
import re
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def read(name):
    return json.loads((HERE / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

final_pins = read("AFTER-EXPANDED.json")
for name, expected in {**final_pins, **read("PROTECTED.json")}.items():
    assert sha(ROOT / name) == expected, name
for name, expected in read("BEFORE.json").items():
    if expected is not None:
        assert sha(HERE / "before" / name) == expected
assert final_pins["layout/generic/nsFlexContainerFrame.cpp"] == "f1df613c89d38ca0d7f7dbe9d18e71da2908dd5ffdb79882cfbc1987e9f29d06"
assert read("AFTER.json")["layout/generic/nsFlexContainerFrame.cpp"] == final_pins["layout/generic/nsFlexContainerFrame.cpp"]
original = (HERE / "after/dom/flex/test/chrome/test_flex_item_initial_clamp.html").read_text()
expanded = (ROOT / "dom/flex/test/chrome/test_flex_item_initial_clamp.html").read_text()
names = lambda s: re.findall(r'\{ name: "([^"]+)"', s)
assert len(names(original)) == 12 and names(expanded)[:12] == names(original) and len(names(expanded)) == 16
for line in original.splitlines():
    if '{ name: "' in line:
        assert line in expanded.splitlines()
manifest = tomllib.loads((ROOT / "dom/flex/test/chrome.toml").read_text())
old_manifest = tomllib.loads((HERE / "before/dom/flex/test/chrome.toml").read_text())
new_test = "chrome/test_flex_item_initial_clamp.html"
assert set(manifest) == set(old_manifest) | {new_test}
assert {k: v for k, v in manifest.items() if k != new_test} == old_manifest

original_failures = {d + " auto " + c + " clamp state" for d in ["column", "column reverse"] for c in ["below max", "below min", "equal max"]}
extra_failures = {d + " explicit automatic min clamp state" for d in ["row", "column", "column reverse"]} | {d + " " + c + " clamp state" for d in ["column", "column reverse"] for c in ["equal bounds", "conflicting bounds", "base equals both bounds"]}
results = {}
labels = {}
for stage, count, fails, child in [("baseline",108,original_failures,1),("baseline-expanded",144,original_failures|extra_failures,1),("focused",144,set(),0),("all-chrome",682,set(),0)]:
    events = [json.loads(line) for line in (HERE / stage / "raw.log").read_text().splitlines()]
    statuses = [e for e in events if e["action"] == "test_status"]
    ends = [e for e in events if e["action"] == "test_end"]
    assert len(statuses) == count
    assert all(e["status"] in ["PASS","FAIL"] for e in statuses)
    actual_failures = {e["message"].split(" - got ")[0] for e in statuses if e["status"] == "FAIL"}
    assert actual_failures == fails
    assert sum(e["status"] == "FAIL" for e in statuses) == len(fails)
    assert all(e["status"] == ("FAIL" if fails else "PASS") for e in ends)
    if stage == "all-chrome":
        expected_tests = {"dom/flex/test/" + k for k in manifest if k != "DEFAULT"}
        assert len(ends) == len(expected_tests) == 8 and {e["test"] for e in ends} == expected_tests
    else:
        assert len(ends) == 1 and ends[0]["test"] == "dom/flex/test/" + new_test
        labels[stage] = [e["message"].split(" - got ")[0] for e in statuses]
        assert len(set(labels[stage])) == count
    commands = read(stage + "/COMMANDS.json")
    assert len(commands) == 1 and commands[0]["exit"] == child
    assert commands[0]["argv"] == read(stage + "/COMMAND.json")
    assert read(stage + "/BINARY-BEFORE.json") == read(stage + "/BINARY-AFTER.json")
    results[stage] = {"assertions": count, "PASS": count-len(fails), "FAIL":len(fails), "files":len(ends), "child_exit":child}
assert labels["baseline-expanded"] == labels["focused"]
assert set(labels["baseline"]) <= set(labels["baseline-expanded"])
assert read("baseline/BINARY-AFTER.json") == read("baseline-expanded/BINARY-BEFORE.json") == read("build/BINARY-BEFORE.json")
assert read("build/BINARY-BEFORE.json") != read("build/BINARY-AFTER.json")
assert read("build/BINARY-AFTER.json") == read("focused/BINARY-BEFORE.json") == read("all-chrome/BINARY-BEFORE.json")
for stage in ["build", "format", "lint"]:
    commands = read(stage + "/COMMANDS.json")
    assert len(commands) == 1 and commands[0]["exit"] == 0
    assert commands[0]["argv"] == read(stage + "/COMMAND.json")
for stage, result in read("FINAL-ABSENCE.json").items():
    assert result["killpg_absent"] and not result["ps_matches"]
    assert result["group"] == read(stage + "/COMMANDS.json")[0]["pgid"]
assert len(read("FINAL-ABSENCE.json")) == 7
patch = read("FINAL-PATCH-CHECK.json")
assert patch["status"] == "PASS" and patch["exact_roundtrip"] and patch["scratch_removed"]
assert len(patch["commands"]) == 8 and all(c["exit"] == 0 for c in patch["commands"])
print(json.dumps({"status":"PASS_LOCAL_VALIDATION", "tests":results,"all_current_source_pins_match":True,"final_patch_sha256":sha(HERE/"standalone-expanded.patch"),"format_changed_bytes":False,"fresh_groups_absent":7,"root_acceptance":"pending independent root audit"},indent=2))
