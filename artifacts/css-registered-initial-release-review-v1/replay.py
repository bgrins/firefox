import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "artifacts/css-registered-initial-release-observation-runtime-1"
CAP = ROOT / "artifacts/css-registered-initial-release-observation-v1"
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def authenticate(directory, digest, runtime=False):
    assert sha(directory / "FILES.json") == digest
    manifest = read(directory / "FILES.json")
    entries = manifest["files"] if runtime else manifest
    if runtime:
        assert manifest["complete"] and not manifest["native_fix_accepted"]
    actual = set()
    links = {}
    for path in directory.rglob("*"):
        name = str(path.relative_to(directory))
        if path.is_symlink():
            links[name] = str(path.resolve())
        elif path.is_file() and name != "FILES.json":
            assert stat.S_ISREG(path.lstat().st_mode)
            actual.add(name)
    assert actual == set(entries)
    assert links == (manifest["excluded_derived_links"] if runtime else {})
    for name, pin in entries.items():
        assert sha(directory / name) == pin["sha256"]
        assert (directory / name).stat().st_size == pin["bytes"]

capsha = "3e2bab2f25407060fe5bea3fbc2f60575988e6e107d8f24c1d2bd90347456ee1"
runsha = "2e4c300ed22e41d2d1bb324525f19ff3f37dc21aa86abb28256fad54a4e26540"
authenticate(CAP, capsha)
authenticate(RUN, runsha, runtime=True)
for name, pin in read(CAP / "REFERENCES.json").items():
    assert sha(ROOT / name) == pin, name
policy, assessment, result = read(CAP / "POLICY.json"), read(RUN / "ASSESSMENT.json"), read(RUN / "RESULT.json")
metadata = read(RUN / "APPLICATION-METADATA.json")
assert metadata == read(RUN / "APPLICATION-METADATA-POST.json") == assessment["run_binding"]
assert all(metadata[k] == v for k, v in policy["release_metadata"].items())
assert metadata["source_stamp"] != metadata["revision"] == policy["frozen_head"]
assert assessment["native_sources"] == {} and assessment["observation_only"]
assert assessment["capsule_manifest_sha256"] == capsha and assessment["experiment_sha256"] == sha(CAP / "EXPERIMENT.json")
assert assessment["epoch_sha256"] == policy["epoch_sha256"] == sha(RUN / "EPOCH.json")
assert assessment["complete"] and assessment["execution_preserved"]
assert not assessment["errors"] and not assessment["infrastructure_faults"] and not assessment["comparison_errors"]
assert result["observation_gate_passed"] and result["exact_pending_staging_preserved"]
assert result["execution_error"] is None and result["preservation_error"] is None
assert not result["native_fix_acceptance"] and result["exit"] == 1
outer = read(RUN / "OUTER.json")
assert outer == {"session_id": 43539, "launch_chunk": "451769", "terminal_chunk": "fe018a", "exit_code": 0}
assert read(RUN / "PRE.json") == read(RUN / "POST.json")
cleanup = read(RUN / "CLEANUP.json")
assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
epoch = read(RUN / "EPOCH.json")
staging = read(ROOT / policy["staged_capsule"] / "STAGING.json")
assert len(epoch["staged_working"]) == 36 and epoch["staged_working"] == staging["staged_working"]
assert epoch["semantic_index"] == staging["semantic_index"]
pre = read(RUN / "PRE.json")
assert {k: pre["index"][k] for k in epoch["semantic_index"]} == epoch["semantic_index"]
assert pre["index"]["raw_index"] == staging["raw_index"]
assert pre["working_sources_binaries_research_preserved"]
command = read(RUN / "COMMAND.json")
assert command["epoch_sha256"] == policy["epoch_sha256"] and command["wrapper_manifest_sha256"] == capsha
assert "--binary=/Applications/Firefox.app/Contents/MacOS/firefox" in command["command"]
assert sorted(v.removeprefix("--include=") for v in command["command"] if v.startswith("--include=")) == sorted(policy["tests"])
assert read(RUN / "NORMAL-BINARIES.json") == policy["phase_binaries"]
phase = read(RUN / "PHASE-BINDING.json")
assert phase["repository_sources_built_browser"] is False and phase["preserved_staged_files"] == 36
assert phase["staged_patch_sha256"] == staging["staged_patch_sha256"]
assert phase["external_browser"]["application_inventory_sha256"] == sha(CAP / "EXTERNAL-APPLICATION.json")
assert len(read(CAP / "EXTERNAL-APPLICATION.json")["entries"]) == 110
assert phase["external_browser"] == assessment["external_browser"]
for name, pin in read(RUN / "OWNED-INPUT-PINS.json").items():
    assert sha(RUN / name) == pin
for name, item in read(CAP / "SOURCE-PINS.json").items():
    if item["exists"]:
        suffix = name.removeprefix("testing/web-platform/")
        relative = "metadata/" + suffix[5:] if suffix.startswith("meta/") else suffix
        assert sha(RUN / relative) == item["sha256"]
parser = load("saved_release_assessor", CAP / "assess.py")
checks = load("saved_release_checks", ROOT / policy["helpers"]["checks"])
events = [json.loads(line) for line in (RUN / "raw.jsonl").read_text().splitlines()]
replayed = parser.assess(events, result["exit"], policy, checks, original=None, run_binding=metadata)
for key, value in replayed.items():
    if key not in ["oracle_caveat", "subtest_cardinality_policy"]:
        assert assessment[key] == value, key
rows = [e for e in events if e.get("action") == "test_status"]
ends = [e for e in events if e.get("action") == "test_end"]
assert len(rows) == 68 and len(ends) == 2 and all(e["status"] == "OK" for e in ends)
assert Counter(r["status"] for r in rows) == {"PASS": 27, "FAIL": 41}
assert {(r["test"], r["subtest"]) for r in rows} == {(test, name) for test, names in policy["target_subtests"].items() for name in names}
assert all(r["message"] == 'assert_throws_dom: function "() => CSS.registerProperty(definition)" did not throw' for r in rows if r["status"] == "FAIL")
local = ROOT / "artifacts/css-registered-provider-expanded-observation-runtime-baseline-1"
authenticate(local, "52dbfe7feb9f65621c4490951a9ec6a2258eb6506866e2dcdab8b8253f61e33e", runtime=True)
original = "/css/css-properties-values-api/registered-initial-computational-independence.html"
def signatures(items):
    return {(r["test"], r["subtest"]): {k: r[k] for k in ["status", "expected", "known_intermittent", "message"] if k in r}
            for r in items if r["test"] == original}
assert signatures(rows) == signatures(read(local / "ASSESSMENT.json")["rows"]) and len(signatures(rows)) == 21
per_page = {test: dict(Counter(r["status"] for r in rows if r["test"] == test)) for test in policy["tests"]}
assert per_page[original] == {"PASS": 12, "FAIL": 9}
assert per_page["/css/css-properties-values-api/registered-initial-selected-independence.html"] == {"PASS": 15, "FAIL": 32}
observed = read(RUN / "OBSERVATIONS.json")
assert observed["assertions"] == 68 and observed["statuses"] == {"PASS": 27, "FAIL": 41}
assert observed["all_failures_missing_syntax_error"] and observed["original21_full_signatures_match_local_baseline"]
verdict = {"verdict": "CONFIRMED_SAVED_EVIDENCE", "raw_replayed": True, "assertions": 68, "statuses": {"PASS": 27, "FAIL": 41}, "harness_ends": {"OK": 2}, "per_page": per_page,
    "original21_full_semantic_signatures_equal_including_field_presence": True,
    "all41_missing_expected_SyntaxError_after_support_assertion": True,
    "external_browser": phase["external_browser"], "harness_revision": policy["frozen_head"],
    "preserved_staged_files": 36, "stored_preservation_and_cleanup_verified": True,
    "native_fix_accepted": False, "browser_rerun": False, "live_state_queried": False}
(HERE / "VERDICT.json").write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
refs = {str(p.relative_to(ROOT)): sha(p) for p in [CAP / "FILES.json", RUN / "FILES.json", RUN / "raw.jsonl", RUN / "ASSESSMENT.json", RUN / "RESULT.json", RUN / "REPORT.md", RUN / "OBSERVATIONS.json", local / "FILES.json"]}
(HERE / "REFERENCES.json").write_text(json.dumps(refs, indent=2, sort_keys=True) + "\n")
print(json.dumps(verdict))
