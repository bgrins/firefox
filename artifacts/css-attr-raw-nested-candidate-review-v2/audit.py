import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAP = ROOT / "artifacts/css-attr-raw-nested-wpt-capsule-v3"
CONTROL = ROOT / "artifacts/css-attr-raw-nested-native-runtime-v1"
inputs = {}
def sha(path):
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    inputs[str(path.relative_to(ROOT))] = value
    return value
def read(path):
    sha(path)
    return json.loads(path.read_text())
def load(name, path):
    sha(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def authenticate(directory, digest):
    assert sha(directory / "FILES.json") == digest
    for name,value in read(directory / "FILES.json").items():
        assert sha(directory / name) == value

capsule_digest = "46eee2d63d2d063f4fdf5f1b48fb8dd9baf2e9d809511d7f46da3819f46caff5"
authenticate(CAP, capsule_digest)
authenticate(ROOT / "artifacts/css-attr-raw-nested-original-review-v2", "11ebb4e46fa9118841a2cb0ed6866407866739f54b759127251c0976a82c12ed")
policy = read(CAP / "POLICY.json")
parser = load("paired_saved_assess", CAP / "assess.py")
checks = load("paired_saved_checks", ROOT / policy["helpers"]["checks"])
expected_digests = {"original":"db6c2726faabf8f6587582d4fa0d4f7f3ca9e1a5e2dd6c99a4c12a9f10a5bb45", "candidate":"15df580123ced4a08fd16dd3fefb1046f9e3bf7b2703eaeeccf80cc59c14897b"}
phases = {}
for role in ("original", "candidate"):
    run = ROOT / ("artifacts/css-attr-raw-nested-wpt-runtime-" + role + "-2")
    assert sha(run / "ASSESSMENT.json") == expected_digests[role]
    a, epoch = read(run / "ASSESSMENT.json"), read(run / "EPOCH.json")
    result, command = read(run / "RESULT.json"), read(run / "COMMAND.json")
    pre, post = read(run / "PRE.json"), read(run / "POST.json")
    assert pre == post and pre["current_raw_stable_during_check"] and pre["working_sources_binaries_research_preserved"]
    for field,key in [("index","semantic_index"),("nested_index","nested_semantic_index")]:
        assert {k:v for k,v in pre[field].items() if k != "raw_index"} == epoch[key]
    assert set(read(run / "INDEX-FLAGS.json")) == {".", "artifacts/css-spec-lean"}
    assert sha(run / "EPOCH.json") == command["epoch_sha256"] == a["epoch_sha256"]
    assert command["wrapper_manifest_sha256"] == a["capsule_manifest_sha256"] == capsule_digest
    assert command["phase"] == a["phase"] == result["phase"] == role + "-2"
    transition = epoch["raw_attribute_transition"]
    assert transition["role"] == role and transition["compiled"] is True
    assert a["native_sources"] == policy["source_roles"][role]
    assert all(epoch["pins"][name] == digest for name,digest in a["native_sources"].items())
    binaries = read(run / "NORMAL-BINARIES.json")
    assert all(epoch["pins"][name] == digest for name,digest in binaries.items())
    app = read(run / "APPLICATION-METADATA.json")
    assert app == read(run / "APPLICATION-METADATA-POST.json") == a["run_binding"]
    assert app["browser_build_id"] == a["run_info"]["browser_build_id"]
    assert app["revision"] == a["run_info"]["revision"] == epoch["semantic_index"]["head"]
    assert app["entry_type"] == 40960 and app["symlink_target"] == app["resolved"]
    resources, owned = read(run / "INPUT-PINS.json"), read(run / "OWNED-INPUT-PINS.json")
    assert resources[policy["application_ini"]] == app["sha256"]
    for name,digest in owned.items():
        path = run / name
        assert not path.is_symlink() and path.resolve().is_relative_to(run.resolve()) and sha(path) == digest
    for name,item in read(CAP / "SOURCE-PINS.json").items():
        relative = Path(name.removeprefix("testing/web-platform/"))
        path = run / ("tests" if relative.parts[0] == "tests" else "metadata") / Path(*relative.parts[1:])
        assert path.exists() == item["exists"]
        if item["exists"]:
            assert sha(path) == item["sha256"] == resources[item["origin"]]
        else:
            assert resources[item["origin"]] is None
    assert read(run / "metadata/MANIFEST.json") == read(CAP / "SUBSET-MANIFEST.json")
    assert sorted(arg.removeprefix("--include=") for arg in command["command"] if arg.startswith("--include=")) == sorted(policy["tests"])
    cleanup, process = read(run / "CLEANUP.json"), read(run / "PROCESS.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    assert process["pid"] == process["pgid"]
    assert result["execution_error"] is None and result["preservation_error"] is None
    assert a["complete"] and a["execution_preserved"] and result["observation_gate_passed"]
    assert result["exit"] == (1 if role == "original" else 0)
    sha(run / "raw.jsonl")
    events = [json.loads(line) for line in (run / "raw.jsonl").read_text().splitlines()]
    baseline = phases["original"]["assessment"] if role == "candidate" else None
    recomputed = parser.assess(events, result["exit"], policy, checks, baseline, app)
    assert all(a[k] == value for k,value in recomputed.items())
    assert len(a["rows"]) == 402 and len(a["starts"]) == len(a["ends"]) == 16
    if role == "candidate":
        assert a["comparison_gate_passed"] and result["comparison_gate_passed"] and not a["errors"] and not a["comparison_errors"]
        assert command["original_assessment_sha256"] == expected_digests["original"]
        assert command["original_assessment"] == str(ROOT / "artifacts/css-attr-raw-nested-wpt-runtime-original-2/ASSESSMENT.json")
    phases[role] = {"assessment":a,"epoch":epoch,"resources":resources,"owned":owned,"binaries":binaries,"application":app,"cleanup":cleanup}

original, candidate = phases["original"], phases["candidate"]
a, b = original["assessment"], candidate["assessment"]
assert a["regression_signature"] == b["regression_signature"]
assert original["epoch"]["semantic_index"]["head"] == candidate["epoch"]["semantic_index"]["head"]
assert {k:v for k,v in a["run_info"].items() if k != "browser_build_id"} == {k:v for k,v in b["run_info"].items() if k != "browser_build_id"}
resource_changes = [name for name in set(original["resources"]) | set(candidate["resources"]) if original["resources"].get(name) != candidate["resources"].get(name)]
assert resource_changes == [policy["application_ini"]]
assert {k:v for k,v in original["owned"].items() if k != "wptrunner.ini"} == {k:v for k,v in candidate["owned"].items() if k != "wptrunner.ini"}
old_rows = {(r["test"],r["subtest"]):r for r in a["rows"]}
new_rows = {(r["test"],r["subtest"]):r for r in b["rows"]}
assert old_rows.keys() == new_rows.keys()
repaired = []
for identity,row in new_rows.items():
    old = old_rows[identity]
    assert row["status"] == "PASS"
    if old["status"] == "FAIL":
        assert row["test"] in policy["target_subtests"]
        repaired.append({"test":identity[0],"subtest":identity[1],"before":parser.signature(old),"after":parser.signature(row),"original_message":old.get("message")})
    else:
        assert parser.signature(old) == parser.signature(row)
assert len(repaired) == 17
assert sum(r["test"] in policy["target_subtests"] for r in b["rows"]) == 73
assert sum(r["test"] not in policy["target_subtests"] for r in b["rows"]) == 329
refs = [e for e in b["ends"] if policy["tests"][e["test"]] == "reftest"]
assert len(refs) == 6 and all(e["status"] == "PASS" for e in refs)
cycle = "/css/css-values/attr-cycle.html"
oracle_rows = [r for r in repaired if r["test"] == cycle]
assert {r["subtest"] for r in oracle_rows} == {"CSS Values and Units Test: attr 3","CSS Values and Units Test: attr 28","CSS Values and Units Test: attr 29"}
controls = read(ROOT / "artifacts/css-attr-raw-nested-repair-v2/EOF-CONTROLS.json")
eof_results = [{"id":c["id"],"original":old_rows[("/css/css-values/attr-raw-nested-cycle.html",c["id"])]["status"],"candidate":new_rows[("/css/css-values/attr-raw-nested-cycle.html",c["id"])]["status"]} for c in controls]

build = CONTROL / "candidate-build-2"
assert read(build / "EPOCH.json") == candidate["epoch"]
build_result = read(build / "RESULT.json")
assert build_result["command_success"] and build_result["preservation_verified"] and not build_result["error"] and not build_result["publication_errors"] and not build_result["owned_processes"]
assert build_result["source_role"] == "candidate"
for name in ["build-RESULT.json","WAKE-RESULT.json"]:
    item = read(build / name)
    assert item["exit"] == 0 and item["owned_group_absent"]
for name in ["build-GROUP-CLEANUP.json","wake-GROUP-CLEANUP.json"]:
    assert read(build / name)["owned_group_absent"]
for name in ["PRE.json","POST.json","COMMAND.json"]:
    read(build / name)
sha(build / "build.log")
log = (build / "build.log").read_text()
assert "0:48.79 Your build was successful!" in log
transition_epoch = read(CONTROL / "candidate-second-EPOCH.json")
assert transition_epoch["raw_attribute_transition"]["role"] == "candidate" and transition_epoch["raw_attribute_transition"]["compiled"] is False
assert all(transition_epoch["pins"][n] == h for n,h in b["native_sources"].items())
assert transition_epoch["semantic_index"]["head"] == candidate["epoch"]["semantic_index"]["head"]

carry = read(CONTROL / "GTEST-CARRYFORWARD-2.json")
gtest = CONTROL / "candidate-gtest-1"
gtest_epoch = read(gtest / "EPOCH.json")
assert carry["current_epoch_sha256"] == b["epoch_sha256"]
assert carry["prior_gtest_epoch_sha256"] == sha(gtest / "EPOCH.json")
assert len(carry["source_pins"]) == carry["source_roles_equal"] == 206
for name,digest in carry["source_pins"].items():
    assert gtest_epoch["pins"][name] == candidate["epoch"]["pins"][name] == digest
assert len(carry["gtest_library_pins"]) == 2
for name,digest in carry["gtest_library_pins"].items():
    assert gtest_epoch["pins"][name] == candidate["epoch"]["pins"][name] == digest
assert carry["fresh_gtest_execution"] is False and carry["normal_browser_binaries_rebuilt"] is True
assert all(gtest_epoch["pins"][name] != digest for name,digest in candidate["binaries"].items())
gtest_check = read(ROOT / carry["prior_result"])
assert sha(ROOT / carry["prior_result"]) == carry["prior_result_sha256"]
assert gtest_check["all_pass"] and gtest_check["suites"] == 4 and gtest_check["failures"] == gtest_check["disabled"] == 0
assert len(gtest_check["tests"]) == 20
assert sha(gtest / "build.log") == gtest_check["log_sha256"]
gtest_log = (gtest / "build.log").read_text()
starts = re.findall(r"TEST_START: ([^\n]+)",gtest_log)
ends = re.findall(r"TEST_END: ([^\n]+)",gtest_log)
assert Counter(starts) == Counter(gtest_check["tests"]) and ends == ["PASS"] * 20
assert "Ran 20 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s)." in gtest_log
assert read(gtest / "RESULT.json")["command_success"]
assert read(gtest / "build-RESULT.json")["exit"] == 0
output = {"paired_comparison_passes":True,"native_fix_acceptance_action_performed":False,
          "target_passes":73,"unchanged_regression_passes":329,"reftest_passes":6,"repaired_assertions":repaired,
          "explicit_three_oracle_corrections":oracle_rows,"eof_controls":eof_results,
          "per_test":b["per_test"],"head":b["run_info"]["revision"],
          "native_sources":{role:item["assessment"]["native_sources"] for role,item in phases.items()},
          "normal_browser_binaries":{role:item["binaries"] for role,item in phases.items()},
          "application_metadata":{role:item["application"] for role,item in phases.items()},
          "only_cross_phase_resource_difference":resource_changes,
          "all_saved_owned_tests_metadata_references_identical":True,
          "saved_pre_post_full_equal_each_phase":True,"saved_build_epoch_equals_candidate_run_epoch":True,
          "saved_cleanup":{role:item["cleanup"] for role,item in phases.items()},
          "build_log_progress_monitor_KeyError_export_count":log.count("KeyError: 'export'"),
          "build_success_elapsed_seconds":48.79,
          "gtest_carry_forward":{"source_roles":206,"identical_libraries":carry["gtest_library_pins"],"previous_passing_tests":gtest_check["tests"],"fresh_execution":False,"normal_binaries_changed_and_separately_WPT_tested":True},
          "live_state_queried":False,"browser_or_build_executed":False,
          "limitation":"Saved wrapper/build records attest full live preservation; this audit independently recomputes raw assessment and saved pins/copies without querying active source, binary, process, HEAD or CURRENT-EPOCH state."}
print(json.dumps({"audit":output,"input_hashes":inputs},indent=2,sort_keys=True))
