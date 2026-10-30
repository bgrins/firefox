import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("paired_report", HERE / "report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
report.authenticate(report.PARSER, report.PARSER_SEAL)
parser = report.load("strict_trace", report.PARSER / "trace.py")

def event(seq, stage, **fields):
    result = dict(pid=1, seq=seq, id="coupled-override", element="0x123", pseudo=0,
                  identifier="0x0", stage=stage, cascade=0, request=2,
                  present=1, bit=1, servo=0, pre=0, root="0x0", flags=0,
                  effect="0x0", animation="0x0")
    result.update(fields)
    return result

events = [event(1, "request-before", bit=0, present=0, servo=1),
          event(2, "request-set", servo=1),
          event(3, "post-deferred", servo=1, request=-1, present=-1, bit=-1),
          event(4, "request-before"), event(5, "request-coalesced"),
          event(6, "pre-post-hint", request=-1, pre=1),
          event(7, "pre-will-compose", request=-1, pre=1)]
text = "\n".join(parser.PREFIX + " ".join(f"{k}={v}" for k, v in row.items()) for row in events)
parsed = parser.parse(text)
assert parsed["trace_syntax_and_sequence_valid"]
groups = report.trace_groups(parsed, parser)
assert len(groups) == 1
assert groups[0]["witness_intervals"] == [{"deferred_request": [1, 2, 3], "outside_layer": [4, 5]}]
assert groups[0]["barriers"] == [{"sequence": 6, "stage": "pre-post-hint"}]
assert groups[0]["will_compose_preparation"] == [7]
later = copy.deepcopy(parsed)
for row in later["events_in_input_order"]:
    row["pid"] = 2
for witness in later["bounded_candidate_witnesses"]:
    witness["pid"] = 2
merged = copy.deepcopy(parsed)
merged["events_in_input_order"] += later["events_in_input_order"]
merged["bounded_candidate_witnesses"] += later["bounded_candidate_witnesses"]
assert len(report.trace_groups(merged, parser)) == 2
compared = report.compare_labels({"full_key_groups": groups}, {"full_key_groups": report.trace_groups(merged, parser)}, parser.IDS)
row = next(x for x in compared if x["label"] == "coupled-override")
assert row["original"]["distinct_keys"] == 1 and row["candidate"]["distinct_keys"] == 2
assert not row["same_native_identity_across_runs_claimed"]
for role in ("original", "candidate"):
    metadata = {"source_role": role, "trace_source_role": "instrumented-" + role}
    report.require_role(metadata, role)
    try:
        report.require_role(metadata, "candidate" if role == "original" else "original")
    except AssertionError:
        pass
    else:
        raise AssertionError("swapped runtime role accepted")
with tempfile.TemporaryDirectory(prefix="paired-trace-report-check-") as temporary:
    directory = Path(temporary)
    (directory / "data").write_text("synthetic")
    manifest = {"data": {"sha256": report.sha(directory / "data"), "bytes": 9}}
    (directory / "FILES.json").write_text(json.dumps(manifest))
    pin = report.sha(directory / "FILES.json")
    assert report.authenticate(directory, pin) == manifest
    (directory / "data").write_text("tampered")
    try:
        report.authenticate(directory, pin)
    except AssertionError:
        pass
    else:
        raise AssertionError("changed payload accepted")
print(json.dumps({"sealed_parser_authenticated": True, "witness_barrier_preparation_groups_correct": True,
                  "process_keys_not_merged": True, "cross_run_labels_not_identity": True,
                  "changed_manifest_payload_rejected": True, "scratch_removed": True,
                  "both_role_joins_pass": True, "both_swapped_roles_rejected": True,
                  "running_or_frozen_native_runtime_read": False}, indent=2))
