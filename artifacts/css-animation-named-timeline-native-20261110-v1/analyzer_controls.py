import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("named_analyzer", here / "analyze.py")
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    raw = Path(sys.argv[1]) / "wpt-raw.jsonl"
    rows = [json.loads(line) for line in raw.read_text().splitlines()]
    baseline = module.analyze(rows)
    module.require(baseline["gate_verified"], "baseline gate not established")
    first = baseline["episodes"][0]
    gate = first["producer_gate"]
    task, rebind = gate["provider_task"], gate["rebindings"][0]
    eligible = rebind["eligible_requests"][0]
    delivered = first["delivery"]["delivered"][0]
    events = first["native_events"]
    root = next(e["index"] for e in events if e["event"] == "document-root")
    host_map = next(
        e["index"] for e in events if e["event"] == "hint-map" and e["smil"] == "1"
    )
    composed = next(e["index"] for e in events if e["event"] == "will-compose")
    scope_lookup = baseline["episodes"][2]["producer_gate"]["lookups"][0]["index"]
    controls = []

    def reject(name, expected, mutate):
        altered = copy.deepcopy(rows)
        mutate(altered)
        try:
            result = module.analyze(altered)
            module.require(result["gate_verified"], "positive gate not established")
        except ValueError as error:
            detail = error.args[0]
            reason = detail[-1] if isinstance(detail, tuple) else detail
            if reason != expected:
                raise RuntimeError(f"Unexpected {name} rejection: {error}") from error
            controls.append({"name": name, "rejected": True, "reason": str(error)})
        else:
            raise RuntimeError("Accepted negative control: " + name)

    def change(index, field, value):
        def mutate(altered):
            pattern = (
                r"pid=\d+(?=\s)"
                if field == "pid"
                else r"(?<!\w)" + field + r"=.*?(?= \w+=|$)"
            )
            text, count = re.subn(pattern, field + "=" + value, altered[index]["data"])
            if count != 1:
                raise RuntimeError("Mutation field not unique")
            altered[index]["data"] = text

        return mutate

    cases = [
        (
            "wrong-document",
            task["installed"],
            "document_node",
            "0xdead",
            "nonunique provider document",
        ),
        ("wrong-call", root, "call", "999999", "wrong call"),
        ("wrong-iteration", root, "iteration", "1", "nonconsecutive iteration"),
        (
            "wrong-provider-mask",
            task["queued"],
            "bits",
            "128",
            "ambiguous/missing queued task",
        ),
        (
            "wrong-task-return-thread",
            task["returned"],
            "thread",
            "ThreadId(999)",
            "task return attribution",
        ),
        (
            "old-primary-present",
            task["management"]["index"],
            "old_present",
            "true",
            "old style mismatch",
        ),
        ("missing-smil-map", host_map, "smil", "0", "same-call SMIL host mapping"),
        (
            "wrong-lookup-document",
            rebind["lookup"]["index"],
            "document_node",
            "0xdead",
            "lookup target identity",
        ),
        (
            "wrong-lookup-name",
            rebind["lookup"]["index"],
            "name",
            "--other",
            "lookup target identity",
        ),
        (
            "wrong-old-timeline",
            rebind["lookup"]["index"],
            "old_timeline",
            "0xdead",
            "rebind identity",
        ),
        (
            "wrong-new-timeline",
            rebind["lookup"]["index"],
            "new_timeline",
            "0xdead",
            "rebind identity",
        ),
        (
            "unresolved-not-concrete",
            rebind["lookup"]["index"],
            "new_kind",
            "unresolved",
            "lookup decision",
        ),
        (
            "wrong-rebind-process",
            rebind["entered"]["index"],
            "pid",
            "999999",
            "missing rebind entry",
        ),
        (
            "rebind-did-not-change",
            rebind["returned"]["index"],
            "changed",
            "0",
            "positive gate not established",
        ),
        (
            "wrong-current-timeline",
            rebind["returned"]["index"],
            "current_timeline",
            "0xdead",
            "rebind current timeline",
        ),
        (
            "empty-properties",
            eligible["eligible"]["index"],
            "properties",
            "0",
            "timing eligibility identity",
        ),
        (
            "wrong-eligible-animation",
            eligible["eligible"]["index"],
            "animation",
            "0xdead",
            "timing eligibility identity",
        ),
        (
            "wrong-eligible-pseudo",
            eligible["eligible"]["index"],
            "pseudo",
            "94",
            "timing request identity",
        ),
        (
            "wrong-eligible-type",
            eligible["eligible"]["index"],
            "type",
            "0",
            "timing request identity",
        ),
        (
            "wrong-request-target",
            eligible["request"]["index"],
            "target_node",
            task["identity"][2],
            "timing request identity",
        ),
        (
            "wrong-request-level",
            eligible["request"]["index"],
            "level",
            "1",
            "timing request identity",
        ),
        (
            "wrong-selection-pseudo",
            delivered["selected"],
            "pseudo",
            "94",
            "selected request key/type",
        ),
        (
            "wrong-composed-effect",
            composed,
            "effect",
            "0xdead",
            "effect/removal identity",
        ),
        (
            "wrong-installer-thread",
            delivered["installed"],
            "thread",
            "ThreadId(999)",
            "restyle attribution",
        ),
        (
            "wrong-installed-font",
            delivered["installed"],
            "font_px",
            "99",
            "installed/getter font mismatch",
        ),
        ("scope-not-equal", scope_lookup, "decision", "rebind", "lookup decision"),
    ]
    for name, index, field, value, expected in cases:
        reject(name, expected, change(index, field, value))
    for name, index, reason in [
        ("missing-queue", task["queued"], "ambiguous/missing queued task"),
        (
            "missing-rebind-return",
            rebind["returned"]["index"],
            "missing or ambiguous rebind return",
        ),
        (
            "missing-request",
            eligible["request"]["index"],
            "selection without measured request",
        ),
        ("missing-installation", delivered["installed"], "outside style installation"),
    ]:
        reject(name, reason, lambda altered, i=index: altered.pop(i))

    def duplicate(altered):
        index = eligible["request"]["index"]
        altered.insert(index + 1, copy.deepcopy(altered[index]))

    reject("unaccounted-new-request", "unattributed measured request", duplicate)

    def malformed(altered):
        altered[task["installed"]]["data"] += " RFDP broken"

    reject("malformed-measured-record", "malformed measured record", malformed)

    def cap(altered):
        altered.insert(
            first["start"] + 1,
            {
                "action": "process_output",
                "data": f"RFDP pid={first['pid']} capped file=test.rs limit=4096",
            },
        )

    reject("tested-process-cap", "tested process capped", cap)
    result = {
        "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "analyzer_sha256": hashlib.sha256(
            (here / "analyze.py").read_bytes()
        ).hexdigest(),
        "prior_analyzer_sha256": module.PRIOR_HASH,
        "controls": controls,
    }
    (here / "ANALYZER-CONTROLS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"negative_controls_rejected": len(controls)}))


if __name__ == "__main__":
    main()
