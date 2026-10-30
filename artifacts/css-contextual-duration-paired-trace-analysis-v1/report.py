import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARSER = ROOT / "artifacts/css-contextual-duration-pending-restyle-trace-parser-v1"
PARSER_SEAL = "7fc2397e2a9d5a1efbfa3fae37dd5e82aa2b6232631dcf33e9bd59ea6c4a608c"
SCHEMA = ROOT / "artifacts/css-contextual-duration-feedback-consistency-probe-v1/duration-feedback-discriminator-record.py"
SCHEMA_HASH = "c0d86674723f3ab84a701e8b646eb8b437f4c84214b497818fba0fc87ab67bb3"


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(directory, pin):
    assert sha(directory / "FILES.json") == pin
    manifest = read(directory / "FILES.json")
    for name, item in manifest.items():
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        path = directory / relative
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == (item["sha256"] if isinstance(item, dict) else item), name
        if isinstance(item, dict):
            assert path.stat().st_size == item["bytes"]
    return manifest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trace_groups(parsed, parser):
    groups = {}
    for event in parsed["events_in_input_order"]:
        key = parser.event_key(event)
        if key not in groups:
            groups[key] = {**{k: event[k] for k in ("pid", "id", "element", "pseudo", "identifier", "cascade")},
                           **parser.identify(event), "sequences": [], "stage_counts": Counter(),
                           "scope_kind": "eligibility-without-cascade" if event["cascade"] == -1 else "cascade-table-key",
                           "barriers": [], "deferred": [], "outside_coalesced": [],
                           "will_compose_preparation": [], "witness_intervals": []}
        group = groups[key]
        group["sequences"].append(event["seq"])
        group["stage_counts"][event["stage"]] += 1
        if event["stage"] in parser.INVALIDATORS:
            group["barriers"].append({"sequence": event["seq"], "stage": event["stage"]})
        if event["stage"] == "post-deferred":
            group["deferred"].append(event["seq"])
        if event["stage"] == "request-coalesced" and event["request"] == 2 and not event["servo"] and not event["pre"]:
            group["outside_coalesced"].append(event["seq"])
        if event["stage"] == "pre-will-compose":
            group["will_compose_preparation"].append(event["seq"])
    for witness in parsed["bounded_candidate_witnesses"]:
        key = tuple(witness[k] if k != "id" else witness["dom_id"].removeprefix("duration-feedback-")
                    for k in ("pid", "id", "element", "pseudo", "identifier", "cascade"))
        groups[key]["witness_intervals"].append({
            "deferred_request": witness["deferred_request_sequences"],
            "outside_layer": witness["outside_coalesced_layer_sequences"],
        })
    for group in groups.values():
        sequences = group.pop("sequences")
        group["first_sequence"], group["last_sequence"] = sequences[0], sequences[-1]
        group["event_count"] = len(sequences)
    return list(groups.values())


def observation_roles(directory, manifest, schema, run_id):
    roles = {}
    for kind in ("coupled", "zero-start"):
        name = f"feedback-records/{kind}.json"
        assert name in manifest
        record = read(directory / name)
        assert set(record) == {"run_id", "kind", "trajectories"} and record["run_id"] == run_id
        assert schema.validate({k: v for k, v in record.items() if k != "run_id"}) == kind
        for trajectory in record["trajectories"]:
            def snapshot(value):
                return {k: value[k] for k in ("order", "style", "effects", "sameAnimations", "sameEffects")} | {
                    "style_repeats_equal": value["style"] == value["repeatStyle"] == value["afterMembershipStyle"],
                    "timing_repeats_equal": value["effects"] == value["repeatEffects"] == value["currentEffects"],
                    "different_repeated_values": {later: value[later] for first, later in (
                        ("style", "repeatStyle"), ("style", "afterMembershipStyle"),
                        ("effects", "repeatEffects"), ("effects", "currentEffects")) if value[first] != value[later]},
                }
            roles[f"{kind}-{trajectory['role']}"] = {
                "record_sha256": sha(directory / name),
                "acquisition": {k: snapshot(v) for k, v in trajectory["acquisition"].items()},
                "phases": [{"name": phase["name"], "reads": [snapshot(v) for v in phase["reads"]]}
                           for phase in trajectory["phases"]],
                "native_sequence_alignment": None,
            }
    return roles


def require_role(metadata, expected_role):
    assert expected_role in ("original", "candidate")
    assert metadata["source_role"] == expected_role
    assert metadata["trace_source_role"] == "instrumented-" + expected_role


def summarize(directory, pin, parser, schema, expected_role):
    directory = Path(directory)
    manifest = authenticate(directory, pin)
    required = {"ROOT-TERMINAL.json", "TRACE-INDEX.json", "DIAGNOSTICS.json", "FEEDBACK-RECORDS.json",
                "feedback-wpt/raw.jsonl", "feedback-wpt/wpt.log", "feedback-wpt/ASSESSMENT.json",
                "feedback-wpt/RESULT.json", "feedback-wpt/APPLICATION-METADATA.json"}
    assert required <= set(manifest)
    index = read(directory / "TRACE-INDEX.json")
    streams = {"raw": directory / "feedback-wpt/raw.jsonl", "log": directory / "feedback-wpt/wpt.log"}
    texts = {key: path.read_text() for key, path in streams.items()}
    primary = "raw" if parser.PREFIX in texts["raw"] else "log"
    expected = parser.parse(texts[primary])
    expected.update(source_files={key: {"sha256": sha(path), "bytes": path.stat().st_size} for key, path in streams.items()},
                    primary_stream=primary, streams_not_merged_or_deduplicated=True,
                    parser_sha256=sha(PARSER / "trace.py"), numeric_or_convergence_oracle=False)
    assert index == expected
    assessment = read(directory / "feedback-wpt/ASSESSMENT.json")
    metadata = read(directory / "feedback-wpt/APPLICATION-METADATA.json")
    require_role(metadata, expected_role)
    records = read(directory / "FEEDBACK-RECORDS.json")
    assert records["numeric_or_convergence_oracle"] is False
    assert set(records["records"]) == {"coupled.json", "zero-start.json"}
    assert records["calibrated_acquisition"] == (assessment["complete"] and len(assessment["rows"]) == 2
                                               and all(row["status"] == "PASS" for row in assessment["rows"]))
    for name, item in records["records"].items():
        assert sha(directory / "feedback-records" / name) == item["sha256"]
    return {
        "directory": str(directory), "manifest_sha256": pin,
        "terminal": read(directory / "ROOT-TERMINAL.json"),
        "phase_result": read(directory / "feedback-wpt/RESULT.json"),
        "metadata": metadata,
        "diagnostics": read(directory / "DIAGNOSTICS.json"),
        "calibrated_acquisition": records["calibrated_acquisition"],
        "callbacks": [{k: row.get(k) for k in ("subtest", "status", "message")} for row in assessment["rows"]],
        "endings": [{k: row.get(k) for k in ("test", "status", "message")} for row in assessment["ends"]],
        "trace": {k: index[k] for k in ("trace_syntax_and_sequence_valid", "truncated", "cap_markers", "errors", "missing_ids", "primary_stream")},
        "full_key_groups": trace_groups(index, parser),
        "observations_by_label": observation_roles(directory, manifest, schema, records["run_id"]),
    }


def compare_labels(original, candidate, ids):
    result = []
    for label in sorted(ids):
        counts = {}
        for name, runtime in (("original", original), ("candidate", candidate)):
            groups = [g for g in runtime["full_key_groups"] if g["id"] == label]
            counts[name] = {"distinct_keys": sum(g["cascade"] >= 0 for g in groups),
                            "eligibility_groups_without_cascade": sum(g["cascade"] == -1 for g in groups),
                            "events": sum(g["event_count"] for g in groups),
                            "bounded_witness_intervals": sum(len(g["witness_intervals"]) for g in groups)}
        result.append({"label": label, **counts, "same_native_identity_across_runs_claimed": False})
    return result


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--original", nargs=2, required=True, metavar=("DIRECTORY", "MANIFEST_SHA256"))
    args.add_argument("--candidate", nargs=2, metavar=("DIRECTORY", "MANIFEST_SHA256"))
    options = args.parse_args()
    authenticate(PARSER, PARSER_SEAL)
    assert sha(SCHEMA) == SCHEMA_HASH
    parser, schema = load("strict_trace", PARSER / "trace.py"), load("record_schema", SCHEMA)
    report = {"original": summarize(*options.original, parser, schema, "original"),
              "limits": {"phase_alignment": "kind/role only; no script marker or synchronized timestamp join",
                         "post_barriers": "dispatch attempts and removal boundaries, not proof of successful composition",
                         "pre_will_compose": "preparation only", "effective_change_per_layer_request": False,
                         "native_refinement_proved": False, "convergence_or_numeric_feedback_oracle": False,
                         "outcome_is_not_trace_completeness": True}}
    if options.candidate:
        report["candidate"] = summarize(*options.candidate, parser, schema, "candidate")
        report["label_comparison"] = compare_labels(report["original"], report["candidate"], parser.IDS)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
