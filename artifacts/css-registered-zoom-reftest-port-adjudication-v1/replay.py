import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAPSULE = ROOT / "artifacts/css-registered-zoom-standalone-wpt-v2"
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def need(value, message):
    if not value:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def references(manifest, experiment):
    found = {}
    def visit(node, prefix):
        for name, value in node.items():
            path = prefix + "/" + name
            if isinstance(value, dict):
                visit(value, path)
            else:
                need(len(value) == 2, "single manifest item")
                item = value[1]
                need(item[0] is None and len(item[1]) == 1 and item[2] == {}, "exact unparameterized reference")
                ref, operator = item[1][0]
                need(operator == "==" and ref.startswith("/css/"), "declared reference operator/path")
                found[path] = (ref, operator)
    visit(manifest["items"]["reftest"], "")
    expected = {name for name, kind in experiment["tests"].items() if kind == "reftest"}
    need(set(found) == expected and len(found) == 6, "exact six manifest reftests")
    return found


def canonical_message(event, declared):
    need(event.get("action") == "test_end" and event.get("status") == "PASS", "only passed completions")
    need(event.get("test") in declared and "subtest" not in event, "only declared reftest completion")
    need("expected" not in event and event.get("known_intermittent") == [], "exact unchanged expectation fields")
    test = event["test"]
    ref, operator = declared[test]
    prefix = "Testing http://web-platform.test:"
    pattern = (re.escape(prefix) + r"([1-9][0-9]{0,4})" + re.escape(test + " " + operator + " http://web-platform.test:")
               + r"([1-9][0-9]{0,4})" + re.escape(ref + "\n"))
    match = re.fullmatch(pattern, event.get("message", ""))
    need(match is not None, "exact manifest test/reference URLs, operator, host and message framing")
    need(match[1] == match[2] and 1 <= int(match[1]) <= 65535, "one valid HTTP port within message")
    return prefix + "<PORT>" + test + " " + operator + " http://web-platform.test:<PORT>" + ref + "\n", int(match[1])


def normalize_pair(original, candidate, declared):
    left, right = copy.deepcopy(original), copy.deepcopy(candidate)
    records = []
    for test in sorted(declared):
        pair = []
        for assessment in (left, right):
            matches = [e for e in assessment["ends"] if e.get("test") == test]
            need(len(matches) == 1, "one declared completion")
            pair.append(matches[0])
        fields = ("action", "status", "expected", "known_intermittent")
        need({k:pair[0][k] for k in fields if k in pair[0]} ==
             {k:pair[1][k] for k in fields if k in pair[1]}, "unchanged non-message signature")
        a, aport = canonical_message(pair[0], declared)
        b, bport = canonical_message(pair[1], declared)
        need(a == b, "only port may differ")
        records.append({"test":test,"reference":declared[test][0],"operator":declared[test][1],
                        "original_port":aport,"candidate_port":bport,
                        "original_message":pair[0]["message"],"candidate_message":pair[1]["message"]})
        pair[0]["message"] = a
        pair[1]["message"] = b
    need(len({r["original_port"] for r in records}) == len({r["candidate_port"] for r in records}) == 1,
         "one recorded HTTP server port per phase")
    return left, right, records


def replay():
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, "python3 -I -S -B required")
    refs = read(HERE / "REFERENCES.json")
    for name, pin in refs.items():
        need(sha(ROOT / name) == pin, "frozen evidence: " + name)
    helper = load("port_run_helper", CAPSULE / "run.py")
    for version in (1, 2):
        directory = ROOT / f"artifacts/css-registered-zoom-standalone-wpt-v{version}"
        helper.authenticate(directory, refs[str((directory / "FILES.json").relative_to(ROOT))])
    experiment = read(CAPSULE / "EXPERIMENT.json")
    base = ROOT / "artifacts/css-registered-zoom-standalone-wpt-v1"
    for name in ("EXPERIMENT.json", "SUBSET-MANIFEST.json", "SOURCE-PINS.json", "assess.py", "compare.py"):
        need((base/name).read_bytes() == (CAPSULE/name).read_bytes(), "same paired input: " + name)
    for item in read(CAPSULE / "SOURCE-PINS.json").values():
        if item["exists"]:
            need(sha(CAPSULE/item["capture"]) == sha(base/item["capture"]) == item["sha256"], "exact captured fixture/resource")
    declared = references(read(CAPSULE / "SUBSET-MANIFEST.json"), experiment)
    assessments = []
    for role, capsule in (("original", base), ("candidate", CAPSULE)):
        runtime = ROOT / f"artifacts/css-registered-zoom-standalone-wpt-runtime-{role}-1"
        assessment, result = read(runtime/"ASSESSMENT.json"), read(runtime/"RESULT.json")
        policy, epoch = read(capsule/"POLICY.json"), read(runtime/"EPOCH.json")
        need(assessment["complete"] and assessment["execution_preserved"] and result["execution_error"] is None
             and result["preservation_error"] is None, "complete preserved phase")
        need(assessment["capsule_manifest_sha256"] == sha(capsule/"FILES.json") and
             assessment["epoch_sha256"] == sha(runtime/"EPOCH.json") and
             assessment["native_sources"] == policy["source_roles"][role], "source/capsule/epoch binding")
        need(read(runtime/"PRE.json") == read(runtime/"POST.json"), "full saved preservation")
        cleanup = read(runtime/"CLEANUP.json")
        need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "saved cleanup")
        need(read(runtime/"metadata/MANIFEST.json") == read(capsule/"SUBSET-MANIFEST.json"), "actual runtime manifest matches pinned inputs")
        for name, item in read(capsule/"SOURCE-PINS.json").items():
            prefix = "testing/web-platform/"
            need(name.startswith(prefix), "captured source path")
            relative = name[len(prefix):]
            staged = runtime / ("metadata/" + relative[5:] if relative.startswith("meta/") else relative)
            if item["exists"]:
                need(staged.is_file() and not staged.is_symlink() and sha(staged) == item["sha256"], "actual runtime copied input")
            else:
                need(not staged.exists() and not staged.is_symlink(), "absent runtime metadata/input")
        metadata = read(runtime/"APPLICATION-METADATA.json")
        need(metadata == read(runtime/"APPLICATION-METADATA-POST.json") == assessment["run_binding"], "saved metadata")
        need(read(runtime/"NORMAL-BINARIES.json") == policy["phase_binaries"], "saved phase binaries")
        load("port_bindings", capsule/"bindings.py").validate_phase(ROOT, capsule, policy, epoch, helper)
        parser = load("port_assessor", capsule/"assess.py")
        checks = load("port_checks", ROOT/policy["helpers"]["checks"])
        raw = [json.loads(line) for line in (runtime/"raw.jsonl").read_text().splitlines()]
        generated = parser.assess(raw, result["exit"], policy, checks, original=None, run_binding=metadata)
        ignore = {"subtest_cardinality_policy", "oracle_caveat"}
        need(all(assessment.get(k) == v for k,v in generated.items() if k not in ignore), "exact raw assessor replay")
        assessments.append(assessment)
    historical = load("port_history", CAPSULE/"history.py").validate(ROOT, CAPSULE, helper)
    comparator = load("port_compare", CAPSULE/"compare.py")
    original, candidate = assessments
    raw_comparison = comparator.compare(original, candidate, experiment, historical)
    saved = read(ROOT/"artifacts/css-registered-zoom-standalone-wpt-runtime-candidate-1/COMPARISON.json")
    need(raw_comparison == saved and not saved["broad_regression_gate_passed"], "retain exact raw false comparison")
    need({r["test"] for r in saved["broad_rejections"]} == set(declared) and
         len(saved["broad_rejections"]) == 6 and
         all(r["subtest"] is None and r["category"] == "changed_unresolved" for r in saved["broad_rejections"]), "only six passed reftest messages rejected")
    left, right, records = normalize_pair(original, candidate, declared)
    normalized = comparator.compare(left, right, experiment, historical)
    need(normalized["broad_regression_gate_passed"] and not normalized["broad_rejections"], "adjudicated broad gate")
    need(normalized["summary"]["subtests"] == {"broad:unchanged":566,"zoom70:repaired":56,"zoom70:unchanged":14}, "exact observed subtest deltas")
    need(normalized["summary"]["test_completions"] == {"broad:unchanged":23,"zoom70:unchanged":6}, "exact completions")
    need(all(e["status"] == "PASS" for e in candidate["rows"] if e["test"] not in experiment["broad_tests"]), "all zoom70 pass")
    for name, pin in refs.items():
        need(sha(ROOT/name) == pin, "evidence unchanged after replay")
    return {"raw_comparison":raw_comparison,"normalized_comparison":normalized,"normalization_records":records,
            "verdict":{"adjudicated_broad_gate_passed":True,"raw_wrapper_gate_remains_false":True,
                       "normalization_scope":"Only HTTP server ports in six manifest-exact PASS reftest test_end messages",
                       "subtests":normalized["summary"]["subtests"],"all_zoom70_pass":True,
                       "reftests_passed":6,"native_fix_acceptance":False,"browser_rerun":False}}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
