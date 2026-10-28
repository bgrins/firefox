import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAP = ROOT / "artifacts/css-registered-number-wpt-capsule-v5"
ORIGINAL = ROOT / "artifacts/css-registered-number-wpt-runtime-original-2"
CANDIDATE = ROOT / "artifacts/css-registered-number-wpt-runtime-candidate-2"
refs = {}

def raw(path):
    data = path.read_bytes()
    refs[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return data

def read(path):
    return json.loads(raw(path))

policy = read(CAP / "POLICY.json")
groups = [policy[x] for x in ["target_subtests", "held_subtests", "regression_subtests"]]
identities = [{(test, name) for test, names in group.items() for name in names} for group in groups]
assert list(map(len, identities)) == [104, 16, 446]
assert sum(map(len, identities)) == len(set.union(*identities))
phases = []
fields = ["status", "expected", "known_intermittent", "message"]
def signature(event):
    return {k: event[k] for k in fields if k in event}

for directory, role, expected_head in [(ORIGINAL, "original", policy["original_frozen_head"]), (CANDIDATE, "candidate", policy["frozen_head"])]:
    result, assessment, epoch = [read(directory / name) for name in ["RESULT.json", "ASSESSMENT.json", "EPOCH.json"]]
    events = [json.loads(line) for line in raw(directory / "raw.jsonl").decode().splitlines()]
    rows, starts, ends = {}, [], {}
    for event in events:
        action = event["action"]
        if action == "test_status":
            key = (event["test"], event["subtest"])
            assert key not in rows
            rows[key] = event
        elif action == "test_start":
            starts.append(event["test"])
        elif action == "test_end":
            assert event["test"] not in ends
            ends[event["test"]] = event
        assert action not in ["crash", "process_crash"]
    assert set(rows) == set.union(*identities)
    assert len(starts) == len(set(starts)) == len(ends) == 23
    assert set(starts) == set(ends) == set(policy["tests"])
    assert sum(e["action"] == "suite_start" for e in events) == 1
    assert sum(e["action"] == "suite_end" for e in events) == 1
    refs_tests = set(ends) - {test for test, _ in rows}
    assert len(refs_tests) == 6 and all(ends[t]["status"] == "PASS" for t in refs_tests)
    assert all(e["status"] == "OK" for t,e in ends.items() if t not in refs_tests)
    assert result["execution_error"] is None and result["preservation_error"] is None
    assert assessment["complete"] and assessment["execution_preserved"]
    assert not assessment["errors"] and not assessment["infrastructure_faults"] and not assessment["comparison_errors"]
    assert read(directory / "PRE.json") == read(directory / "POST.json")
    cleanup = read(directory / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    meta = read(directory / "APPLICATION-METADATA.json")
    assert meta == read(directory / "APPLICATION-METADATA-POST.json") == assessment["run_binding"]
    assert meta["revision"] == epoch["semantic_index"]["head"] == expected_head
    suite_info = next(e["run_info"] for e in events if e["action"] == "suite_start")
    assert suite_info == assessment["run_info"]
    assert suite_info["revision"] == expected_head and suite_info["browser_build_id"] == meta["browser_build_id"]
    assert assessment["native_sources"] == policy["source_roles"][role]
    assert all(epoch["pins"][n] == pin for n,pin in assessment["native_sources"].items())
    binaries = read(directory / "NORMAL-BINARIES.json")
    assert all(epoch["pins"][n] == pin for n,pin in binaries.items())
    captures = read(directory / "OWNED-INPUT-PINS.json")
    for name, pin in captures.items():
        assert hashlib.sha256(raw(directory / name)).hexdigest() == pin
    phases.append(dict(rows=rows, ends=ends, metadata=meta, captures=captures, binaries=binaries,
                       assessment=assessment, result=result, run_info=suite_info))

old, new = phases
assert set(old["captures"]) == set(new["captures"])
assert {n for n in old["captures"] if old["captures"][n] != new["captures"][n]} == {"wptrunner.ini"}
assert raw(ORIGINAL / "wptrunner.ini").replace(str(ORIGINAL).encode(), b"OWNED-RUNTIME") == raw(CANDIDATE / "wptrunner.ini").replace(str(CANDIDATE).encode(), b"OWNED-RUNTIME")
assert {k:v for k,v in old["run_info"].items() if k not in ["browser_build_id","revision"]} == {k:v for k,v in new["run_info"].items() if k not in ["browser_build_id","revision"]}
counts = []
for group in identities:
    counts.append({phase: dict(collections.Counter(item["rows"][key]["status"] for key in group)) for phase,item in [("original",old),("candidate",new)]})
assert counts == [{"original":{"PASS":57,"FAIL":47},"candidate":{"PASS":104}}, {"original":{"FAIL":16},"candidate":{"FAIL":16}}, {"original":{"PASS":446},"candidate":{"PASS":446}}]
for key in identities[1] | identities[2]:
    assert signature(old["rows"][key]) == signature(new["rows"][key]), key
for test in old["ends"]:
    before_end, after_end = signature(old["ends"][test]), signature(new["ends"][test])
    if old["ends"][test]["status"] == "PASS":
        for end in [before_end, after_end]:
            end["message"] = re.sub(r"http://web-platform\.test:[0-9]+/", "http://web-platform.test:PORT/", end["message"])
    assert before_end == after_end, test
held = []
for key in sorted(identities[1]):
    message = new["rows"][key]["message"]
    decoder = json.JSONDecoder()
    observations, _ = decoder.raw_decode(message.split("observed=",1)[1])
    assert len(observations) == 2 and all(isinstance(v,dict) and v for v in observations)
    held.append(dict(test=key[0], subtest=key[1], signature=signature(new["rows"][key]), observations=observations))
changed = [dict(test=k[0],subtest=k[1],original=signature(old["rows"][k]),candidate=signature(new["rows"][k])) for k in sorted(identities[0]) if old["rows"][k]["status"] != new["rows"][k]["status"]]
assert len(changed) == 47 and all(v["original"]["status"] == "FAIL" and v["candidate"]["status"] == "PASS" for v in changed)
assert new["result"]["comparison_gate_passed"] and new["assessment"]["comparison_gate_passed"]
assert new["result"]["exit"] == 1 and not new["result"]["native_fix_acceptance"]
assert refs[str((CANDIDATE/"RESULT.json").relative_to(ROOT))] == "f6552b414ebb305d5ad085ad63bdbffc3e9902bfc0d126cdf85f06423f132d78"
assert refs[str((CANDIDATE/"ASSESSMENT.json").relative_to(ROOT))] == "b1ce69e398ec8ae9f603747636a62c665818b6643ba2147d4c29567196549b31"
succession = read(CANDIDATE / "HEAD-SUCCESSION.json")
assert succession["candidate_binaries"] == new["binaries"]
assert (succession["old_head"],succession["new_head"]) == (policy["original_frozen_head"],policy["frozen_head"])
build_dir = ROOT / "artifacts/css-registered-number-native-runtime-v1/head-candidate-build-2"
build = read(build_dir / "RESULT.json")
build_epoch = read(build_dir / "EPOCH.json")
assert build["command_success"] and build["preservation_verified"] and not build["owned_processes"] and not build["publication_errors"]
assert all(build_epoch["pins"][n] == pin for n,pin in new["binaries"].items())
assert all(build_epoch["pins"][n] == pin for n,pin in policy["source_roles"]["candidate"].items())
sign_rows = []
for name, wpt in [("original", old), ("candidate", new)]:
    directory = ROOT / ("artifacts/css-registered-admission-sign-runtime-" + name + "-1")
    result = read(directory / "RESULT.json")
    payload = read(directory / "RAW.json")
    assert result["complete"] and result["execution_preserved"] and result["error"] is None and result["preservation_error"] is None
    assert len(payload["payloads"]) == 1 and not payload["network_errors"]
    observation = payload["payloads"][0]["observation"]
    rows = observation["rows"]
    assert len(rows) == len({row["id"] for row in rows}) == 24
    assert all(len(row["snapshots"]) == 2 and row["registrationErrors"] == [] for row in rows)
    assert result["application_metadata"] == wpt["metadata"]
    assert result["normal_binaries"] == wpt["binaries"]
    assert result["native_sources"] == policy["source_roles"][name]
    assert result["normative_assessment_sha256"] == refs[str(((ORIGINAL if name == "original" else CANDIDATE)/"ASSESSMENT.json").relative_to(ROOT))]
    assert read(directory / "PRE.json") == read(directory / "POST.json")
    cleanup = read(directory / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["profile_removed"] and cleanup["server_thread_stopped"]
    sign_rows.append(dict(rows=rows, queryOrder=observation["queryOrder"], cleanup=cleanup))
assert sign_rows[0]["rows"] == sign_rows[1]["rows"] and sign_rows[0]["queryOrder"] == sign_rows[1]["queryOrder"]
assert refs["artifacts/css-registered-admission-sign-runtime-candidate-1/RESULT.json"] == "ea0cdb91212ce5c4f365024ed174a9545793ae3e7bb1504dbb0b606ab436ed0f"
check = dict(status="INDEPENDENT_RAW_COMPARISON_MATCHES", sign_24_rows_48_snapshots_exactly_unchanged=True, sign_cleanup=sign_rows[1]["cleanup"], counts=counts, changed_A=changed, held=held,
             reftests_each=6, all_23_completion_statuses_preserved=True, reftest_messages_equal_except_owned_server_port=True, all_fixture_metadata_captures_identical=True, only_configuration_change_is_owned_runtime_relocation=True,
             original_metadata=old["metadata"], candidate_metadata=new["metadata"],
             browser_processes_started=False, native_fix_accepted=False,
             candidate_WPT_exit=1, wrapper_gate_passed=True)
(HERE/"CHECK.json").write_text(json.dumps(check,indent=2)+"\n")
(HERE/"REFERENCES.json").write_text(json.dumps(refs,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in check.items() if k not in ["changed_A","held"]}))
