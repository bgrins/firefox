import copy
import json

from analyze import NATIVE, PHASE, analyze_records


def priority(important=False, flags="0x0"):
    return f"CascadePriority {{ cascade_level: CascadeLevel({12 if important else 4}), flags: RuleCascadeFlags({flags}), layer_order: LayerOrder(0) }}"


def raw(text):
    return {"action": "process_output", "pid": 100, "process": "200", "data": text}


def roster(blocks, *, pid=201, call=0, importance=None, flags=None):
    lines = []
    importance = importance or [False] * len(blocks)
    flags = flags or ["0x0"] * len(blocks)
    for node, (block, important, flag) in enumerate(zip(blocks, importance, flags)):
        lines.append(raw(NATIVE + f"pid={pid} call={call} event=source node={node} block=0x{block:x} entries=1 important={str(important).lower()} priority={priority(important, flag)} normalized={priority(False, flag)}"))
        lines.append(raw(NATIVE + f"pid={pid} call={call} event=entry node={node} entry=0 block=0x{block:x} declaration=0x{block + 100:x} property=Longhand(MarginLeft)"))
    lines.append(raw(NATIVE + f"pid={pid} call={call} event=end sources={len(blocks)} entries={len(blocks)}"))
    return lines


def main():
    checks = []

    def check(name, condition):
        assert condition, name
        checks.append(name)

    good = roster([10, 20, 10])
    result = analyze_records(good)
    check("nonadjacent same-phase pointer witness", result["input_integrity_ok"] and result["same_phase_nonadjacent_pairs"] == 1)
    check("embedded content PID, not transport or harness PID", result["calls"][0]["pid"] == 201)
    check("ordinary classification", result["calls"][0]["same_raw_priority_nonadjacent_pairs"][0]["partition"] == "ordinary")
    result = analyze_records(roster([10, 20, 10], importance=[True] * 3))
    check("important classification", result["calls"][0]["same_raw_priority_nonadjacent_pairs"][0]["partition"] == "important")
    result = analyze_records(roster([10, 10], importance=[True, False]))
    check("normal/important pair is not a repeated-occurrence witness", result["same_phase_nonadjacent_pairs"] == 0 and result["ordinary_important_pairs"] == 1)
    result = analyze_records(roster([10, 20, 10], flags=["0x0", "0x0", "0x1"]))
    check("flags retained in equality", result["same_phase_nonadjacent_pairs"] == 0)
    result = analyze_records(roster([10, 10]))
    check("adjacent copies reported separately", result["same_phase_nonadjacent_pairs"] == 0 and len(result["calls"][0]["same_raw_priority_adjacent_pairs"]) == 1)
    result = analyze_records(roster([10], pid=201) + roster([10], pid=202))
    check("no cross-PID join", result["same_phase_nonadjacent_pairs"] == 0 and len(result["calls"]) == 2)
    result = analyze_records(roster([10], call=0) + roster([10], call=1))
    check("no cross-call join", result["same_phase_nonadjacent_pairs"] == 0 and len(result["calls"]) == 2)
    for name, records in [
        ("missing end", good[:-1]),
        ("missing entry", good[:1] + good[2:]),
        ("missing whole source", good[2:]),
        ("duplicate source", good[:2] + good),
        ("trailing record after end", good + good[:1]),
        ("entry cap", good[:-1] + [raw(NATIVE + "pid=201 call=0 event=entry-cap node=0 limit=8")] + good[-1:]),
        ("node cap", good[:-1] + [raw(NATIVE + "pid=201 call=0 event=node-cap limit=64")]),
    ]:
        result = analyze_records(records)
        check(name + " rejects completeness", not result["input_integrity_ok"] and result["same_phase_nonadjacent_pairs"] == 0)
    inconsistent = copy.deepcopy(good)
    inconsistent[5]["data"] = inconsistent[5]["data"].replace("declaration=0x6e", "declaration=0xff")
    result = analyze_records(inconsistent)
    check("inconsistent retained entry addresses rejected", not result["input_integrity_ok"] and result["same_phase_nonadjacent_pairs"] == 0)
    result = analyze_records(good + [raw(NATIVE + "pid=999 event=call-cap limit=128")])
    check("unrelated PID cap does not erase complete witness", result["same_phase_nonadjacent_pairs"] == 1 and result["call_caps"][0]["pid"] == 999)
    result = analyze_records(good + [raw(NATIVE + "pid=201 event=call-cap limit=128")])
    check("later same-PID cap limits run coverage, not completed roster", result["same_phase_nonadjacent_pairs"] == 1)
    begin = {"family": "cache-clone", "direction": "ltr", "independent": False,
             "phase": "initial-rollback", "event": "begin-read"}
    end = {**begin, "event": "end-read"}
    result = analyze_records([raw(PHASE + json.dumps(begin)), *good, raw(PHASE + json.dumps(end))])
    context = result["calls"][0]["candidate_phase_context"]
    check("phase transport context is explicitly weak", context["transport_process"] == "200" and "no content-PID" in result["calls"][0]["phase_binding"])
    result = analyze_records([raw(PHASE + json.dumps(begin)), *good])
    check("missing phase end reports incomplete interval", not result["input_integrity_ok"])
    print(json.dumps({"synthetic_checks": len(checks), "checks": checks,
                      "actual_native_observation": False}, indent=2))


if __name__ == "__main__":
    main()
