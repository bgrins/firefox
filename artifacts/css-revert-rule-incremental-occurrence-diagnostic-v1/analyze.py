import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re


NATIVE = "CSS_OCCURRENCE_NATIVE_V1 "
PHASE = "CSS_OCCURRENCE_PHASE_V1 "
ADDRESS = r"0x[0-9a-fA-F]+"
HEADER = re.compile(r"pid=(\d+) (?:call=(\d+) )?event=([a-z-]+)(?: (.*))?$")
SOURCE = re.compile(
    rf"node=(\d+) block=({ADDRESS}) entries=(\d+) important=(true|false) "
    r"priority=(.+) normalized=(.+)$"
)
ENTRY = re.compile(
    rf"node=(\d+) entry=(\d+) block=({ADDRESS}) declaration=({ADDRESS}) property=(.+)$"
)


def priority_is_full(value):
    return (value.startswith("CascadePriority {") and value.endswith("}")
            and all(field in value for field in ["cascade_level:", "flags:", "layer_order:"]))


def assess_call(call):
    errors = call["errors"]
    sources = call["sources"]
    if call["end"] is None:
        errors.append("missing end record")
    if call["caps"]:
        errors.append("call has a node or declaration cap")
    total_entries = 0
    for source in sources.values():
        if source["expected_entries"] > 8 or set(source["entries"]) != set(range(source["expected_entries"])):
            errors.append(f"incomplete entries for source {source['node']}")
        total_entries += len(source["entries"])
        if not source["direct"]:
            if not priority_is_full(source["raw_priority"]) or not priority_is_full(source["normalized_priority"]):
                errors.append("priority record does not contain the full structural fields")
    if call["end"] is not None and call["end"] != [len(sources), total_entries]:
        errors.append("end counts disagree with retained source/entry records")
    groups = {}
    for source in sources.values():
        signature = [(i, e["declaration"], e["property"]) for i, e in sorted(source["entries"].items())]
        previous = groups.setdefault(source["block"], signature)
        if previous != signature:
            errors.append("one retained block has inconsistent declaration entries")
    same_phase = []
    cross_phase = []
    adjacent = []
    ordered = sorted(sources.values(), key=lambda source: source["node"])
    if not errors:
        for left, right in itertools.combinations(ordered, 2):
            if left["direct"] or right["direct"] or left["block"] != right["block"]:
                continue
            shared = list(left["entries"].values())
            if not shared:
                continue
            pair = {
                "nodes": [left["node"], right["node"]],
                "source_events": [left["event_index"], right["event_index"]],
                "block": left["block"], "shared_entries": shared,
                "normalized_priority": left["normalized_priority"],
            }
            if left["raw_priority"] == right["raw_priority"]:
                if left["important"] != right["important"] or left["normalized_priority"] != right["normalized_priority"]:
                    errors.append("equal raw priorities disagree on importance or normalization")
                    continue
                pair["partition"] = "important" if left["important"] else "ordinary"
                pair["raw_priority"] = left["raw_priority"]
                pair["intervening_sources"] = [
                    {"node": middle["node"], "block": middle["block"],
                     "raw_priority": middle["raw_priority"], "event_index": middle["event_index"]}
                    for middle in ordered
                    if left["node"] < middle["node"] < right["node"] and middle["block"] != left["block"]
                ]
                (same_phase if pair["intervening_sources"] else adjacent).append(pair)
            elif (left["normalized_priority"] == right["normalized_priority"]
                  and left["important"] != right["important"]):
                pair["raw_priorities"] = [left["raw_priority"], right["raw_priority"]]
                cross_phase.append(pair)
    if errors:
        same_phase, cross_phase, adjacent = [], [], []
    return {
        "pid": call["pid"], "call": call["call"],
        "complete_uncapped_roster": not errors,
        "errors": errors, "caps": call["caps"],
        "first_event_index": call["first_event_index"], "last_event_index": call["last_event_index"],
        "source_count": len(sources), "entry_count": total_entries,
        "candidate_phase_context": call["phase_context"],
        "candidate_phase_contexts": call["phase_contexts"],
        "phase_binding": "transport interval only; no content-PID or element identity in phase markers",
        "same_raw_priority_nonadjacent_pairs": same_phase,
        "same_raw_priority_adjacent_pairs": adjacent,
        "ordinary_important_pairs": cross_phase,
        "sources": ordered,
    }


def analyze_records(records):
    calls, active_phases, phase_events, global_errors, call_caps = {}, {}, [], [], []
    for event_index, record in enumerate(records):
        if record.get("action") != "process_output":
            continue
        data = record.get("data")
        if not isinstance(data, str):
            continue
        transport = str(record.get("process", "unknown"))
        for subline, line in enumerate(data.splitlines()):
            if line.startswith(PHASE):
                try:
                    phase = json.loads(line[len(PHASE):])
                    event = phase["event"]
                    assert event in ["begin-setup", "end-setup", "begin-read", "end-read"]
                    assert phase["family"] in ["selector-list", "cache-clone", "implicit-scope"]
                    assert phase["direction"] in ["ltr", "rtl"] and type(phase["independent"]) is bool
                    if event.endswith("read"):
                        assert isinstance(phase["phase"], str)
                except (ValueError, KeyError, TypeError, AssertionError):
                    global_errors.append(f"malformed phase at event {event_index}:{subline}")
                    continue
                context = {"transport_process": transport, "event_index": event_index, **phase}
                phase_events.append(context)
                if event.startswith("begin"):
                    if transport in active_phases:
                        global_errors.append(f"overlapping phase intervals at event {event_index}")
                    active_phases[transport] = context
                else:
                    opened = active_phases.pop(transport, None)
                    fields = ["family", "direction", "independent", "phase"]
                    if (opened is None or opened["event"].replace("begin", "end") != event
                            or any(opened.get(key) != phase.get(key) for key in fields)):
                        global_errors.append(f"unmatched phase end at event {event_index}")
                continue
            if not line.startswith(NATIVE):
                if NATIVE in line or PHASE in line:
                    global_errors.append(f"unsupported embedded marker at event {event_index}:{subline}")
                continue
            match = HEADER.fullmatch(line[len(NATIVE):])
            if not match:
                global_errors.append(f"malformed native header at event {event_index}:{subline}")
                continue
            pid, identifier, event, rest = match.groups()
            pid = int(pid)
            if event == "call-cap" and identifier is None and rest == "limit=128":
                call_caps.append({"pid": pid, "event_index": event_index})
                continue
            if identifier is None or int(identifier) >= 128:
                global_errors.append(f"missing/out-of-range call at event {event_index}")
                continue
            identifier = int(identifier)
            key = (pid, identifier)
            call = calls.setdefault(key, {
                "pid": pid, "call": identifier, "sources": {}, "end": None, "caps": [], "errors": [],
                "first_event_index": event_index, "last_event_index": event_index,
                "phase_context": active_phases.get(transport),
                "phase_contexts": [active_phases.get(transport)],
            })
            call["last_event_index"] = event_index
            if call["end"] is not None:
                call["errors"].append(f"record after end at event {event_index}")
            if active_phases.get(transport) not in call["phase_contexts"]:
                call["phase_contexts"].append(active_phases.get(transport))
            try:
                if event in ["source", "direct"]:
                    if event == "source":
                        found = SOURCE.fullmatch(rest)
                        assert found
                        node, block, count, important, priority, normalized = found.groups()
                        node, count = int(node), int(count)
                    else:
                        found = re.fullmatch(rf"block=({ADDRESS}) entries=(\d+)", rest)
                        assert found
                        block, count = found.groups()
                        node, count, important, priority, normalized = 0, int(count), None, None, None
                    assert node < 64 and node not in call["sources"]
                    assert not call["sources"] or node > max(call["sources"])
                    call["sources"][node] = {
                        "node": node, "block": block, "expected_entries": count, "entries": {},
                        "direct": event == "direct", "important": important == "true",
                        "raw_priority": priority, "normalized_priority": normalized,
                        "event_index": event_index,
                    }
                elif event == "entry":
                    found = ENTRY.fullmatch(rest)
                    assert found
                    node, entry, block, declaration, prop = found.groups()
                    node, entry = int(node), int(entry)
                    source = call["sources"][node]
                    assert source["block"] == block and entry < 8 and entry not in source["entries"]
                    source["entries"][entry] = {"entry": entry, "declaration": declaration,
                                                "property": prop, "event_index": event_index}
                elif event == "end":
                    found = re.fullmatch(r"sources=(\d+) entries=(\d+)", rest)
                    assert found
                    call["end"] = list(map(int, found.groups()))
                elif event in ["entry-cap", "node-cap"]:
                    assert ((event == "entry-cap" and re.fullmatch(r"node=\d+ limit=8", rest))
                            or (event == "node-cap" and rest == "limit=64"))
                    call["caps"].append({"event": event, "event_index": event_index, "details": rest})
                else:
                    raise ValueError("unknown native event")
            except (ValueError, KeyError, TypeError, AssertionError):
                call["errors"].append(f"malformed/duplicate/out-of-order {event} at event {event_index}")
    if active_phases:
        global_errors.append("unclosed phase intervals")
    assessed = [assess_call(call) for call in calls.values()]
    return {
        "input_format": "WPT process_output JSONL; event indices are zero-based parsed records",
        "input_integrity_ok": not global_errors and all(not call["errors"] for call in assessed),
        "global_errors": global_errors, "call_caps": call_caps, "phase_events": phase_events,
        "native_call_count": len(assessed),
        "native_observation_present": bool(assessed),
        "complete_uncapped_calls": sum(call["complete_uncapped_roster"] for call in assessed),
        "same_phase_nonadjacent_pairs": sum(len(call["same_raw_priority_nonadjacent_pairs"]) for call in assessed),
        "ordinary_important_pairs": sum(len(call["ordinary_important_pairs"]) for call in assessed),
        "same_phase_pairs_by_partition": {
            partition: sum(pair["partition"] == partition for call in assessed
                           for pair in call["same_raw_priority_nonadjacent_pairs"])
            for partition in ["ordinary", "important"]
        },
        "calls": assessed,
        "limits": ["No pointer identity joins across calls, PIDs or input files",
                   "A call cap limits later observations; earlier complete calls remain bounded evidence",
                   "Phase markers provide transport context, not a certified element/cascade join",
                   "Roster membership does not prove a declaration was evaluated or excluded"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    raw = args.raw.read_bytes()
    records = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    result = analyze_records(records)
    result["input"] = {"path": str(args.raw), "sha256": hashlib.sha256(raw).hexdigest(), "records": len(records)}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ["input_integrity_ok", "complete_uncapped_calls",
                                                   "same_phase_nonadjacent_pairs", "ordinary_important_pairs"]}))
    return 0 if result["input_integrity_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
