import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / "css-hidden-layout-column-runtime-v1"
RAW = RUNTIME / "trace-both-column/raw.json"
query = re.compile(
    r"CV_COLUMN_QUERY target=(\S+) kind=(col|group|table) d=([01]) h=([01]) "
    r"provider=(\S+) table=([01]) pd=([01]) ph=([01])"
)
publish = re.compile(
    r"CV_COLUMN_PUBLISH table=(\S+) target=(\S+) kind=(col|group) "
    r"rect=(-?\d+),(-?\d+),(-?\d+),(-?\d+)"
)
events = [json.loads(line) for line in RAW.read_text().splitlines()]
records = []
counts = Counter()
for ordinal, event in enumerate(events):
    data = event.get("data", "")
    if event.get("action") != "process_output" or "CV_COLUMN_" not in data:
        continue
    q = query.fullmatch(data)
    p = publish.fullmatch(data)
    assert bool(q) != bool(p), data
    record = {"raw_ordinal": ordinal, "output_process": event["process"]}
    if q:
        target, kind, dirty, children, provider, table, pd, ph = q.groups()
        target_dirty = bool(int(dirty) or int(children))
        provider_dirty = bool(int(pd) or int(ph))
        record.update(
            action="query", target=target, kind=kind, dirty=int(dirty),
            dirty_children=int(children), provider=provider, table=bool(int(table)),
            provider_dirty=int(pd), provider_dirty_children=int(ph),
        )
        counts[f"query/{kind}/target-dirty={target_dirty}/table={bool(int(table))}/provider-dirty={provider_dirty}"] += 1
    else:
        table, target, kind, *rect = p.groups()
        record.update(action="publish", table=table, target=target, kind=kind,
                      rect_app_units=[int(v) for v in rect])
        counts[f"publish/{kind}"] += 1
    records.append(record)
assert records and any(r["action"] == "query" for r in records)
assert any(r["action"] == "publish" for r in records)
trace_run = json.loads((RUNTIME / "trace-both-column/RUN.json").read_text())
both_run = json.loads((RUNTIME / "both/RUN.json").read_text())
assert trace_run["complete"] and trace_run["before"] == trace_run["after"]
assert len(trace_run["rows"]) == 16 and len(trace_run["ends"]) == 2
trace_rows = {(r["test"], r["subtest"]): (r["status"], r.get("message")) for r in trace_run["rows"]}
both_rows = {(r["test"], r["subtest"]): (r["status"], r.get("message")) for r in both_run["rows"]}
assert len(trace_rows) == 16
assert all(both_rows[k] == v for k, v in trace_rows.items())
result = {
    "input_sha256": {str(p.relative_to(RUNTIME)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [RAW, RUNTIME / "trace-both-column/RUN.json", RUNTIME / "both/RUN.json"]},
    "instrumented_outcomes_match": True,
    "counts": dict(sorted(counts.items())),
    "scope": "Each query records target/provider bits in one native call. Publications are recorded independently. Output-process/pointer equality does not prove DOM identity, frame lifetime, query-stage identity, or cross-event causation.",
    "records": records,
}
(HERE / "TRACE.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"counts": result["counts"], "instrumented_outcomes_match": True}, indent=2))
