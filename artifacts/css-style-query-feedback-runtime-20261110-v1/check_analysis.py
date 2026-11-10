import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("feedback_analysis", HERE / "analyze.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rows = [json.loads(line) for line in (HERE / "runtime1/wpt-raw.jsonl").read_text().splitlines()]
assert module.analyze(rows)["records"] == 80


def reject(name, mutate):
    changed = copy.deepcopy(rows)
    mutate(changed)
    try:
        module.analyze(changed)
    except (ValueError, KeyError, TypeError):
        return name
    raise AssertionError("Accepted " + name)


def status(rows):
    return next(row for row in rows if row["action"] == "test_status")


def observation(rows):
    return next(row for row in rows if row.get("data", "").startswith("QF_PROBE "))


def change_observation(rows, key, value):
    row = observation(rows)
    data = json.loads(row["data"][len("QF_PROBE "):])
    data[key] = value
    row["data"] = "QF_PROBE " + json.dumps(data)


controls = [
    reject("wrong test", lambda rows: status(rows).update(test="/other.html")),
    reject("callback failure", lambda rows: status(rows).update(status="FAIL")),
    reject("missing observation", lambda rows: rows.remove(observation(rows))),
    reject("unknown mode", lambda rows: change_observation(rows, "mode", "unknown")),
    reject("pending baseline", lambda rows: change_observation(rows, "pending", True)),
    reject("malformed prefix", lambda rows: observation(rows).update(data="bad QF_PROBE {}")),
]
print(json.dumps({"baseline": "PASS", "rejected_controls": controls}, indent=2))
