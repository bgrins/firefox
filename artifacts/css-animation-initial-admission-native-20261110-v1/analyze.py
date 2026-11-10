import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODES = ("smil-animated", "normal-animated", "smil-literal")
PHASES = (
    "stimulus-begin",
    "stimulus-return",
    "getter-begin",
    "getter-return",
    "complete",
)
ROLES = {"host", "first", "second", "third", "leaf", "svg", "-"}
DESCENDANTS = {"first", "second", "third", "leaf"}
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
    "hint-map": "target_node normalized_node pseudo pseudo_id animation transition smil",
    "hint-posted": "node hint merged",
    "hint-discard": "node hint reason",
    "restyle": "node document_node role flags hint kind admitted_animation initial thread",
    "installed": "node document_node role style flags initial font_px thread",
    "animation-management": "node document_node role flags old_present thread",
    "task-queued": "node document_node role flags old_present bits thread",
    "task-execute": "node document_node role bits thread",
    "task-return": "node document_node role bits thread",
    "document-enter": "set document document_node call flags",
    "document-root": "set call iteration root_node flags",
    "document-exit": "set call iteration post",
    "document-no-root": "set call",
    "drain-selected": "set call iteration",
    "new-subtree-enter": "set document_node call root_node",
    "new-subtree-pass": "set document_node call root_node phase flags",
    "new-subtree-exit": "set document_node call root_node",
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def parse(text, index):
    match = re.fullmatch(r"RFDP pid=(\d+) ([\w-]+) (.*)", text)
    require(match is not None and text.count("RFDP") == 1, (index, "malformed"))
    pid, event, payload = match.groups()
    require(event in SCHEMAS, (index, "unknown or capped", event))
    fields = re.findall(r"(\w+)=(.*?)(?= \w+=|$)", payload)
    require(" ".join(k for k, _ in fields) == SCHEMAS[event], (index, "schema"))
    require(" ".join(k + "=" + v for k, v in fields) == payload, (index, "fields"))
    result = dict(fields, pid=pid, event=event, index=index)
    if "role" in result:
        require(result["role"] in ROLES, (index, "role"))
    for name in ("initial", "old_present", "admitted_animation"):
        if name in result:
            require(result[name] in {"true", "false"}, (index, name))
    for name in ("bits", "iteration", "call"):
        if name in result:
            require(result[name].isdigit(), (index, name))
    return result


def identity(event):
    return event["pid"], event["document_node"], event["node"]


def context(frame):
    return {
        key: frame[key]
        for key in ("kind", "set", "call", "document_node", "phase", "iteration")
    }


def classify(events):
    stacks = collections.defaultdict(list)
    admissions = {}
    tasks = []
    executions = {}
    role_nodes = {}
    node_roles = {}
    calls = []
    for event in events:
        pid, kind = event["pid"], event["event"]
        stack = stacks[pid]
        if stack:
            event["call_context"] = context(stack[-1])
        if kind in {"document-enter", "new-subtree-enter"}:
            frame = dict(event, kind=kind, phase="pretraverse", iteration=None)
            stack.append(frame)
            calls.append({**context(frame), "pid": pid, "enter": event["index"]})
        elif kind in {"document-root", "drain-selected", "new-subtree-pass"}:
            require(stack, (event["index"], "missing active call"))
            frame = stack[-1]
            require(
                (frame["set"], frame["call"]) == (event["set"], event["call"]),
                (event["index"], "wrong call"),
            )
            if kind == "new-subtree-pass":
                require(frame["kind"] == "new-subtree-enter", "wrong subtree call")
                require(
                    frame["document_node"] == event["document_node"]
                    and frame["root_node"] == event["root_node"],
                    "wrong subtree identity",
                )
                require(event["phase"] in {"default", "final"}, "wrong subtree phase")
                frame["phase"] = event["phase"]
            else:
                require(frame["kind"] == "document-enter", "wrong document call")
                iteration = int(event["iteration"])
                previous = frame["iteration"]
                require(
                    iteration
                    == (
                        0 if previous is None else previous + (kind == "drain-selected")
                    ),
                    "nonconsecutive iteration",
                )
                frame["iteration"] = iteration
                frame["phase"] = "traversal" if kind == "document-root" else "selected"
        elif kind in {"document-exit", "document-no-root", "new-subtree-exit"}:
            require(stack, (event["index"], "unmatched exit"))
            frame = stack[-1]
            require(
                (frame["set"], frame["call"]) == (event["set"], event["call"]),
                "wrong exit call",
            )
            if kind == "new-subtree-exit":
                require(
                    frame["kind"] == "new-subtree-enter"
                    and frame["document_node"] == event["document_node"]
                    and frame["root_node"] == event["root_node"],
                    "wrong subtree exit",
                )
            else:
                require(frame["kind"] == "document-enter", "wrong document exit")
                require(
                    (kind == "document-no-root") == (frame["iteration"] is None),
                    "root/exit mismatch",
                )
                if kind == "document-exit":
                    require(
                        int(event["iteration"]) == frame["iteration"], "exit iteration"
                    )
            require(pid not in executions, "callback did not return before call exit")
            require(
                not any(
                    t["pid"] == pid
                    and t["call"] == context(frame)
                    and "returned" not in t
                    for t in tasks
                ),
                "queued task did not complete before call exit",
            )
            stack.pop()
        elif kind in {
            "restyle",
            "installed",
            "animation-management",
            "task-queued",
            "task-execute",
            "task-return",
        }:
            require(stack, (event["index"], "unattributed native event"))
            frame = stack[-1]
            require(
                frame["document_node"] == event["document_node"],
                (event["index"], "wrong document"),
            )
            require(
                frame["phase"] in {"traversal", "default", "final"},
                "native event without traversal marker",
            )
            event["call_context"] = context(frame)
            token = identity(event)
            if event["role"] != "-":
                role = pid, event["document_node"], event["role"]
                require(
                    role_nodes.setdefault(role, event["node"]) == event["node"],
                    "nonunique role",
                )
                require(
                    node_roles.setdefault(token, event["role"]) == event["role"],
                    "node role changed",
                )
            if kind == "restyle":
                admissions[token] = {"restyle": event}
            elif kind in {"animation-management", "task-queued", "installed"}:
                require(token in admissions, "missing restyle admission")
                admission = admissions[token]
                selected = admission["restyle"]
                require(
                    selected["call_context"] == event["call_context"]
                    and selected["thread"] == event["thread"]
                    and selected["role"] == event["role"],
                    "restyle attribution",
                )
                require(selected["flags"] == event["flags"], "restyle flags")
                if kind == "animation-management":
                    require(
                        "AnimationOnly" in event["flags"],
                        "management outside animation prepass",
                    )
                    require(
                        (selected["initial"] == "true")
                        == (event["old_present"] == "false"),
                        "old style mismatch",
                    )
                    require("management" not in admission, "duplicate management entry")
                    admission["management"] = event
                elif kind == "task-queued":
                    require(int(event["bits"]) > 0, "empty task")
                    require(
                        (selected["initial"] == "true")
                        == (event["old_present"] == "false"),
                        "queue old style mismatch",
                    )
                    if "AnimationOnly" in event["flags"]:
                        require(
                            "management" in admission
                            and event["old_present"] == "false",
                            "queue lacks initial management entry",
                        )
                    tasks.append({
                        "pid": pid,
                        "identity": token,
                        "role": event["role"],
                        "bits": event["bits"],
                        "call": context(frame),
                        "queued": event["index"],
                        "admission": selected,
                        "management": admission.get("management"),
                    })
                else:
                    require(
                        selected["initial"] == event["initial"],
                        "installed initial mismatch",
                    )
                    require("installed" not in admission, "duplicate installation")
                    admission["installed"] = event
                    for task in tasks:
                        if task["admission"] is selected:
                            task["installed"] = event["index"]
            elif kind == "task-execute":
                require(pid not in executions, "nested callback needs separate account")
                candidates = [
                    t
                    for t in tasks
                    if t["identity"] == token
                    and t["bits"] == event["bits"]
                    and "executed" not in t
                ]
                require(
                    len(candidates) == 1,
                    (event["index"], "ambiguous/missing queued task"),
                )
                task = candidates[0]
                require(
                    task["call"] == context(frame)
                    and task["role"] == event["role"]
                    and "installed" in task,
                    "task execution attribution",
                )
                task.update(
                    executed=event["index"],
                    execution_thread=event["thread"],
                    requests=[],
                )
                executions[pid] = task
            else:
                require(pid in executions, "return without execution")
                task = executions.pop(pid)
                require(
                    task["identity"] == token
                    and task["bits"] == event["bits"]
                    and task["role"] == event["role"]
                    and task["execution_thread"] == event["thread"]
                    and task["call"] == context(frame),
                    "task return attribution",
                )
                task["returned"] = event["index"]
        elif kind == "request" and pid in executions:
            task = executions[pid]
            task["requests"].append({
                **event,
                "same_target": event["target_node"] == task["identity"][2],
            })
    require(not any(stacks.values()) and not executions, "unfinished native call")
    require(all("returned" in task for task in tasks), "unfinished queued task")
    return {
        "calls": calls,
        "tasks": tasks,
        "roles": [
            {"pid": k[0], "document_node": k[1], "role": k[2], "node": v}
            for k, v in role_nodes.items()
        ],
    }


def delivery_ledger(events, tasks, document):
    def key(event):
        return tuple(
            event[field]
            for field in ("compositor", "target_node", "pseudo", "pseudo_id", "level")
        )

    def call(event):
        ctx = event.get("call_context")
        require(
            ctx is not None
            and ctx["kind"] == "document-enter"
            and ctx["document_node"] == document,
            "delivery outside tested StyleDocument",
        )
        return ctx["set"], ctx["call"], ctx["document_node"]

    queue = {}
    posted = {}
    in_flight = []
    deliveries = []
    admissions = {}
    pre = None
    drains = []
    selected_since_drain = []
    requests = {r["index"]: t for t in tasks for r in t["requests"]}
    request_details = set()
    selection_details = set()
    compositors = {e["compositor"] for e in events if "compositor" in e}
    require(len(compositors) == 1, "nonunique episode compositor")
    for pos, event in enumerate(events):
        kind = event["event"]
        if kind == "pre-enter":
            require(pre is None, "nested pretraverse")
            pre = {
                "call": call(event),
                "compositor": event["compositor"],
                "selected": 0,
                "queue": [],
                "remaining": [],
            }
        elif kind in {"pre-queue", "pre-remaining"}:
            require(
                pre is not None and pre["compositor"] == event["compositor"],
                "queue outside pretraverse",
            )
            require(
                int(event["count"])
                == sum(
                    identity[0] == event["compositor"] and identity[4] == event["level"]
                    for identity in queue
                ),
                "queue population mismatch",
            )
            pre["queue" if kind == "pre-queue" else "remaining"].append(event["level"])
        elif kind == "pre-exit":
            require(
                pre is not None
                and pre["compositor"] == event["compositor"]
                and pre["call"] == call(event),
                "pretraverse exit mismatch",
            )
            require(
                pre["queue"] == pre["remaining"] == ["0", "1"],
                "incomplete queue snapshots",
            )
            require(
                event["found"] == str(int(pre["selected"] > 0)),
                "pretraverse found mismatch",
            )
            pre = None
        elif kind == "request":
            require(event["type"] in {"0", "1", "2"}, "unsupported request type")
            identity = key(event)
            require(event["index"] in requests, "request outside recorded callback")
            task = requests[event["index"]]
            require(
                task["identity"][1] == document
                and task["identity"][2] == event["target_node"],
                "callback target mismatch",
            )
            require(
                call(event) == (task["call"]["set"], task["call"]["call"], document),
                "request call mismatch",
            )
            require(
                event["posted_before"] == str(int(posted.get(identity, False))),
                "posted-before mismatch",
            )
            queue.setdefault(identity, []).append(event["index"])
            if event["type"] != "0":
                post = events[pos + 1]
                request_details.add(post["index"])
                require(
                    post["event"] == "request-post"
                    and key(post) == identity
                    and post["skip"] == event["posted_before"],
                    "request posting mismatch",
                )
                if post["skip"] == "0":
                    deferred = events[pos + 2]
                    request_details.add(deferred["index"])
                    require(
                        deferred["event"] == "post-deferred"
                        and key(deferred) == identity
                        and deferred["normalized_node"] == event["target_node"]
                        and deferred["pretraverse"] == "0",
                        "request deferral mismatch",
                    )
                posted[identity] = True
        elif kind == "pre-selected":
            identity = key(event)
            require(
                pre is not None and pre["compositor"] == event["compositor"],
                "selection outside pretraverse",
            )
            require(
                identity in queue and posted.get(identity) and event["posted"] == "1",
                "unaccounted selected cohort",
            )
            require(
                not any(d["key"] == identity for d in in_flight),
                "overlapping same-key cohort",
            )
            mapped, inserted, composed, removed = events[pos + 1 : pos + 5]
            selection_details.update(
                e["index"] for e in (mapped, inserted, composed, removed)
            )
            require(
                [e["event"] for e in (mapped, inserted, composed, removed)]
                == ["hint-map", "hint-posted", "will-compose", "select-remove"],
                "selection delivery sequence",
            )
            require(
                all(
                    mapped[f] == event[f]
                    for f in ("target_node", "pseudo", "pseudo_id")
                ),
                "hint mapping key",
            )
            require(
                event["level"] == "0"
                and (mapped["animation"], mapped["transition"], mapped["smil"])
                == ("1", "0", "0"),
                "unexpected cascade level/hint",
            )
            require(
                mapped["normalized_node"] == inserted["node"] == event["target_node"],
                "hint mapping target",
            )
            require(
                "RESTYLE_CSS_ANIMATIONS" in inserted["hint"]
                and "RESTYLE_CSS_ANIMATIONS" in inserted["merged"],
                "actual hint insertion missing",
            )
            require(
                key(composed) == key(removed) == identity, "composition/removal key"
            )
            cohort = {
                "key": identity,
                "requests": queue.pop(identity),
                "selected": event["index"],
                "mapped": mapped["index"],
                "inserted": inserted["index"],
                "removed": removed["index"],
                "call": call(event),
                "node": inserted["node"],
            }
            posted.pop(identity)
            in_flight.append(cohort)
            selected_since_drain.append(cohort)
            pre["selected"] += 1
        elif kind == "drain-selected":
            require(
                selected_since_drain and pre is None,
                "drain without completed selection",
            )
            for cohort in selected_since_drain:
                require(
                    cohort["call"] == (event["set"], event["call"], document),
                    "drain selection call",
                )
                cohort["drain_iteration"] = int(event["iteration"])
            drains.append({
                "call": event["call"],
                "iteration": int(event["iteration"]),
                "cohorts": len(selected_since_drain),
            })
            selected_since_drain = []
        elif kind == "restyle":
            admissions[event["node"]] = event
        elif kind == "installed":
            for cohort in list(in_flight):
                if cohort["node"] != event["node"]:
                    continue
                admission = admissions[event["node"]]
                require(
                    cohort["inserted"] < admission["index"] < event["index"],
                    "delivery ordering",
                )
                require(
                    cohort["call"] == call(event) == call(admission), "delivery call"
                )
                require(
                    admission["thread"] == event["thread"]
                    and admission["call_context"] == event["call_context"],
                    "delivery traversal identity",
                )
                require(
                    cohort.get("drain_iteration") == event["call_context"]["iteration"],
                    "delivery drain iteration",
                )
                require(
                    "AnimationOnly" in admission["flags"]
                    and "AnimationOnly" in event["flags"]
                    and "RESTYLE_CSS_ANIMATIONS" in admission["hint"]
                    and admission["kind"] != "None",
                    "delivery admission",
                )
                cohort.update(
                    admitted=admission["index"],
                    installed=event["index"],
                    font_px=event["font_px"],
                )
                deliveries.append(cohort)
                in_flight.remove(cohort)
        elif kind == "hint-discard":
            raise ValueError("hint discard in measured interval")
        elif kind in {"request-post", "post-deferred"}:
            require(event["index"] in request_details, "orphan request side effect")
        elif kind in {"will-compose", "select-remove"}:
            require(event["index"] in selection_details, "orphan selection side effect")
    require(
        not queue
        and not posted
        and not in_flight
        and not selected_since_drain
        and pre is None,
        "undelivered measured work",
    )
    require(
        sum(len(d["requests"]) for d in deliveries) == len(requests),
        "request conservation",
    )
    return {
        "cohorts": deliveries,
        "drains": drains,
        "request_count": len(requests),
        "compositor": next(iter(compositors)),
    }


def analyze(rows):
    tests = [r for r in rows if r["action"] == "test_status"]
    endings = [r for r in rows if r["action"] == "test_end"]
    require(
        len(tests) == 3
        and {r["subtest"] for r in tests}
        == {"Revealed font dependency chain: " + mode for mode in MODES}
        and all(r["status"] == "PASS" for r in tests),
        "WPT callbacks",
    )
    require(len(endings) == 1 and endings[0]["status"] == "OK", "WPT harness")
    markers = collections.defaultdict(list)
    malformed_outside = []
    caps = []
    parsed = {}
    for index, row in enumerate(rows):
        text = row.get("data", "")
        if "IA_PROBE" in text:
            require(
                text.startswith("IA_PROBE ") and text.count("IA_PROBE") == 1,
                "malformed marker",
            )
            marker = json.loads(text[len("IA_PROBE ") :])
            require(
                marker.get("mode") in MODES and marker.get("phase") in PHASES,
                "unknown marker",
            )
            markers[marker["mode"]].append((index, marker))
        if "RFDP" in text:
            if "capped" in text:
                cap = re.fullmatch(
                    r"RFDP pid=(\d+) capped file=(\S+) limit=(\d+)", text
                )
                require(cap is not None, (index, "malformed cap"))
                caps.append({
                    "index": index,
                    "pid": cap[1],
                    "file": cap[2],
                    "limit": cap[3],
                })
                continue
            try:
                parsed[index] = parse(text, index)
            except ValueError:
                malformed_outside.append(index)
    episodes = []
    for mode in MODES:
        marks = markers[mode]
        require([m["phase"] for _, m in marks] == list(PHASES), (mode, "marker order"))
        start, end = marks[0][0], marks[3][0]
        require(
            not any(start < index < end for index in malformed_outside),
            (mode, "malformed measured record"),
        )
        events = [dict(event) for index, event in parsed.items() if start < index < end]
        documents = {
            (e["pid"], e["document_node"])
            for e in events
            if e.get("role") in DESCENDANTS
        }
        require(len(documents) == 1, (mode, "nonunique tested document"))
        pid, document = next(iter(documents))
        require(
            not any(c["pid"] == pid and c["index"] < end for c in caps),
            (mode, "tested process capped"),
        )
        excluded_process_events = sum(e["pid"] != pid for e in events)
        events = [e for e in events if e["pid"] == pid]
        result = classify(events)
        require(len(documents) == 1, (mode, "nonunique tested document"))
        pid, document = next(iter(documents))
        tested_roles = {
            r["role"]: r["node"]
            for r in result["roles"]
            if (r["pid"], r["document_node"]) == (pid, document)
        }
        require(
            DESCENDANTS | {"host"} <= tested_roles.keys(),
            (mode, "missing tested roles"),
        )
        witnesses = [
            t
            for t in result["tasks"]
            if t["identity"][:2] == (pid, document)
            and t["role"] in DESCENDANTS
            and t["admission"]["initial"] == "true"
            and "AnimationOnly" in t["admission"]["flags"]
        ]
        for witness in witnesses:
            require(
                witness["admission"]["kind"] == "Some(MatchAndCascade)"
                and witness["management"] is not None,
                "initial admission kind",
            )
        smil_maps = [
            e
            for e in events
            if e["pid"] == pid
            and e["event"] == "hint-map"
            and e["target_node"] == tested_roles["host"]
            and e["normalized_node"] == tested_roles["host"]
            and e["smil"] == "1"
        ]
        observation = marks[-1][1]["observation"]
        require(
            marks[3][1]["value"]
            == observation["firstLeaf"]
            == observation["repeatLeaf"]
            == "512px",
            "getter value",
        )
        require(
            observation["hostDisplay"] == "inline"
            and observation["mode"] == mode
            and observation["phase"] == "complete"
            and observation["cssAnimationsPaused"] is True,
            "observation identity/state",
        )
        require(
            observation["animationTargets"]
            == (sorted(DESCENDANTS) if mode.endswith("-animated") else []),
            "animation roster",
        )
        require(
            observation["paused"] == (True if mode.startswith("smil-") else None)
            and observation["time"] == (75 if mode.startswith("smil-") else None),
            "SMIL timing",
        )
        require(bool(smil_maps) == mode.startswith("smil-"), "SMIL host mapping")
        for mapped in smil_maps:
            index = events.index(mapped)
            inserted = events[index + 1]
            require(
                inserted["event"] == "hint-posted"
                and inserted["node"] == tested_roles["host"]
                and "RESTYLE_SMIL" in inserted["hint"]
                and "RESTYLE_SMIL" in inserted["merged"],
                "SMIL host insertion",
            )
            host_admissions = [
                e
                for e in events[index + 2 :]
                if e["event"] == "restyle"
                and e.get("role") == "host"
                and e["call_context"]["call"] == mapped["call_context"]["call"]
            ]
            require(
                host_admissions
                and "RESTYLE_SMIL" in host_admissions[0]["hint"]
                and "AnimationOnly" in host_admissions[0]["flags"],
                "SMIL host admission",
            )
        initial = [
            e
            for e in events
            if e["event"] == "restyle"
            and e.get("role") in DESCENDANTS
            and e["initial"] == "true"
        ]
        require(
            {e["role"] for e in initial} == DESCENDANTS and len(initial) == 4,
            "initial descendant roster",
        )
        for admission in initial:
            require(
                admission["kind"] == "Some(MatchAndCascade)"
                and admission["call_context"]["kind"] == "document-enter"
                and admission["call_context"]["iteration"] == 0,
                "initial phase",
            )
            require(
                ("AnimationOnly" in admission["flags"]) == mode.startswith("smil-"),
                "initial animation/ordinary control",
            )
            if mode.startswith("smil-"):
                require(
                    any(
                        mapped["index"] < admission["index"]
                        and mapped["call_context"]["call"]
                        == admission["call_context"]["call"]
                        and mapped["call_context"]["set"]
                        == admission["call_context"]["set"]
                        for mapped in smil_maps
                    ),
                    "initial admission lacks same-call SMIL host mapping",
                )
        require(
            len(witnesses) == (4 if mode == "smil-animated" else 0),
            "initial task witness count",
        )
        ledger = delivery_ledger(events, result["tasks"], document)
        require(
            len(ledger["cohorts"]) == (10 if mode.endswith("-animated") else 0),
            "delivery cohort count",
        )
        require(
            [d["cohorts"] for d in ledger["drains"]]
            == ([4, 3, 2, 1] if mode.endswith("-animated") else []),
            "drain cohort shape",
        )
        result.update(
            mode=mode,
            excluded_process_events=excluded_process_events,
            start=start,
            end=end,
            pid=pid,
            document_node=document,
            markers=marks,
            initial_animation_only_tasks=witnesses,
            host_smil_maps=smil_maps,
            initial_admissions=initial,
            delivery=ledger,
        )
        episodes.append(result)
    require(
        all(a["markers"][-1][0] < b["start"] for a, b in zip(episodes, episodes[1:])),
        "overlapping modes",
    )
    return {
        "episodes": episodes,
        "malformed_outside_primary_intervals": malformed_outside,
        "caps": caps,
        "delivery_verified": True,
        "recurrence_claim": False,
        "native_to_lean_refinement": False,
    }


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    require(len(sys.argv) == 2, "Usage: python3 -I analyze.py runtime-directory")
    runtime = Path(sys.argv[1]).resolve()
    terminal = json.loads((runtime / "RESULT.json").read_text())
    restored = json.loads((runtime / "RESTORED.json").read_text())
    require(
        terminal["error"] is None
        and terminal["restoration_verified"] is True
        and restored["source_and_application_restored"] is True,
        "native transaction not successfully restored",
    )
    wpt = terminal["commands"]["wpt"]
    require(
        wpt["exit_code"] == 0
        and "--setpref=dom.window.dump.enabled=true" in wpt["command"]
        and "--setpref=layout.css.display-animations.enabled=false" in wpt["command"],
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
            "delivery_verified": result["delivery_verified"],
        })
    )


if __name__ == "__main__":
    main()
