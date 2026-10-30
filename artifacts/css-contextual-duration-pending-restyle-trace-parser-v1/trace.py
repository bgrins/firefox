import argparse
import json
import re
from pathlib import Path

PREFIX = "DURATION_RESTYLE_TRACE "
IDS = {f"{kind}-{role}" for kind in ("coupled", "zero-start")
       for role in ("passive", "seek", "outline", "override", "literal")}
STAGES = {
    "request-before", "request-throttled", "request-set", "request-coalesced",
    "post-deferred", "post-dispatch", "pre-skip-throttled", "pre-skip-no-shell",
    "pre-skip-subtree", "pre-selected", "pre-remove-wrong-document",
    "pre-post-hint", "pre-remove-no-effects", "pre-will-compose",
    "pre-remove-consumed", "pre-clear",
}
INVALIDATORS = {"post-dispatch", "pre-post-hint", "pre-remove-wrong-document",
                "pre-remove-no-effects", "pre-remove-consumed", "pre-clear"}
POINTER = r"(?:0x[0-9a-fA-F]+|\(nil\)|0)"
EVENT = re.compile(
    r"pid=(?P<pid>\d+) seq=(?P<seq>\d+) id=(?P<id>[a-z-]+) "
    rf"element=(?P<element>{POINTER}) pseudo=(?P<pseudo>\d+) identifier=(?P<identifier>{POINTER}) "
    r"stage=(?P<stage>[a-z-]+) cascade=(?P<cascade>-?\d+) request=(?P<request>-?\d+) "
    r"present=(?P<present>-?\d+) bit=(?P<bit>-?\d+) servo=(?P<servo>\d+) pre=(?P<pre>\d+) "
    rf"root=(?P<root>{POINTER}) flags=(?P<flags>\d+) effect=(?P<effect>{POINTER}) animation=(?P<animation>{POINTER})"
)
CAP = re.compile(r"pid=(?P<pid>\d+) cap-exhausted limit=4096")
INTEGERS = {"pid", "seq", "pseudo", "cascade", "request", "present", "bit", "servo", "pre", "flags"}


def stage_fields(event):
    stage = event["stage"]
    if stage.startswith("request-"):
        if not (event["cascade"] in (0, 1) and event["present"] in (0, 1)
                and event["bit"] in (0, 1) and event["request"] in (0, 1, 2)):
            return False
        if stage in ("request-set", "request-coalesced"):
            return event["present"] == event["bit"] == 1 and event["request"] in (1, 2)
        if stage == "request-throttled":
            return event["present"] == 1 and event["request"] == 0
        return event["present"] == 1 or event["bit"] == 0
    if stage.startswith("post-"):
        return (event["cascade"] in (0, 1)
                and event["request"] == event["present"] == event["bit"] == -1
                and bool(event["servo"] or event["pre"]) == (stage == "post-deferred"))
    unknown_cascade = stage in {"pre-selected", "pre-skip-throttled", "pre-skip-no-shell", "pre-skip-subtree"}
    return (event["pre"] == 1 and event["cascade"] in ((-1,) if unknown_cascade else (0, 1))
            and event["request"] == -1 and event["present"] == 1 and event["bit"] in (0, 1))


def event_key(event):
    return tuple(event[k] for k in ("pid", "id", "element", "pseudo", "identifier", "cascade"))


def identify(event):
    kind = "zero-start" if event["id"].startswith("zero-start-") else "coupled"
    return {"kind": kind, "role": event["id"][len(kind) + 1:],
            "dom_id": "duration-feedback-" + event["id"]}


def witnesses(events):
    by_pid = {}
    for event in events:
        by_pid.setdefault(event["pid"], []).append(event)
    found = []
    for stream in by_pid.values():
        pending = {}
        for i, event in enumerate(stream):
            key = event_key(event)
            if event["stage"] in INVALIDATORS or (
                event["stage"] == "request-before" and event["bit"] == 0
            ):
                pending.pop(key, None)
            if i >= 2 and event["stage"] == "post-deferred":
                before, changed = stream[i - 2:i]
                if (before["stage"] == "request-before" and before["bit"] == 0
                    and changed["stage"] == "request-set" and changed["bit"] == 1
                    and before["request"] == changed["request"] in (1, 2)
                    and event_key(before) == event_key(changed) == key
                    and (before["servo"], before["pre"]) == (changed["servo"], changed["pre"]) == (event["servo"], event["pre"])
                    and (event["servo"] or event["pre"])):
                    pending[key] = [before["seq"], changed["seq"], event["seq"]]
            if i and event["stage"] == "request-coalesced" and key in pending:
                before = stream[i - 1]
                if (before["stage"] == "request-before"
                    and event_key(before) == key
                    and before["request"] == event["request"] == 2
                    and before["present"] == before["bit"] == event["present"] == event["bit"] == 1
                    and not any((before["servo"], before["pre"], event["servo"], event["pre"]))):
                    found.append({
                        **identify(event), "pid": event["pid"], "element": event["element"],
                        "pseudo": event["pseudo"], "identifier": event["identifier"],
                        "cascade": event["cascade"], "deferred_request_sequences": pending[key],
                        "outside_coalesced_layer_sequences": [before["seq"], event["seq"]],
                        "no_intervening_logged_post_attempt_or_removal_boundary": True,
                        "actual_composition_or_effective_timing_change_proved": False,
                    })
    return found


def parse(text):
    events, caps, errors = [], [], []
    sequences, capped = {}, set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if PREFIX not in line:
            continue
        if line.lstrip().startswith("{"):
            try:
                record = json.loads(line)
                assert record.get("action") == "process_output"
                line = record["data"]
                assert isinstance(line, str)
            except (ValueError, KeyError, AssertionError, TypeError):
                errors.append({"line": line_number, "reason": "unsupported or malformed JSON carrier"})
                continue
        for part_number, part in enumerate(line.splitlines(), 1):
            if PREFIX not in part:
                continue
            body = part.split(PREFIX, 1)[1]
            location = {"line": line_number, "part": part_number}
            match = CAP.fullmatch(body)
            if match:
                pid = int(match["pid"])
                if pid <= 0 or pid in capped or sequences.get(pid) != 4096:
                    errors.append(dict(location, reason="cap without exactly 4096 preceding events"))
                capped.add(pid)
                caps.append(dict(location, pid=pid, limit=4096))
                continue
            match = EVENT.fullmatch(body)
            if not match:
                errors.append(dict(location, reason="malformed trace event", text=body))
                continue
            event = match.groupdict()
            for key in INTEGERS:
                event[key] = int(event[key])
            for key in ("element", "identifier", "root", "effect", "animation"):
                event[key] = "0x0" if event[key] in ("0", "(nil)") else hex(int(event[key], 16))
            valid = (event["id"] in IDS and event["stage"] in STAGES
                     and event["pid"] > 0 and event["element"] != "0x0"
                     and 1 <= event["seq"] <= 4096 and event["pid"] not in capped
                     and event["seq"] == sequences.get(event["pid"], 0) + 1
                     and event["cascade"] in (-1, 0, 1) and event["request"] in (-1, 0, 1, 2)
                     and event["present"] in (-1, 0, 1) and event["bit"] in (-1, 0, 1)
                     and event["servo"] in (0, 1) and event["pre"] in (0, 1)
                     and stage_fields(event))
            if not valid:
                errors.append(dict(location, reason="invalid field, unknown label, or sequence discontinuity"))
            sequences[event["pid"]] = event["seq"]
            events.append(dict(event, **location))
    return {
        "events_in_input_order": events, "cap_markers": caps, "errors": errors,
        "trace_syntax_and_sequence_valid": bool(events) and not errors,
        "truncated": bool(caps),
        "observed_ids": sorted({event["id"] for event in events}),
        "missing_ids": sorted(IDS - {event["id"] for event in events}),
        "bounded_candidate_witnesses": witnesses(events) if events and not errors else [],
        "limits": [
            "A cap marks truncation; any witness only concerns its closed recorded sequence interval.",
            "No cap is not proof of full capture; terminal and capture-integrity checks are external.",
            "Posts and removals are instrumented preparation/call boundaries, not successful composition.",
            "pre-will-compose is preparation, not evidence that ComposeStyle executed.",
            "Layer requests are not assumed to be effective timing changes or model iterations.",
            "Role labels do not identify the exact JavaScript call or align event time with a snapshot.",
            "Compositor destruction, uninstrumented wakeups, adoption and cross-document identity are outside this witness.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    result = parse(args.trace.read_text())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["trace_syntax_and_sequence_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
