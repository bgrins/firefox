import collections
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMAS = {
    "request": "compositor target_node pseudo pseudo_id level type posted_before",
    "request-post": "compositor target_node pseudo pseudo_id level skip",
    "post-deferred": "compositor target_node normalized_node pseudo pseudo_id level pretraverse",
    "post-shell": "compositor target_node normalized_node pseudo pseudo_id level",
    "pre-enter": "compositor root_node flags",
    "pre-queue": "compositor level count",
    "pre-remaining": "compositor level count",
    "pre-exit": "compositor found",
    "pre-selected": "compositor target_node pseudo pseudo_id level posted",
    "will-compose": "compositor effect target_node pseudo pseudo_id level",
    "select-remove": "compositor target_node pseudo pseudo_id level",
    "hint-map": "target_node normalized_node pseudo pseudo_id animation transition",
    "hint-posted": "node hint merged",
    "hint-discard": "node hint reason",
    "restyle": "node flags hint kind admitted_animation initial thread",
    "installed": "node style flags initial font_px thread",
    "document-enter": "set document call flags",
    "document-root": "set call iteration root_node flags",
    "document-exit": "set call iteration post",
    "document-no-root": "set call",
    "drain-selected": "set call iteration",
}
MARKERS = ["startup:activation", "unrelated restyle:activation", "unrelated:mutation"]
KEY = ("compositor", "target_node", "pseudo", "pseudo_id", "level")


def parse(row, index):
    text = row.get("data", "")
    match = re.fullmatch(r"RFDP pid=(\d+) ([\w-]+) (.*)", text)
    assert match and text.count("RFDP") == 1, (index, "malformed event")
    pid, event, payload = match.groups()
    assert event in SCHEMAS, (index, "unknown or capped event")
    fields = re.findall(r"(\w+)=(.*?)(?= \w+=|$)", payload)
    assert " ".join(k for k, _ in fields) == SCHEMAS[event], (index, "field schema")
    assert " ".join(k + "=" + v for k, v in fields) == payload
    return dict(fields, pid=pid, event=event, index=index)


def key(event):
    return tuple(event[field] for field in KEY)


def analyze(rows):
    assert collections.Counter(
        (r["action"], r["status"])
        for r in rows
        if r["action"] in ("test_status", "test_end")
    ) == {("test_status", "PASS"): 2, ("test_end", "OK"): 1}
    assert not any("capped" in r.get("data", "") for r in rows)
    episodes = []
    content_pid = None
    for name in MARKERS:
        starts = [
            i for i, r in enumerate(rows) if r.get("data") == "RFDP_JS_BEGIN " + name
        ]
        ends = [
            i
            for i, r in enumerate(rows)
            if r.get("data") == "RFDP_JS_END " + name + " actual=512px"
        ]
        assert len(starts) == len(ends) == 1 and starts[0] < ends[0]
        start, end = starts[0], ends[0]
        events = [
            parse(r, i)
            for i, r in enumerate(rows[start + 1 : end], start + 1)
            if r["action"] == "process_output"
        ]
        selected_pids = {e["pid"] for e in events if e["event"] == "pre-selected"}
        if name.endswith(":activation"):
            assert len(selected_pids) == 1
            pid = selected_pids.pop()
            assert content_pid is None or content_pid == pid
            content_pid = pid
        else:
            assert not selected_pids and content_pid is not None
            pid = content_pid
        events = [e for e in events if e["pid"] == pid]
        compositors = {e["compositor"] for e in events if "compositor" in e}
        style_sets = {e["set"] for e in events if "set" in e}
        documents = {e["document"] for e in events if "document" in e}
        threads = {e["thread"] for e in events if "thread" in e}
        assert (
            len(compositors) == len(style_sets) == len(documents) == len(threads) == 1
        )
        queue = collections.defaultdict(list)
        in_flight = []
        deliveries = []
        selections = []
        admissions = {}
        drains = []
        active_call = None
        for pos, event in enumerate(events):
            kind = event["event"]
            if kind == "document-enter":
                assert active_call is None
                active_call = (event["set"], event["call"])
            elif kind in ("document-exit", "document-no-root"):
                assert active_call == (event["set"], event["call"])
                assert not in_flight
                active_call = None
            elif kind in ("pre-queue", "pre-remaining"):
                assert int(event["count"]) == sum(
                    1
                    for identity in queue
                    if identity[0] == event["compositor"]
                    and identity[4] == event["level"]
                )
            elif kind == "document-root":
                assert active_call == (event["set"], event["call"])
            elif kind == "request":
                assert event["type"] in ("1", "2"), (
                    "Throttled requests need a separate account"
                )
                queue[key(event)].append(event["index"])
            elif kind == "pre-selected":
                identity = key(event)
                assert active_call is not None
                assert queue[identity], (
                    "Selection has no request within marked interval"
                )
                mapped, posted, composed, removed = events[pos + 1 : pos + 5]
                assert [e["event"] for e in [mapped, posted, composed, removed]] == [
                    "hint-map",
                    "hint-posted",
                    "will-compose",
                    "select-remove",
                ]
                assert all(
                    mapped[f] == event[f]
                    for f in ("target_node", "pseudo", "pseudo_id")
                )
                assert (mapped["animation"], mapped["transition"]) == (
                    ("1", "0") if event["level"] == "0" else ("0", "1")
                )
                assert event["level"] in ("0", "1")
                assert mapped["normalized_node"] != "0x0"
                assert mapped["normalized_node"] == posted["node"]
                hint = (
                    "RESTYLE_CSS_ANIMATIONS"
                    if event["level"] == "0"
                    else "RESTYLE_CSS_TRANSITIONS"
                )
                assert hint in posted["hint"] and hint in posted["merged"]
                assert key(composed) == key(removed) == identity
                assert not any(d["key"] == identity for d in in_flight)
                delivery = {
                    "key": identity,
                    "requests": queue.pop(identity),
                    "selected": event["index"],
                    "mapped": mapped["index"],
                    "posted": posted["index"],
                    "removal_intent": removed["index"],
                    "node": posted["node"],
                    "hint": hint,
                    "document_call": active_call,
                }
                selections.append(event["index"])
                in_flight.append(delivery)
            elif kind == "hint-discard":
                raise AssertionError("Hint discard inside marked interval")
            elif kind == "restyle":
                admissions[event["node"]] = event
            elif kind == "installed":
                for delivery in list(in_flight):
                    if delivery["node"] != event["node"]:
                        continue
                    admitted = admissions[event["node"]]
                    assert delivery["posted"] < admitted["index"] < event["index"]
                    assert (
                        "AnimationOnly" in admitted["flags"]
                        and "AnimationOnly" in event["flags"]
                    )
                    assert delivery["hint"] in admitted["hint"]
                    assert admitted["kind"] != "None"
                    assert admitted["thread"] == event["thread"]
                    assert delivery["document_call"] == active_call
                    delivery.update(
                        admitted=admitted["index"],
                        installed=event["index"],
                        font_px=event["font_px"],
                    )
                    deliveries.append(delivery)
                    in_flight.remove(delivery)
            elif kind == "drain-selected":
                assert selections and in_flight
                assert active_call == (event["set"], event["call"])
                drains.append({
                    "index": event["index"],
                    "iteration": event["iteration"],
                    "selected": len(selections),
                })
                selections.clear()
        assert not queue and not in_flight and not selections and active_call is None
        if name.endswith(":activation"):
            assert [d["selected"] for d in drains] == [4, 3, 2, 1]
            assert [d["iteration"] for d in drains] == ["1", "2", "3", "4"]
            assert len(deliveries) == 10
        else:
            assert not deliveries and not drains
        episodes.append({
            "name": name,
            "start": start,
            "end": end,
            "pid": pid,
            "events": len(events),
            "drains": drains,
            "deliveries": deliveries,
            "request_events": sum(len(d["requests"]) for d in deliveries),
            "compositor": next(iter(compositors)),
            "style_set": next(iter(style_sets)),
            "document": next(iter(documents)),
            "thread": next(iter(threads)),
        })
    assert all(a["end"] < b["start"] for a, b in zip(episodes, episodes[1:]))
    return episodes


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    raw = HERE / "runtime1/wpt-raw.jsonl"
    rows = [json.loads(line) for line in raw.read_text().splitlines()]
    episodes = analyze(rows)
    first = episodes[0]["deliveries"][0]
    controls = []

    def reject(name, mutate):
        changed = copy.deepcopy(rows)
        mutate(changed)
        try:
            analyze(changed)
        except AssertionError as error:
            controls.append({"name": name, "rejected": True, "reason": str(error)})
        else:
            raise AssertionError("Accepted negative control: " + name)

    def replace(index, before, after):
        def change(changed):
            assert before in changed[index]["data"]
            changed[index]["data"] = changed[index]["data"].replace(before, after, 1)

        return change

    reject("missing hint insertion", lambda r: r.pop(first["posted"]))
    reject("missing installation", lambda r: r.pop(first["installed"]))
    reject("wrong cascade level", replace(first["selected"], "level=0", "level=1"))
    reject(
        "wrong pseudo argument",
        replace(first["mapped"], "pseudo_id=0x0", "pseudo_id=0x1"),
    )
    reject(
        "wrong normalized node",
        replace(
            first["mapped"], "normalized_node=" + first["node"], "normalized_node=0x1"
        ),
    )
    reject(
        "ordinary traversal used as delivery",
        replace(first["installed"], "AnimationOnly | ", ""),
    )
    reject(
        "missing request cohort",
        lambda r: [r[i].update(action="log") for i in first["requests"]],
    )
    reject(
        "new request erased by old completion",
        lambda r: r.insert(first["installed"], copy.deepcopy(r[first["requests"][-1]])),
    )
    reject("trace cap", replace(first["posted"], "hint-posted", "capped"))
    reject(
        "interleaved trace record",
        replace(first["posted"], " merged=", " RFDP pid=1 merged="),
    )
    reject(
        "wrong document call",
        replace(
            episodes[0]["drains"][0]["index"],
            "call=" + first["document_call"][1],
            "call=999",
        ),
    )
    reject(
        "different installer thread",
        replace(first["installed"], "ThreadId(4)", "ThreadId(999)"),
    )
    outside = []
    for i, row in enumerate(rows):
        if "RFDP" not in row.get("data", "") or row.get("data", "").startswith(
            "RFDP_JS_"
        ):
            continue
        if any(e["start"] < i < e["end"] for e in episodes):
            continue
        try:
            parse(row, i)
        except AssertionError:
            outside.append(i)
    result = {
        "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "row_indices": "zero-based JSONL records",
        "episodes": episodes,
        "negative_controls": controls,
        "malformed_records_outside_intervals": outside,
        "claim": "Observed selected request cohorts reach actual style installation within each marked activation interval",
        "native_refinement_proved": False,
        "termination_proved": False,
    }
    (HERE / "ANALYSIS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps({
            "episodes": [
                {k: e[k] for k in ("name", "events", "request_events")}
                for e in episodes
            ],
            "controls": len(controls),
            "malformed_outside": len(outside),
        })
    )


if __name__ == "__main__":
    main()
