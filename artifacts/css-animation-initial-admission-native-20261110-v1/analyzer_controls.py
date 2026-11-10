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
    spec = importlib.util.spec_from_file_location(
        "admission_analyzer", here / "analyze.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    raw = Path(sys.argv[1]) / "wpt-raw.jsonl"
    rows = [json.loads(line) for line in raw.read_text().splitlines()]
    result = module.analyze(rows)
    first = result["episodes"][0]
    task = first["initial_animation_only_tasks"][0]
    cohort = first["delivery"]["cohorts"][0]
    begin = first["markers"][2][0]
    root = next(
        i
        for i in range(begin, first["end"])
        if " document-root " in rows[i].get("data", "")
    )
    smil = next(m["index"] for m in first["host_smil_maps"] if m["index"] > begin)
    controls = []
    expected_reasons = {
        "wrong-document": "nonunique tested document",
        "wrong-call": "wrong call",
        "wrong-iteration": "nonconsecutive iteration",
        "wrong-installer-thread": "restyle attribution",
        "wrong-return-thread": "task return attribution",
        "wrong-return-mask": "task return attribution",
        "missing-queue": "ambiguous/missing queued task",
        "missing-return": "nested callback needs separate account",
        "missing-initial-install": "task execution attribution",
        "old-style-present": "old style mismatch",
        "missing-same-call-smil-map": "initial admission lacks same-call SMIL host mapping",
        "wrong-pseudo-map": "hint mapping key",
        "wrong-map-process": "selection delivery sequence",
        "wrong-hint-insertion": "actual hint insertion missing",
        "missing-css-install": "undelivered measured work",
        "wrong-css-install-thread": "restyle attribution",
        "missing-newer-generation-request": "orphan request side effect",
        "missing-coalesced-request": "orphan request side effect",
        "wrong-request-target": "callback target mismatch",
        "malformed-measured-record": "malformed measured record",
        "tested-process-cap": "tested process capped",
        "wrong-getter-value": "getter value",
    }

    def reject(name, mutation):
        altered = copy.deepcopy(rows)
        mutation(altered)
        try:
            module.analyze(altered)
        except ValueError as error:
            detail = error.args[0]
            reason = detail[-1] if isinstance(detail, tuple) else detail
            if reason != expected_reasons[name]:
                raise RuntimeError(
                    f"Unexpected rejection for {name}: {error}"
                ) from error
            controls.append({"name": name, "rejected": True, "reason": str(error)})
        else:
            raise RuntimeError("Accepted negative control: " + name)

    def replace(index, field, value):
        def mutation(altered):
            pattern = (
                r"pid=\d+"
                if field == "pid"
                else r"(?<!\w)" + field + r"=.*?(?= \w+=|$)"
            )
            text, count = re.subn(
                pattern,
                field + "=" + value,
                altered[index]["data"],
            )
            if count != 1:
                raise RuntimeError("Control field is not unique")
            altered[index]["data"] = text

        return mutation

    def remove(index):
        return lambda altered: altered.pop(index)

    reject("wrong-document", replace(task["installed"], "document_node", "0xdead"))
    reject("wrong-call", replace(root, "call", "999999"))
    reject("wrong-iteration", replace(root, "iteration", "1"))
    reject(
        "wrong-installer-thread", replace(task["installed"], "thread", "ThreadId(999)")
    )
    reject("wrong-return-thread", replace(task["returned"], "thread", "ThreadId(999)"))
    reject("wrong-return-mask", replace(task["returned"], "bits", "4"))
    reject("missing-queue", remove(task["queued"]))
    reject("missing-return", remove(task["returned"]))
    reject("missing-initial-install", remove(task["installed"]))
    reject(
        "old-style-present", replace(task["management"]["index"], "old_present", "true")
    )
    reject("missing-same-call-smil-map", replace(smil, "smil", "0"))
    reject("wrong-pseudo-map", replace(cohort["mapped"], "pseudo", "94"))
    reject("wrong-map-process", replace(cohort["mapped"], "pid", "999999"))
    reject(
        "wrong-hint-insertion", replace(cohort["inserted"], "hint", "RestyleHint(0x0)")
    )
    reject("missing-css-install", remove(cohort["installed"]))
    reject(
        "wrong-css-install-thread",
        replace(cohort["installed"], "thread", "ThreadId(999)"),
    )
    reject(
        "missing-newer-generation-request",
        remove(first["delivery"]["cohorts"][-1]["requests"][-1]),
    )
    reject("missing-coalesced-request", remove(cohort["requests"][-1]))
    reject(
        "wrong-request-target",
        replace(task["requests"][0]["index"], "target_node", "0xdead"),
    )

    def malformed(altered):
        altered[task["installed"]]["data"] += " RFDP broken"

    reject("malformed-measured-record", malformed)

    def cap(altered):
        altered.insert(
            begin + 1,
            {
                "action": "process_output",
                "data": f"RFDP pid={first['pid']} capped file=test.rs limit=4096",
            },
        )

    reject("tested-process-cap", cap)

    def wrong_value(altered):
        altered[first["end"]]["data"] = altered[first["end"]]["data"].replace(
            "512px", "32px"
        )

    reject("wrong-getter-value", wrong_value)
    output = {
        "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "analyzer_sha256": hashlib.sha256(
            (here / "analyze.py").read_bytes()
        ).hexdigest(),
        "controls": controls,
    }
    (here / "ANALYZER-CONTROLS.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"negative_controls_rejected": len(controls)}))


if __name__ == "__main__":
    main()
