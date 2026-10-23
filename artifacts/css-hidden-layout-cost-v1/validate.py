import math
import statistics

TIMERS = ["constructionMs", "establishMs", "mutationFlushMs", "recoveryPrepareMs", "recoveryQueryMs"]

def validate(observation, config, label):
    if observation.get("complete") is not True or observation.get("label") != label or observation.get("config") != config:
        raise ValueError("Incomplete or mismatched observation")
    elapsed = observation.get("elapsedMs")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError("Invalid elapsed time")
    configs = [(kind, state, count) for kind in config["kinds"] for state in config["states"] for count in config["sizes"]]
    rows = observation["rows"]
    if len(rows) != len(configs) * config["measured_rounds"]:
        raise ValueError("Wrong row count")
    queries = 0
    mismatches = 0
    groups = {}
    for position, row in enumerate(rows):
        round_no, slot = divmod(position, len(configs))
        ordinal = (slot + round_no + config["warmup_rounds"]) % len(configs)
        kind, state, count = configs[ordinal]
        if [row.get(k) for k in ("round", "slot", "ordinal", "kind", "state", "count")] != [round_no, slot, ordinal, kind, state, count]:
            raise ValueError("Wrong row identity/order")
        n = min(count, config["query_limit"])
        indices = [0] if n == 1 else [i * (count - 1) // (n - 1) for i in range(n)]
        if row["indices"] != indices:
            raise ValueError("Wrong selected leaves")
        for key in TIMERS:
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError("Invalid timer")
        expected_outer = sum((168 if i % 2 == 0 else 160) + 64 for i in range(config["iterations"]))
        expected_queries = sum((ordinal + 1) * (i + 1) * (index + 1) for i in range(config["iterations"]) for index in indices)
        if row["outerChecksum"] != expected_outer or row["queryChecksum"] != expected_queries:
            raise ValueError("Work checksum mismatch")
        sizes = row["observedSizes"]
        if len(sizes) != n * config["iterations"]:
            raise ValueError("Missing geometry reads")
        for size in sizes:
            if not isinstance(size, list) or len(size) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in size):
                raise ValueError("Invalid geometry")
        geometry_checksum = sum(w * 17 + h * 31 for w, h in sizes)
        bad = sum(size != [8, 8] for size in sizes)
        if row["geometryChecksum"] != geometry_checksum or row["mismatches"] != bad:
            raise ValueError("Geometry receipt mismatch")
        queries += len(sizes)
        mismatches += bad
        group = groups.setdefault(f"{kind}/{state}/{count}", {key: [] for key in TIMERS})
        for key in TIMERS:
            group[key].append(row[key])
    summary = {}
    for group, timers in groups.items():
        summary[group] = {key: {"samplesMs": values, "medianMs": statistics.median(values), "minMs": min(values), "maxMs": max(values), "zeroSamples": values.count(0)} for key, values in timers.items()}
    return {"measuredRows": len(rows), "queryReads": queries, "geometryMismatches": mismatches, "mutationFlushes": len(rows) * config["iterations"], "recoveryPreparations": len(rows) * config["iterations"], "groups": summary, "interpretation": "Descriptive per-batch distributions; geometry mismatches are retained, not accepted as equivalent work."}
