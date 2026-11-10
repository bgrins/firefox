import collections
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "css-animation-initial-admission-native-20261110-v1/analyze.py"
PRIOR_HASH = "2221b39d5aac6655482ed49e7dc0064b4bb642f6d1484cf83e298e57579b251f"
MODES = ("smil-scroll", "normal-scroll", "smil-scope-only")
PHASES = (
    "stimulus-begin",
    "stimulus-return",
    "getter-begin",
    "getter-return",
    "complete",
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def prior_analyzer():
    require(
        hashlib.sha256(PRIOR.read_bytes()).hexdigest() == PRIOR_HASH,
        "Prior analyzer changed",
    )
    spec = importlib.util.spec_from_file_location("initial_admission", PRIOR)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    schemas = json.loads((HERE / "TRACE-SCHEMAS.json").read_text())
    module.SCHEMAS.update(schemas["new_events"])
    module.ROLES.update(schemas["added_fixed_roles"])
    return module


def parse_trace(rows):
    prior = prior_analyzer()
    events, markers, malformed, caps = {}, collections.defaultdict(list), [], []
    for index, row in enumerate(rows):
        text = row.get("data", "")
        if "NT_PROBE" in text:
            require(
                text.startswith("NT_PROBE ") and text.count("NT_PROBE") == 1,
                "Malformed marker",
            )
            marker = json.loads(text[len("NT_PROBE ") :])
            require(
                marker.get("mode") in MODES and marker.get("phase") in PHASES,
                "Unknown marker",
            )
            markers[marker["mode"]].append((index, marker))
        if "RFDP" in text:
            if "capped" in text:
                cap = re.fullmatch(
                    r"RFDP pid=(\d+) capped file=(\S+) limit=(\d+)", text
                )
                require(cap is not None, "Malformed cap")
                caps.append({
                    "index": index,
                    "pid": cap[1],
                    "file": cap[2],
                    "limit": cap[3],
                })
                continue
            try:
                events[index] = prior.parse(text, index)
            except ValueError:
                malformed.append(index)
    return prior, events, markers, malformed, caps


def producer_gate(episode):
    mode, events = episode["mode"], episode["native_events"]
    provider, outside = (
        episode["fixed_roles"]["provider"],
        episode["fixed_roles"]["outside"],
    )
    tasks = [
        t
        for t in episode["tasks"]
        if t["identity"][2] == provider and t["admission"]["initial"] == "true"
    ]
    require(len(tasks) == 1, (mode, "initial provider task"))
    task = tasks[0]
    require(
        task["bits"] == ("128" if mode == "smil-scope-only" else "32"),
        (mode, "provider task mask"),
    )
    require(
        task["call"]["kind"] == "document-enter"
        and task["call"]["iteration"] == 0
        and task["admission"]["kind"] == "Some(MatchAndCascade)",
        (mode, "provider initial phase"),
    )
    require(
        ("AnimationOnly" in task["admission"]["flags"]) == mode.startswith("smil-"),
        (mode, "provider traversal flags"),
    )
    if mode.startswith("smil-"):
        require(
            task["management"] is not None
            and task["management"]["old_present"] == "false",
            (mode, "provider old primary"),
        )
        maps = [
            e
            for e in events
            if e["event"] == "hint-map"
            and e["target_node"] == episode["fixed_roles"]["host"]
            and e["smil"] == "1"
            and e.get("call_context", {}).get("call") == task["call"]["call"]
            and e["index"] < task["admission"]["index"]
        ]
        require(len(maps) == 1, "same-call SMIL host mapping")
        mapped = maps[0]
        inserted = events[events.index(mapped) + 1]
        require(
            inserted["event"] == "hint-posted"
            and inserted["node"] == mapped["normalized_node"] == mapped["target_node"]
            and "RESTYLE_SMIL" in inserted["hint"]
            and "RESTYLE_SMIL" in inserted["merged"],
            "actual SMIL host insertion",
        )
    require(
        len([
            e
            for e in events
            if e["event"] == "restyle"
            and e.get("role") == "provider"
            and e["initial"] == "true"
        ])
        == 1,
        "provider initialized repeatedly",
    )
    interval = [e for e in events if task["executed"] < e["index"] < task["returned"]]
    lookup_records = [e for e in interval if e["event"] == "timeline-lookup"]
    require(lookup_records, (mode, "no named lookup in provider callback"))
    rebindings = []
    for lookup in lookup_records:
        require(
            lookup["name"] == "--t"
            and lookup["target_node"] == outside
            and lookup["document_node"] == episode["document_node"],
            (mode, "lookup target identity"),
        )
        require(lookup["deferred_updates"] in {"0", "1"}, "deferred mode")
        expected = (
            "equal"
            if lookup["old_timeline"] == lookup["new_timeline"]
            else "defer"
            if lookup["deferred_updates"] == "1"
            and lookup["new_kind"] in {"null", "unresolved"}
            else "rebind"
        )
        require(lookup["decision"] == expected, "lookup decision")
        following = [e for e in interval if e["index"] > lookup["index"]]
        if expected == "defer":
            require(
                following and following[0]["event"] == "timeline-deferred",
                "missing deferred insertion",
            )
            continue
        if expected != "rebind":
            continue
        require(
            following and following[0]["event"] == "timeline-rebind-enter",
            "missing rebind entry",
        )
        entered = following[0]
        returns = [
            e
            for e in following
            if e["event"] == "timeline-rebind-return"
            and e["animation"] == lookup["animation"]
        ]
        require(len(returns) == 1, "missing or ambiguous rebind return")
        returned = returns[0]
        for event in (entered, returned):
            require(
                all(
                    event[key] == lookup[key]
                    for key in (
                        "animation",
                        "target_node",
                        "document_node",
                        "name",
                        "old_timeline",
                        "new_timeline",
                    )
                ),
                "rebind identity",
            )
        require(returned["changed"] in {"0", "1"}, "rebind result")
        if returned["changed"] == "1":
            require(
                returned["current_timeline"] == lookup["new_timeline"],
                "rebind current timeline",
            )
        eligible = [
            e
            for e in interval
            if entered["index"] < e["index"] < returned["index"]
            and e["event"] == "timing-eligible"
        ]
        requests = []
        for gate in eligible:
            require(
                gate["animation"] == lookup["animation"]
                and gate["target_node"] == outside
                and gate["document_node"] == episode["document_node"]
                and gate["timing_changed"] == "1"
                and int(gate["properties"]) > 0,
                "timing eligibility identity",
            )
            position = events.index(gate)
            request = events[position + 1]
            if request["event"] != "request":
                continue
            require(
                all(
                    request[field] == gate[field]
                    for field in ("target_node", "pseudo", "pseudo_id", "type")
                )
                and request["level"] == "0",
                "timing request identity",
            )
            require(
                gate["index"] < request["index"] < returned["index"]
                and request["index"] in {r["index"] for r in task["requests"]},
                "request not in rebind callback",
            )
            requests.append({"eligible": gate, "request": request})
        rebindings.append({
            "lookup": lookup,
            "entered": entered,
            "returned": returned,
            "eligible_requests": requests,
        })
    positive = [
        r
        for r in rebindings
        if r["returned"]["changed"] == "1"
        and r["lookup"]["new_kind"] == "scroll"
        and r["eligible_requests"]
    ]
    if mode == "smil-scope-only":
        require(
            all(e["decision"] == "equal" for e in lookup_records)
            and not rebindings
            and not task["requests"],
            "scope-only control changed timeline or requested work",
        )
    return {
        "provider_task": task,
        "lookups": lookup_records,
        "rebindings": rebindings,
        "eligible_cross_target_request_reached": bool(positive),
        "status": "REACHED"
        if positive
        else "CONTROL_EQUAL"
        if mode == "smil-scope-only"
        else "NOT_REACHED",
    }


def delivery_gate(episode):
    events = episode["native_events"]
    producer = episode["producer_gate"]
    eligible = [
        pair
        for rebind in producer["rebindings"]
        for pair in rebind["eligible_requests"]
    ]
    requests = [e for e in events if e["event"] == "request"]
    require(
        {e["index"] for e in requests}
        == {pair["request"]["index"] for pair in eligible},
        "unattributed measured request",
    )
    selected = [e for e in events if e["event"] == "pre-selected"]
    if not requests:
        require(not selected, "selection without measured request")
        require(
            all(
                e["count"] == "0"
                for e in events
                if e["event"] in {"pre-queue", "pre-remaining"}
            ),
            "unaccounted queued work",
        )
        return {"delivered": [], "request_count": 0}
    require(len(requests) == len(selected) == 1, "unsupported cohort multiplicity")
    request, selection = requests[0], selected[0]
    fields = ("compositor", "target_node", "pseudo", "pseudo_id", "level")
    identity = tuple(request[f] for f in fields)
    require(
        tuple(selection[f] for f in fields) == identity
        and request["type"] == "1"
        and request["posted_before"] == "0"
        and selection["posted"] == "1",
        "selected request key/type",
    )
    position = events.index(request)
    post, deferred = events[position + 1 : position + 3]
    require(
        post["event"] == "request-post"
        and post["skip"] == "0"
        and tuple(post[f] for f in fields) == identity,
        "request posting",
    )
    require(
        deferred["event"] == "post-deferred"
        and deferred["pretraverse"] == "0"
        and deferred["normalized_node"] == request["target_node"]
        and tuple(deferred[f] for f in fields) == identity,
        "actual deferred request",
    )
    position = events.index(selection)
    mapped, inserted, composed, removed = events[position + 1 : position + 5]
    require(
        [e["event"] for e in (mapped, inserted, composed, removed)]
        == ["hint-map", "hint-posted", "will-compose", "select-remove"],
        "selection delivery sequence",
    )
    require(
        all(mapped[f] == request[f] for f in ("target_node", "pseudo", "pseudo_id"))
        and (mapped["animation"], mapped["transition"], mapped["smil"])
        == ("1", "0", "0"),
        "mapped full key",
    )
    require(
        mapped["normalized_node"] == inserted["node"] == request["target_node"]
        and "RESTYLE_CSS_ANIMATIONS" in inserted["hint"]
        and "RESTYLE_CSS_ANIMATIONS" in inserted["merged"],
        "actual hint insertion",
    )
    require(
        tuple(composed[f] for f in fields)
        == tuple(removed[f] for f in fields)
        == identity
        and composed["effect"] == eligible[0]["eligible"]["effect"],
        "effect/removal identity",
    )
    drains = [e for e in events if e["event"] == "drain-selected"]
    require(len(drains) == 1 and drains[0]["iteration"] == "1", "delivery drain")
    task = producer["provider_task"]
    require(
        drains[0]["set"] == task["call"]["set"]
        and drains[0]["call"] == task["call"]["call"],
        "delivery call",
    )
    admissions = [
        e
        for e in events
        if e["event"] == "restyle"
        and e["node"] == request["target_node"]
        and inserted["index"] < e["index"]
        and "RESTYLE_CSS_ANIMATIONS" in e["hint"]
        and "AnimationOnly" in e["flags"]
    ]
    require(len(admissions) == 1, "outside animation admission")
    admission = admissions[0]
    installations = [
        e
        for e in events
        if e["event"] == "installed"
        and e["node"] == request["target_node"]
        and e["index"] > admission["index"]
        and e["flags"] == admission["flags"]
    ]
    require(len(installations) == 1, "outside style installation")
    installed = installations[0]
    for event in (selection, admission, installed):
        ctx = event["call_context"]
        require(
            ctx["kind"] == "document-enter"
            and ctx["set"] == task["call"]["set"]
            and ctx["call"] == task["call"]["call"]
            and ctx["document_node"] == episode["document_node"],
            "cohort call attribution",
        )
    require(
        admission["thread"] == installed["thread"]
        and admission["call_context"] == installed["call_context"]
        and admission["call_context"]["iteration"] == 1
        and admission["initial"] == installed["initial"] == "false",
        "outside installation phase",
    )
    require(
        request["index"]
        < selection["index"]
        < inserted["index"]
        < drains[0]["index"]
        < admission["index"]
        < installed["index"]
        < episode["end"],
        "delivery ordering",
    )
    for event in events:
        if event["event"] in {"pre-queue", "pre-remaining"}:
            expected = int(
                event["level"] == "0"
                and request["index"] < event["index"] < removed["index"]
            )
            require(
                event["compositor"] == request["compositor"]
                and int(event["count"]) == expected,
                "queue accounting",
            )
    return {
        "request_count": 1,
        "delivered": [
            {
                "key": identity,
                "request": request["index"],
                "selected": selection["index"],
                "inserted": inserted["index"],
                "removed": removed["index"],
                "drain": drains[0]["index"],
                "admitted": admission["index"],
                "installed": installed["index"],
                "font_px": installed["font_px"],
                "call": task["call"]["call"],
                "iteration": 1,
            }
        ],
    }


def pretraverse_integrity(events):
    active = None
    for event in events:
        kind = event["event"]
        if kind == "pre-enter":
            require(active is None, "nested pretraverse")
            active = {
                "compositor": event["compositor"],
                "call": event["call_context"],
                "queue": [],
                "remaining": [],
                "selections": 0,
            }
        elif kind in {"pre-queue", "pre-remaining", "pre-selected", "pre-exit"}:
            require(
                active is not None
                and event["compositor"] == active["compositor"]
                and event["call_context"] == active["call"],
                "pretraverse attribution",
            )
            if kind in {"pre-queue", "pre-remaining"}:
                active["queue" if kind == "pre-queue" else "remaining"].append(
                    event["level"]
                )
            elif kind == "pre-selected":
                active["selections"] += 1
            else:
                require(
                    active["queue"] == active["remaining"] == ["0", "1"]
                    and event["found"] == str(int(active["selections"] > 0)),
                    "pretraverse exit accounting",
                )
                active = None
    require(active is None, "unfinished pretraverse")


def analyze(rows):
    tests = [r for r in rows if r["action"] == "test_status"]
    endings = [r for r in rows if r["action"] == "test_end"]
    require(
        len(tests) == 3
        and {t["subtest"] for t in tests}
        == {"Named timeline admission: " + mode for mode in MODES}
        and all(t["status"] == "PASS" for t in tests),
        "WPT callbacks",
    )
    require(len(endings) == 1 and endings[0]["status"] == "OK", "WPT harness")
    prior, parsed, markers, malformed, caps = parse_trace(rows)
    episodes = []
    for mode in MODES:
        marks = markers[mode]
        require([m["phase"] for _, m in marks] == list(PHASES), (mode, "marker order"))
        start, end = marks[0][0], marks[3][0]
        require(
            not any(start < index < end for index in malformed),
            (mode, "malformed measured record"),
        )
        events = [dict(event) for index, event in parsed.items() if start < index < end]
        documents = {
            (e["pid"], e["document_node"])
            for e in events
            if e.get("role") == "provider"
        }
        require(len(documents) == 1, (mode, "nonunique provider document"))
        pid, document = next(iter(documents))
        require(
            not any(c["pid"] == pid and c["index"] < end for c in caps),
            (mode, "tested process capped"),
        )
        excluded = sum(e["pid"] != pid for e in events)
        events = [e for e in events if e["pid"] == pid]
        classified = prior.classify(events)
        roles = collections.defaultdict(set)
        for index, event in parsed.items():
            if index >= end:
                break
            if (
                event["pid"] == pid
                and event.get("document_node") == document
                and event.get("role")
                in {"host", "provider", "outside", "fallback", "svg"}
            ):
                roles[event["role"]].add(event["node"])
        require(
            {"provider", "outside", "fallback", "host"} <= roles.keys()
            and all(len(nodes) == 1 for nodes in roles.values()),
            (mode, "role attribution"),
        )
        classified.update(
            mode=mode,
            start=start,
            end=end,
            pid=pid,
            document_node=document,
            markers=marks,
            fixed_roles={name: next(iter(nodes)) for name, nodes in roles.items()},
            excluded_process_events=excluded,
            native_events=events,
        )
        classified["producer_gate"] = producer_gate(classified)
        pretraverse_integrity(events)
        classified["delivery"] = delivery_gate(classified)
        observation = marks[-1][1]["observation"]
        before, after = observation["before"], observation["after"]
        require(
            observation["mode"] == mode
            and observation["phase"] == "complete"
            and observation["sameAnimation"] is True
            and observation["hostDisplay"] == "inline"
            and observation["fallbackScrollTop"] == 100,
            "fixture identity/state",
        )
        require(
            before["timelineSource"] == "fallback"
            and before["playState"] == "running"
            and before["pending"] is False
            and before["timing"]["progress"] is not None
            and abs(before["timing"]["progress"] - 0.5) <= 0.001
            and abs(float(before["font"].removesuffix("px")) - 20) <= 0.01,
            "active fallback calibration",
        )
        require(marks[3][1]["value"] == observation["firstFont"], "first getter marker")
        require(
            after["timelineSource"]
            == ("fallback" if mode == "smil-scope-only" else "provider"),
            "final timeline source",
        )
        require(
            observation["paused"] == (True if mode.startswith("smil-") else None)
            and observation["time"] == (75 if mode.startswith("smil-") else None),
            "SMIL timing",
        )
        if mode == "smil-scope-only":
            require(
                observation["firstFont"] == before["font"], "scope-only font changed"
            )
        for cohort in classified["delivery"]["delivered"]:
            require(
                float(cohort["font_px"])
                == float(observation["firstFont"].removesuffix("px")),
                "installed/getter font mismatch",
            )
        episodes.append(classified)
    require(
        all(a["markers"][-1][0] < b["start"] for a, b in zip(episodes, episodes[1:])),
        "overlapping modes",
    )
    verified = all(
        e["producer_gate"]["status"]
        == ("CONTROL_EQUAL" if e["mode"] == "smil-scope-only" else "REACHED")
        and len(e["delivery"]["delivered"])
        == (0 if e["mode"] == "smil-scope-only" else 1)
        for e in episodes
    )
    return {
        "episodes": episodes,
        "malformed": malformed,
        "caps": caps,
        "gate_verified": verified,
        "recurrence_claim": False,
        "native_to_lean_refinement": False,
    }


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    require(len(sys.argv) == 2, "Usage: python3 -I analyze.py runtime-directory")
    runtime = Path(sys.argv[1]).resolve()
    terminal = json.loads((runtime / "RESULT.json").read_text())
    require(
        terminal["error"] is None and terminal["restoration_verified"] is True,
        "Native transaction not restored",
    )
    command = terminal["commands"]["wpt"]["command"]
    require(
        terminal["commands"]["wpt"]["exit_code"] == 0
        and all(
            pref in command
            for pref in (
                "--setpref=dom.window.dump.enabled=true",
                "--setpref=layout.css.display-animations.enabled=false",
                "--setpref=layout.css.scroll-driven-animations.enabled=true",
            )
        ),
        "required runtime configuration",
    )
    raw = runtime / "wpt-raw.jsonl"
    result = analyze([json.loads(line) for line in raw.read_text().splitlines()])
    result["raw_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    result["analyzer_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE / "ANALYSIS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps({
            "episodes": len(result["episodes"]),
            "gate_verified": result["gate_verified"],
        })
    )


if __name__ == "__main__":
    main()
