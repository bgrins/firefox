import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / "css-hidden-layout-compact-runtime-v3"
result = {}
for phase in ["baseline", "principal-only", "oof-only", "both"]:
    path = RUNTIME / (phase + "-timing") / "RESULT.json"
    data = path.read_bytes()
    run = json.loads(data)
    assert run["before"] == run["after"] and run["stable"]
    assert run["terminal"] and run["noLiveGroup"] and not run["cleanupErrors"]
    assert run["profileRemoved"] and not (path.parent / "profile").exists()
    if run["failure"] is not None or len(run["observations"]) != 1:
        result[phase] = {"result_sha256": hashlib.sha256(data).hexdigest(),
                         "measurement_complete": False, "failure": run["failure"],
                         "observations": len(run["observations"]), "cleanup_verified": True}
        continue
    observation = run["observations"][0]
    assert observation["complete"] and observation["label"] == phase
    groups = defaultdict(lambda: {"reads": Counter(), "mismatches": Counter(), "samples": defaultdict(list)})
    rows = observation["rows"]
    assert len(rows) == 84
    for row in rows:
        group = groups[f'{row["kind"]}/{row["state"]}/{row["count"]}']
        for bucket, values in row["times"].items():
            group["samples"][bucket].append(sum(values))
        for record in row["observations"]:
            bucket = record["bucket"]
            x = (record["width"] - 8) / 2 if row["kind"] == "oof" else record["index"] * 8
            group["reads"][bucket] += 1
            group["mismatches"][bucket] += record["rect"] != [x, 0, 8, 8]
    assert sum(sum(g["reads"].values()) for g in groups.values()) == 13440
    for group in groups.values():
        group["medians_ms"] = {b: statistics.median(v) for b, v in group["samples"].items()}
    result[phase] = {"result_sha256": hashlib.sha256(data).hexdigest(), "measurement_complete": True, "groups": groups}
(HERE / "COST.json").write_text(json.dumps(result, indent=2) + "\n")
for phase, data in result.items():
    print(phase)
    if not data["measurement_complete"]:
        print(data)
        continue
    for kind in ["principal", "oof"]:
        group = data["groups"][kind + "/hidden/256"]
        print(kind, "medians_ms", group["medians_ms"], "mismatches", dict(group["mismatches"]))
