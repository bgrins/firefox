import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MODES = ["opposed", "aligned", "constant-query", "stable-underlying"]
TEST = "/css/css-conditional/container-queries/style-query-timeline-feedback.html"
FIELDS = {"gate", "source", "timelineTime", "currentTime", "progress",
          "localTime", "pending", "playState", "providerName", "repeatGate"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def analyze(rows):
    starts = [row for row in rows if row["action"] == "test_start"]
    tests = [row for row in rows if row["action"] == "test_status"]
    endings = [row for row in rows if row["action"] == "test_end"]
    require(len(starts) == 1 and all(row.get("test") == TEST
            for row in starts + tests + endings), "test identity")
    require(len(tests) == 4 and [row["subtest"] for row in tests] == [
        "Style-query timeline feedback: " + mode for mode in MODES], "callback roster")
    require(all(row["status"] == "PASS" for row in tests), "callback failure")
    require(len(endings) == 1 and endings[0]["status"] == "OK", "harness ending")
    records = []
    for row in rows:
        data = row.get("data", row.get("message", ""))
        if isinstance(data, str) and "QF_PROBE" in data:
            require(data.startswith("QF_PROBE "), "malformed observation prefix")
            records.append(json.loads(data[len("QF_PROBE "):]))
    require(all(row.get("mode") in MODES for row in records), "unknown mode")
    require([row["mode"] for row in records] == sorted(
        [row["mode"] for row in records], key=MODES.index), "interleaved modes")
    result = {}
    for mode in MODES:
        selected = [row for row in records if row["mode"] == mode]
        prepare = [row for row in selected if row["phase"].startswith("prepare-")]
        require(1 <= len(prepare) <= 24, "preparation count")
        expected = ([f"prepare-{i}" for i in range(len(prepare))] +
                    ["armed-before", "armed-after"] +
                    [f"sync-{i}" for i in range(4)] +
                    [f"frame-{i}" for i in range(12)] + ["complete"])
        require([row["phase"] for row in selected] == expected, "phase sequence")
        require(all(set(row) == {"mode", "phase"} for row in selected
                    if row["phase"] in {"armed-before", "armed-after", "complete"}),
                "marker fields")
        observed = [row for row in selected if "gate" in row]
        require(all(set(row) == FIELDS | {"mode", "phase"} for row in observed),
                "observation fields")
        require(len(observed) == len(prepare) + 16, "observation count")
        baseline = prepare[-1]
        require(baseline["source"] == "fallback" and baseline["gate"] == "on" and
                baseline["pending"] is False and baseline["playState"] == "running" and
                baseline["progress"] is not None and abs(baseline["progress"] - .75) < .001,
                "baseline preconditions")
        snapshots = {phase: [row for row in observed if row["phase"].startswith(phase)]
                     for phase in ["sync-", "frame-"]}
        result[mode] = {
            "baseline": baseline,
            "snapshots": snapshots,
            "read_disagreements": sum(row["gate"] != row["repeatGate"] for row in observed),
        }
    return {"callbacks_pass": 4, "harnesses_ok": 1, "records": len(records),
            "modes": result, "snapshots_are_atomic": False,
            "native_drain_recurrence_established": False}


def main():
    raw = HERE / "runtime1/wpt-raw.jsonl"
    rows = [json.loads(line) for line in raw.read_text().splitlines()]
    result = analyze(rows)
    result["raw_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    result["fixture_sha256"] = hashlib.sha256(
        (HERE / "style-query-timeline-feedback.html").read_bytes()).hexdigest()
    output = HERE / (sys.argv[1] if len(sys.argv) > 1 else "ANALYSIS.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Authenticated {result['records']} records across four callbacks")


if __name__ == "__main__":
    main()
