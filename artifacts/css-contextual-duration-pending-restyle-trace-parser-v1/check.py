import copy
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("trace_parser", Path(__file__).with_name("trace.py"))
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


def event(stage, **changes):
    result = dict(pid=10, seq=1, id="coupled-override", element="0x123", pseudo=0,
                  identifier="0x0", stage=stage, cascade=0, request=2,
                  present=1, bit=1, servo=0, pre=0, root="0x0", flags=0,
                  effect="0x0", animation="0x0")
    if stage.startswith("post-"):
        result.update(request=-1, present=-1, bit=-1)
    if stage.startswith("pre-"):
        result.update(request=-1, pre=1)
    result.update(changes)
    return result


def encode(events):
    return "\n".join(trace.PREFIX + " ".join(f"{k}={v}" for k, v in event.items()) for event in events)


def numbered(events):
    counts = {}
    result = [copy.deepcopy(item) for item in events]
    for event in result:
        counts[event["pid"]] = counts.get(event["pid"], 0) + 1
        event["seq"] = counts[event["pid"]]
    return result


seed = [event("request-before", present=0, bit=0, servo=1),
        event("request-set", servo=1), event("post-deferred", servo=1)]
outside = [event("request-before"), event("request-coalesced")]
sample = numbered(seed + outside)
result = trace.parse(encode(sample))
assert result["trace_syntax_and_sequence_valid"] and len(result["bounded_candidate_witnesses"]) == 1
assert result["events_in_input_order"][0]["seq"] == 1
carrier = "\n".join(json.dumps({"action": "process_output", "data": line}) for line in encode(sample).splitlines())
assert trace.parse(carrier)["bounded_candidate_witnesses"] == result["bounded_candidate_witnesses"]
pre = copy.deepcopy(sample)
for item in pre[:3]:
    item.update(servo=0, pre=1)
assert len(trace.parse(encode(pre))["bounded_candidate_witnesses"]) == 1
prepared = trace.parse(encode(numbered(seed + [event("pre-will-compose")] + outside)))
assert len(prepared["bounded_candidate_witnesses"]) == 1
assert prepared["bounded_candidate_witnesses"][0]["actual_composition_or_effective_timing_change_proved"] is False
rejected = []
for stage in sorted(trace.INVALIDATORS):
    observed = trace.parse(encode(numbered(seed + [event(stage)] + outside)))
    assert observed["trace_syntax_and_sequence_valid"] and not observed["bounded_candidate_witnesses"]
    rejected.append(stage)
for key, value in (("pid", 11), ("element", "0x456"), ("pseudo", 2),
                   ("identifier", "0x77"), ("cascade", 1), ("id", "zero-start-override")):
    changed = copy.deepcopy(outside)
    for item in changed:
        item[key] = value
    observed = trace.parse(encode(numbered(seed + changed)))
    assert observed["trace_syntax_and_sequence_valid"] and not observed["bounded_candidate_witnesses"]
    rejected.append("cross-key " + key)
standard = copy.deepcopy(outside)
for item in standard:
    item["request"] = 1
assert not trace.parse(encode(numbered(seed + standard)))["bounded_candidate_witnesses"]
rejected.append("outside Standard is not Layer")
for label, mutate in [
    ("gap", lambda s: s[-1].update(seq=9)),
    ("duplicate", lambda s: s[-1].update(seq=4)),
    ("unknown ID", lambda s: s[-1].update(id="other")),
    ("unknown stage", lambda s: s[-1].update(stage="composed")),
    ("null element", lambda s: s[-1].update(element="0x000")),
    ("invalid bit", lambda s: s[-1].update(bit=4)),
    ("invalid coalesced bit", lambda s: s[-1].update(bit=0)),
    ("deferred outside", lambda s: s[2].update(servo=0)),
]:
    changed = copy.deepcopy(sample)
    mutate(changed)
    observed = trace.parse(encode(changed))
    assert observed["errors"] and not observed["bounded_candidate_witnesses"]
    rejected.append(label)
for label, text in (("trailing text", encode(sample) + " extra"),
                    ("pre-stage outside PreTraverse", encode(numbered(seed + [event("pre-will-compose", pre=0)] + outside))),
                    ("unsupported JSON", json.dumps({"message": encode(sample)})),
                    ("premature cap", encode(sample) + "\n" + trace.PREFIX + "pid=10 cap-exhausted limit=4096")):
    observed = trace.parse(text)
    assert observed["errors"] and not observed["bounded_candidate_witnesses"]
    rejected.append(label)
long_stream = numbered(seed + outside + [event("request-before")] * (4096 - 5))
capped = trace.parse(encode(long_stream) + "\n" + trace.PREFIX + "pid=10 cap-exhausted limit=4096")
assert capped["truncated"] and capped["trace_syntax_and_sequence_valid"]
assert len(capped["bounded_candidate_witnesses"]) == 1
assert not trace.parse("")["trace_syntax_and_sequence_valid"]
print(json.dumps({"positive_cases": ["Servo deferred witness", "PreTraverse deferred witness", "mozlog carrier", "WillCompose preparation does not prove composition", "explicit cap retains only bounded prefix witness"],
                  "negative_cases": rejected, "empty_capture_not_valid": True,
                  "native_trace_executed": False}, indent=2))
