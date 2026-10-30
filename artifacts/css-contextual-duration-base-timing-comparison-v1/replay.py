import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
references = {}


def pin(path):
    references[str(path.relative_to(ROOT))] = sha(path)


def frozen(name, digest):
    directory = ROOT / "artifacts" / name
    assert sha(directory / "FILES.json") == digest
    pin(directory / "FILES.json")
    for name, row in read(directory / "FILES.json").items():
        path = directory / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == (row["sha256"] if isinstance(row, dict) else row)
        if isinstance(row, dict):
            assert path.stat().st_size == row["bytes"]
    return directory


def load(name, path):
    pin(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def records(directory):
    result = {}
    for path in sorted((directory / "progress-records").glob("*.json")):
        pin(path)
        result[path.stem] = read(path)["observations"]
    return result


def projection(item):
    return {"samples": [sample.get("value", sample.get("opacity")) for sample in item["samples"]],
            "phases": [sample["phase"] for sample in item["samples"]],
            "initial": item["initial"], "beforeMembership": item["beforeMembership"],
            "afterMembership": item["afterMembership"], "membership": item["membership"]}


original = frozen("css-contextual-duration-base-timing-original-runtime-1", "aae9fcfeff083a2940004a8614172f216b328cdfaac3c538d0516a6dd101c9bf")
candidate = frozen("css-contextual-duration-base-timing-candidate-runtime-1", "6c308f53a63e9a6642bc1a064e0fc575dcc6dcbb6447cce973e2bfb04047b031")
owner = frozen("css-contextual-duration-base-timing-candidate-v1", "75c52b6bbf11ec407778e80c9a602f551280f31cc17ad49d65e3d33e29d45ba0")
policy = read(owner / "POLICY.json")
comparison = load("timing_comparison", owner / "comparison.py")
assessor = load("timing_assessor", owner / "assess.py")
checks = load("timing_checks", ROOT / policy["wpt"]["checks_helper"])
baseline = comparison.replay_original(ROOT, policy, assessor, checks)
phase = candidate / "candidate-wpt"
settings = read(phase / "ASSESSMENT-POLICY.json")
assert settings == comparison.phase_policy(policy["wpt"])
events = [json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines()]
assessment = assessor.assess(events, read(phase / "RESULT.json")["exit"], settings, checks,
                            original=baseline, run_binding=read(phase / "APPLICATION-METADATA.json"))
assert json.loads(json.dumps(assessment)) == read(phase / "ASSESSMENT.json")
assert assessment["complete"] and not assessment["errors"] and not assessment["comparison_gate_passed"]
assert [row["status"] for row in assessment["rows"]].count("PASS") == 2
assert [row["status"] for row in assessment["rows"]].count("FAIL") == 5
assert len(assessment["ends"]) == 3 and all(row["status"] == "OK" for row in assessment["ends"])
collector = load("timing_records", owner / "records.py")
collection = collector.collect(ROOT, candidate / "progress-records", read(candidate / "PROGRESS-BINDING.json"), policy, assessment)
assert collection == read(candidate / "PROGRESS-RECORDS.json") and collection["complete"] and not collection["errors"]
calibration = load("timing_calibration", owner / "calibration.py").report(candidate / "progress-records", collection, policy)
assert calibration == read(candidate / "CALIBRATION.json") and calibration["all_calibrated"]
terminal = read(candidate / "ROOT-TERMINAL.json")
assert terminal["session_id"] == 29079 and terminal["terminal_chunk"] == "6c7cd1" and terminal["exit"] == 1
assert terminal["state_and_application_restoration_independently_verified"] and terminal["backup_removed_bytes"] == 1008605176
assert not terminal["native_acceptance"] and terminal["result_sha256"] == sha(candidate / "CANDIDATE-RESULT.json")
assert read(candidate / "candidate-build/RESULT.json")["native_sources"] == {
    name: row["candidate_sha256"] for name, row in read(owner / "SOURCE-ROLES.json").items()}
pin(candidate / "ROOT-TERMINAL.json")
refresh = ROOT / "artifacts/css-contextual-duration-base-timing-root-refresh.json"
pin(refresh)
assert read(refresh)["runtime_manifest_sha256"] == sha(candidate / "FILES.json")
assert read(refresh)["accepted_fix_increment"] == 0 and read(refresh)["only_changed_field"] == "raw_index_observation.current"

old_same = frozen("css-contextual-duration-same-element-candidate-runtime-1", "0e2168c3cf3a34e51c6a2437133d31c9bd5c2e3fc7b4971b09b5cfbf1895b7b2")
old_depth = frozen("css-contextual-duration-finite-depth-candidate-runtime-1", "7439b1de3c87ad0d0a100b558ca4c09a02ea5553f5a8d519b047a630737b1125")
chrome_same = frozen("css-chrome-same-element-runtime-1", "2a0b0e70f5e223a21a751c757905c3be7709b3484d0fad093dca54fe3aea9a5d")
chrome_depth = frozen("css-chrome-finite-depth-runtime-1", "091d92e8721f046bab1bb8455e5bdd581e2ada0cd10ad1913b8697ae1f64601f")
chrome_masked = frozen("css-chrome-masked-base-runtime-1", "84e0c8cd421d7a7802cebbff6764610cee620a45bc523d0895fbaac8311f40b4")
groups = {"original7": records(original), "timing_candidate": records(candidate),
          "prior_three_source": records(old_same) | records(old_depth),
          "chrome": records(chrome_same) | records(chrome_depth) | records(chrome_masked)}
table = {}
for kind in groups["original7"]:
    values = {label: items[kind] for label, items in groups.items() if kind in items}
    control_names = set(values["original7"]) - {"contextual"}
    for control in control_names:
        assert all(value[control] == values["original7"][control] for value in values.values()), (kind, control)
    for value in values.values():
        assert all(member["animation"] and member["effect"] for item in value.values() for member in item["membership"])
        assert all(item["beforeMembership"] == item["afterMembership"] for item in value.values())
    if kind.startswith("depth-"):
        assert all(value["contextual"]["initial"] == values["original7"]["contextual"]["initial"] for value in values.values())
    table[kind] = {label: projection(value["contextual"]) for label, value in values.items()}
result = {"original": {"PASS": 1, "FAIL": 6, "OK": 3}, "candidate": {"PASS": 2, "FAIL": 5, "OK": 3},
          "candidate_outcome_preserved": read(candidate / "CANDIDATE-RESULT.json"),
          "literal_controls_exactly_equal": True, "depth_initial_controls_exactly_equal": True,
          "identities_current": True, "details_before_after_membership_equal": True,
          "table": table, "terminal": terminal, "refresh": read(refresh),
          "scope": "Fresh pair strict raw/records/calibration replay; historical frozen record projection, not a rerun or native pass-count inference."}
(HERE / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
(HERE / "REFERENCES.json").write_text(json.dumps(references, indent=2, sort_keys=True) + "\n")
print(json.dumps({"new_pair": result["candidate"], "kinds": len(table), "references": len(references), "all_literal_controls_equal": True}))
