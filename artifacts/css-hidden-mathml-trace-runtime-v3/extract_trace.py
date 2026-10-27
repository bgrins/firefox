"""Extract one proposed original-eight run; does not launch or modify Firefox."""
import collections
import hashlib
import json
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
output = pathlib.Path(sys.argv[2])
output.mkdir(parents=True, exist_ok=True)
events = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
native = []
results = []
phases = []
decoder = json.JSONDecoder()
for event_index, event in enumerate(events):
    for field in ("data", "message"):
        value = event.get(field)
        if not isinstance(value, str):
            continue
        variants = [value]
        for offset, char in enumerate(value):
            if char != '"':
                continue
            try:
                decoded, _ = decoder.raw_decode(value[offset:])
            except ValueError:
                continue
            if isinstance(decoded, str) and decoded.startswith("HMQ_"):
                variants.append(decoded)
        for variant in dict.fromkeys(variants):
            if "HMQ_NATIVE " in variant:
                record = variant.split("HMQ_NATIVE ", 1)[1].strip()
                native.append({"raw_event": event_index, "process": event.get("process"),
                               **dict(part.split("=", 1) for part in record.split()
                                      if "=" in part)})
                break
            if variant.startswith("HMQ_RESULT "):
                record, _ = decoder.raw_decode(variant[len("HMQ_RESULT "):])
                results.append({"raw_event": event_index, **record})
                break
            if variant.startswith("HMQ_PHASE "):
                phases.append({"raw_event": event_index,
                               "phase": variant[len("HMQ_PHASE "):].strip()})
                break
statuses = [x for x in events if x.get("action") == "test_status"]
ends = [x for x in events if x.get("action") == "test_end"]
errors = []
if len(statuses) != 8 or len({x["subtest"] for x in statuses}) != 8:
    errors.append("Expected eight unique WPT subtests")
if len(ends) != 1 or ends[0].get("status") != "OK":
    errors.append("Expected one file-level OK")
if len(results) != 8 or {r["index"] for r in results} != set(range(8)):
    errors.append("Expected eight unique HMQ_RESULT records")
if not native:
    errors.append("No native trace captured")
for result in results:
    if [r["stage"] for r in result["rows"]] != ["warm", "hide", "mutate", "show", "restore"]:
        errors.append(f"Incomplete stages for case {result['index']}")
summary = {
    "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "counts": dict(collections.Counter(x["status"] for x in statuses)),
    "native_records": len(native), "phase_records": len(phases),
    "events": dict(collections.Counter(x.get("event") for x in native)),
    "results": results, "capture_errors": errors,
    "interpretation": "Event presence does not independently prove the proposed causal chain. Join by phase, frame/id and order; inspect dirty state and publication."}
for name, payload in [("NATIVE.json", native), ("PHASES.json", phases), ("SUMMARY.json", summary)]:
    (output/name).write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({k: summary[k] for k in ["counts", "native_records", "phase_records", "capture_errors"]}))
raise SystemExit(bool(errors))
