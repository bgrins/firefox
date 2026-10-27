import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "artifacts/css-attr-raw-nested-wpt-runtime-original-2"
PRIOR = ROOT / "artifacts/css-attr-raw-nested-wpt-runtime-original-1"
CAP = ROOT / "artifacts/css-attr-raw-nested-wpt-capsule-v3"
BUILD = ROOT / "artifacts/css-attr-raw-nested-native-runtime-v1/original-build-2"
CONTROLLER = BUILD.parent
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
    for name, value in read(directory / "FILES.json").items():
        assert sha(directory / name) == value

authenticate(CAP, "46eee2d63d2d063f4fdf5f1b48fb8dd9baf2e9d809511d7f46da3819f46caff5")
assert sha(RUN / "ASSESSMENT.json") == "db6c2726faabf8f6587582d4fa0d4f7f3ca9e1a5e2dd6c99a4c12a9f10a5bb45"
policy = read(CAP / "POLICY.json")
a, prior = read(RUN / "ASSESSMENT.json"), read(PRIOR / "ASSESSMENT.json")
result, command = read(RUN / "RESULT.json"), read(RUN / "COMMAND.json")
epoch, pre, post = read(RUN / "EPOCH.json"), read(RUN / "PRE.json"), read(RUN / "POST.json")
assert pre == post and pre["current_raw_stable_during_check"] and pre["working_sources_binaries_research_preserved"]
for name, key in [("index", "semantic_index"), ("nested_index", "nested_semantic_index")]:
    assert {k:v for k,v in pre[name].items() if k != "raw_index"} == epoch[key]
assert sha(RUN / "EPOCH.json") == command["epoch_sha256"] == a["epoch_sha256"]
assert a["capsule_manifest_sha256"] == command["wrapper_manifest_sha256"] == inputs[str((CAP / "FILES.json").relative_to(ROOT))]
assert a["phase"] == result["phase"] == command["phase"] == "original-2"
assert a["complete"] and a["execution_preserved"] and not a["comparison_gate_passed"]
assert result["observation_gate_passed"] and result["exit"] == 1
assert result["execution_error"] is None and result["preservation_error"] is None
assert not result["comparison_gate_passed"] and not result["native_fix_acceptance"]
transition = epoch["raw_attribute_transition"]
assert transition["role"] == "original" and transition["compiled"] is True
assert a["native_sources"] == policy["source_roles"]["original"]
assert all(epoch["pins"][n] == h for n,h in a["native_sources"].items())
binaries = read(RUN / "NORMAL-BINARIES.json")
assert all(epoch["pins"][n] == h for n,h in binaries.items())
app = read(RUN / "APPLICATION-METADATA.json")
assert app == read(RUN / "APPLICATION-METADATA-POST.json") == a["run_binding"]
assert app["revision"] == epoch["semantic_index"]["head"] == a["run_info"]["revision"]
assert app["browser_build_id"] == a["run_info"]["browser_build_id"]
assert app["entry_type"] == 40960 and app["symlink_target"] == app["resolved"]
input_pins = read(RUN / "INPUT-PINS.json")
assert input_pins[policy["application_ini"]] == app["sha256"]
assert set(read(RUN / "INDEX-FLAGS.json")) == {".", "artifacts/css-spec-lean"}
cleanup = read(RUN / "CLEANUP.json")
assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
owned = read(RUN / "OWNED-INPUT-PINS.json")
for name, digest in owned.items():
    path = RUN / name
    assert not path.is_symlink() and path.resolve().is_relative_to(RUN.resolve())
    assert sha(path) == digest
for name,item in read(CAP / "SOURCE-PINS.json").items():
    relative = Path(name.removeprefix("testing/web-platform/"))
    path = RUN / ("tests" if relative.parts[0] == "tests" else "metadata") / Path(*relative.parts[1:])
    assert path.exists() == item["exists"]
    if item["exists"]:
        assert sha(path) == item["sha256"] == input_pins[item["origin"]]
    else:
        assert input_pins[item["origin"]] is None
assert read(RUN / "metadata/MANIFEST.json") == read(CAP / "SUBSET-MANIFEST.json")
assert sorted(arg.removeprefix("--include=") for arg in command["command"] if arg.startswith("--include=")) == sorted(policy["tests"])
sha(RUN / "raw.jsonl")
events = [json.loads(line) for line in (RUN / "raw.jsonl").read_text().splitlines()]
checks = load("original_saved_checks", ROOT / policy["helpers"]["checks"])
parser = load("original_saved_assess", CAP / "assess.py")
recomputed = parser.assess(events, 1, policy, checks, run_binding=app)
assert recomputed["complete"]
assert all(a[k] == v for k,v in recomputed.items())
assert len(a["rows"]) == 402
assert len(a["starts"]) == len(a["ends"]) == 16
rows = {(r["test"], r["subtest"]):r for r in a["rows"]}
old_rows = {(r["test"], r["subtest"]):r for r in prior["rows"]}
target_rows = [r for r in a["rows"] if r["test"] in policy["target_subtests"]]
regression_rows = [r for r in a["rows"] if r["test"] not in policy["target_subtests"]]
assert Counter(r["status"] for r in target_rows) == {"PASS":56,"FAIL":17}
assert len(regression_rows) == 329 and all(r["status"] == "PASS" for r in regression_rows)
refs = [e for e in a["ends"] if policy["tests"][e["test"]] == "reftest"]
assert len(refs) == 6 and all(e["status"] == "PASS" for e in refs)
assert a["regression_signature"] == prior["regression_signature"]
changes = []
for identity, old in old_rows.items():
    new = rows[identity]
    if parser.signature(old) != parser.signature(new):
        changes.append({"test":identity[0],"subtest":identity[1],"before":parser.signature(old),"after":parser.signature(new)})
assert len(changes) == 1 and changes[0]["subtest"] == "CSS Values and Units Test: attr 28"
assert changes[0]["before"]["status"] == "PASS" and changes[0]["after"]["status"] == "FAIL"
new_identities = set(rows) - set(old_rows)
controls = read(ROOT / "artifacts/css-attr-raw-nested-repair-v2/EOF-CONTROLS.json")
raw_page = "/css/css-values/attr-raw-nested-cycle.html"
assert new_identities == {(raw_page,c["id"]) for c in controls}
new_controls = [{"id":c["id"],"status":rows[(raw_page,c["id"])]["status"],"message":rows[(raw_page,c["id"])].get("message")} for c in controls]
assert Counter(x["status"] for x in new_controls) == {"PASS":4,"FAIL":3}
assert {x["id"] for x in new_controls if x["status"] == "FAIL"} == {"eof-bare-self","eof-raw-string-self","raw-self-with-valid-trailing-value"}
old_failures = {identity for identity,row in old_rows.items() if row["status"] == "FAIL"}
assert len(old_failures) == 13 and all(rows[i]["status"] == "FAIL" for i in old_failures)
assert read(BUILD / "EPOCH.json") == epoch
build_result = read(BUILD / "RESULT.json")
assert build_result["command_success"] and build_result["preservation_verified"] and not build_result["error"] and not build_result["publication_errors"] and not build_result["owned_processes"]
assert build_result["source_role"] == "original"
for name in ["build-RESULT.json","WAKE-RESULT.json"]:
    item = read(BUILD / name)
    assert item["exit"] == 0 and item["owned_group_absent"]
for name in ["build-GROUP-CLEANUP.json","wake-GROUP-CLEANUP.json"]:
    assert read(BUILD / name)["owned_group_absent"]
for name in ["PRE.json","POST.json","COMMAND.json"]:
    read(BUILD / name)
restore = read(CONTROLLER / "original-second-EPOCH.json")
assert restore["raw_attribute_transition"]["role"] == "original" and restore["raw_attribute_transition"]["compiled"] is False
assert all(restore["pins"][n] == h for n,h in a["native_sources"].items())
assert restore["semantic_index"]["head"] == epoch["semantic_index"]["head"]
for name in ["original-second-PRE.json","original-second-POST.json","original-second.log"]:
    sha(CONTROLLER / name)
output = {"saved_observation_valid":True,"native_fix_acceptance":False,
          "target_statuses":{"PASS":56,"FAIL":17},"unchanged_regression_passes":329,"reftest_passes":6,
          "per_test":a["per_test"],"all17_failures":[r for r in target_rows if r["status"] == "FAIL"],
          "prior13_failures_retained":True,"sole_prior_identity_status_change":changes,
          "seven_new_controls":new_controls,"head":epoch["semantic_index"]["head"],
          "native_sources":a["native_sources"],"binary_pins":binaries,"application_metadata":app,
          "saved_pre_post_full_equal":True,"saved_build_epoch_equals_run_epoch":True,
          "saved_epoch_inventory_sizes":{k:len(epoch[k]) for k in ["pins","installed_identities","modified_native_paths","untracked_native","committed_research_working_payloads"]},
          "saved_cleanup":cleanup,"owned_inputs_authenticated":len(owned),
          "live_state_queried":False,"browser_or_build_executed":False,
          "limitation":"Full live preservation is attested by the completed wrapper/build records and authenticated epoch. This review recomputes saved evidence and copied inputs; it does not requery current source, binary, process or epoch state during the candidate transition."}
print(json.dumps({"audit":output,"input_hashes":inputs},indent=2,sort_keys=True))
