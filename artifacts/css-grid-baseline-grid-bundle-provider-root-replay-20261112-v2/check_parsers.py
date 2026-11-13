import ast
import copy
import importlib.util
import json
import re
from pathlib import Path

import provider_parse as provider
import work_parse as work

HERE = Path(__file__).resolve().parent


def refused(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError("malformed trace was accepted")


def bundle_records(d, key="cache-absent", stored=0, cached_bundle=0,
                   cached_present=0, grid=None, produced=1, dirty=0, present=1):
    rows = []
    grid = d >= 3 if grid is None else grid

    def event(stage, **values):
        row = {name: 0 for name in work.FIELDS}
        row.update(seq=len(rows) + 1, stage=stage, id="gsw-level-0", phase="seed",
                   call=1, demand=d, site="baseline" if d else "content", frame="0x123")
        row.update(values)
        rows.append(row)

    event("call-begin")
    event(key, subtree=int(key == "key-dirty"), v0=int(key == "key-mismatch"))
    hit = key == "key-valid" and (d == 0 or d == stored or (cached_bundle and d >= 3))
    if key == "key-valid":
        event("demand-hit" if hit else "demand-miss", v0=d, v1=stored,
              v2=cached_bundle, v3=cached_present)
    if hit:
        event("cache-hit")
    else:
        event("measure-begin")
        if grid:
            event("producer-reset")
            if produced:
                event("producer-complete", v0=1)
        event("capture-begin", subtree=dirty, v0=d, v1=int(grid), v2=produced, v3=dirty)
        bundled = bool(d >= 3 and grid and produced and not dirty)
        queries = [(1, 0), (1, 1), (2, 0), (2, 1)] if bundled else ([] if work.QUERY[d] is None else [work.QUERY[d]])
        for kind, group in queries:
            event("query-begin", v0=kind, v1=group)
            event("query-end", v0=kind, v1=group, v2=int(kind == 0),
                  v3=3 * int(kind == 0), v4=int(kind == 0))
        present = 0 if d == 0 else (1 if d >= 3 else present)
        event("capture-end", v0=d, v1=present, v2=int(bundled))
        event("store-create" if key == "cache-absent" else "store-update",
              v0=d, v1=present, v2=int(bundled))
        event("measure-end")
    event("call-end")
    return rows


def encode_work(rows):
    return "\n".join("GRIDWORK " + " ".join(f"{key}={row[key]}" for key in work.FIELDS)
                     for row in rows) + "\n"


def provider_records(d, produced=1, clean=1, present=1, provider_ok=1):
    rows = []

    def event(stage, **values):
        row = {name: 0 for name in provider.FIELDS}
        row.update(seq=len(rows) + 1, stage=stage, id="gse-text-visible", phase="seed",
                   request="content" if d == 0 else "baseline", capture=1,
                   frame="0x123", owner="0x123", parent="0x456")
        row.update(values)
        rows.append(row)

    event("capture-begin", subtree=1-clean, v2=d, v3=produced, v4=clean, v5=int(d >= 3))
    bundled = bool(d >= 3 and produced and clean)
    queries = [(1, 0), (1, 1), (2, 0), (2, 1)] if bundled else ([] if work.QUERY[d] is None else [work.QUERY[d]])
    for kind, group in queries:
        if kind == 0:
            event("natural-before", v0=group)
            event("text-clean", v0=group, v1=provider_ok)
            event("natural-after", v0=group, v1=present, v2=17 if present else 0)
        else:
            event("grid-before", v0=group, v1=1 if kind == 1 else 0)
            event("grid-after", v0=group, v1=23, v2=1 if kind == 1 else 0)
    event("capture-end", v0=int(bundled), v1=0 if d == 0 else (1 if d >= 3 else present), v2=d)
    return rows


def encode_provider(rows):
    return "\n".join("GRIDSNAPSHOT " + " ".join(f"{key}={row[key]}" for key in provider.FIELDS)
                     for row in rows) + "\n"


def main():
    legacy_path = HERE.parent / "css-grid-baseline-measurement-work-trace-plan-20261112-v2/check.py"
    source = legacy_path.read_text()
    node = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "stream")
    scope = {"m": work}
    exec(ast.get_source_segment(source, node), scope)
    legacy_stream = scope["stream"]
    legacy_count = 0
    for version in ("old", "demand"):
        for demand in range(7):
            reasons = ["hit", "cache-absent", "key-dirty", "key-mismatch"]
            if version == "demand" and demand:
                reasons.append("demand-miss")
            for reason in reasons:
                assert work.parse(legacy_stream(version, demand, reason), version)["calls"] == 1
                legacy_count += 1
    bundle_count = 0
    for demand in range(7):
        for reason in ("cache-absent", "key-dirty", "key-mismatch"):
            for produced in (0, 1):
                for dirty in (0, 1):
                    parsed = work.parse(encode_work(bundle_records(demand, key=reason, produced=produced, dirty=dirty)), "bundle")
                    assert parsed["measures"] == 1 and parsed["hits"] == 0
                    bundle_count += 1
        for stored in range(7):
            for bundled in ((0, 1) if stored >= 3 else (0,)):
                for present in ((0,) if stored == 0 else ((0, 1) if stored < 3 else (1,))):
                    parsed = work.parse(encode_work(bundle_records(demand, key="key-valid", stored=stored,
                                        cached_bundle=bundled, cached_present=present)), "bundle")
                    assert parsed["hits"] == int(demand == 0 or demand == stored or (bundled and demand >= 3))
                    bundle_count += 1
    parent = bundle_records(3)
    child = bundle_records(5)
    for row in child:
        row.update(call=2, frame="0x456", id="gsw-level-1")
    position = next(i for i, row in enumerate(parent) if row["stage"] == "measure-begin") + 1
    nested = parent[:position] + child + parent[position:]
    for i, row in enumerate(nested):
        row["seq"] = i + 1
    parsed = work.parse(encode_work(nested), "bundle")
    assert parsed["calls"] == 2 and sum(parsed["query_groups"].values()) == 8
    assert parsed["bundle_totals"]["grid_scalar_reads"] == 8
    assert parsed["bundle_totals"]["captured_requested_exports"] == 2
    assert parsed["bundle_totals"]["bundled_captures"] == 2
    generation = bundle_records(0, key="key-mismatch", grid=True)
    next_request = bundle_records(4, key="key-valid", stored=0)
    for row in next_request:
        row["call"] = 2
        row["seq"] += len(generation)
    parsed = work.parse(encode_work(generation + next_request), "bundle")
    assert parsed["exact_demand_miss_totals"] == {"(0, 4)": 1}
    assert sum(parsed["query_groups"].values()) == 4
    for before, after in ((4, 5), (5, 4)):
        reused = work.parse(encode_work(bundle_records(after, key="key-valid", stored=before,
                           cached_bundle=1, cached_present=1)), "bundle")
        assert reused["exact_bundle_switch_hits"] == {str((before, after)): 1}
        assert reused["bundle_totals"]["grid_scalar_reads"] == 0
    bad_cases = []
    good = bundle_records(3)
    for stage in ("producer-reset", "producer-complete", "capture-begin", "capture-end", "query-end", "store-create"):
        rows = copy.deepcopy(good)
        rows.pop(next(i for i, row in enumerate(rows) if row["stage"] == stage))
        for i, row in enumerate(rows):
            row["seq"] = i + 1
        bad_cases.append(encode_work(rows))
    for stage, field, value in (("query-end", "v0", 2), ("query-end", "v2", 1),
                                ("capture-begin", "v3", 1), ("capture-end", "v2", 0),
                                ("store-create", "v0", 0), ("producer-reset", "v0", 1)):
        rows = copy.deepcopy(good)
        next(row for row in rows if row["stage"] == stage)[field] = value
        bad_cases.append(encode_work(rows))
    bad_cases += [encode_work(good) + "GRIDWORK TRUNCATED\n", encode_work(good[:-1]),
                  encode_work(good).replace("seq=2 ", "seq=3 "), "GRIDWORK " + "x" * 513]
    for text in bad_cases:
        refused(lambda: work.parse(text, "bundle"))
    provider_count = 0
    for demand in range(7):
        for produced in (0, 1):
            for clean in (0, 1):
                for present in ((0, 1) if demand in (1, 2) else (1,)):
                    result = provider.parse(encode_provider(provider_records(demand, produced, clean, present)))
                    assert result["captures"] == 1 and not result["capture_predicate_violations"]
                    provider_count += 1
    violations = provider.parse(encode_provider(provider_records(1, provider_ok=0)))
    assert len(violations["capture_predicate_violations"]) == 1
    malformed_provider = []
    for stage, field, value in (("grid-after", "v2", 0), ("capture-end", "v0", 0),
                                ("capture-begin", "v3", 0), ("capture-end", "v2", 4)):
        rows = provider_records(3)
        next(row for row in rows if row["stage"] == stage)[field] = value
        malformed_provider.append(encode_provider(rows))
    malformed_provider.extend([encode_provider(provider_records(3)[:-1]),
                               encode_provider(provider_records(0)) + "GRIDSNAPSHOT TRUNCATED\n"])
    for text in malformed_provider:
        refused(lambda: provider.parse(text))
    strict_refusals = []
    for present in (0, 1):
        rows = provider_records(1, present=present)
        after = next(row for row in rows if row["stage"] == "natural-after")
        after.update(v1=1-present, v2=17 if not present else 0)
        strict_refusals.append(("natural-presence-" + str(present), "provider", rows))
    rows = provider_records(1)
    next(row for row in rows if row["stage"] == "natural-after")["v1"] = 2
    strict_refusals.append(("natural-nonboolean", "provider", rows))
    for clean in (0, 1):
        rows = provider_records(3, clean=clean)
        rows[0]["subtree"] = clean
        strict_refusals.append(("provider-clean-" + str(clean), "provider", rows))
    for dirty in (0, 1):
        rows = bundle_records(3, dirty=dirty)
        next(row for row in rows if row["stage"] == "capture-begin")["subtree"] = 1-dirty
        strict_refusals.append(("work-dirty-" + str(dirty), "work", rows))
    for demand in (1, 3):
        for stage in ("capture-begin", "capture-end",
                      "natural-before" if demand == 1 else "grid-before",
                      "natural-after" if demand == 1 else "grid-after"):
            rows = provider_records(demand)
            next(row for row in rows if row["stage"] == stage)["frame"] = "0x999"
            strict_refusals.append(("provider-frame-" + stage, "provider", rows))
    for stage in ("capture-begin", "capture-end", "query-begin", "query-end"):
        rows = bundle_records(3)
        next(row for row in rows if row["stage"] == stage)["frame"] = "0x999"
        strict_refusals.append(("work-frame-" + stage, "work", rows))
    for label, kind, rows in strict_refusals:
        if kind == "provider":
            refused(lambda: provider.parse(encode_provider(rows)))
        else:
            refused(lambda: work.parse(encode_work(rows), "bundle"))
    descendants = provider_records(1)
    next(row for row in descendants if row["stage"] == "text-clean")["frame"] = "0x789"
    assert provider.parse(encode_provider(descendants))["captures"] == 1

    real = {}
    prior = HERE.parent / "css-grid-baseline-measurement-work-completion-plan-20261112-v1/parse.py"
    spec = importlib.util.spec_from_file_location("prior_work", prior)
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    native = HERE.parent / "css-grid-baseline-measurement-work-native-20261112-v3"
    for version in ("old", "demand"):
        path = native / (version + "-instrumented-d1-parallel-TRACE.log")
        result = work.parse_file(path, version)
        assert result == previous.parse_file(path, version)
        real[version] = {key: result[key] for key in ("records", "calls", "measures", "hits")}
    result = dict(status="PASS source-only parser controls", legacy_cases=legacy_count,
                  bundle_cases=bundle_count, nested_bundle_queries=8,
                  geometry_replacement_then_grid_miss=True, bundle_refusals=len(bad_cases),
                  provider_cases=provider_count, provider_refusals=len(malformed_provider),
                  unsafe_provider_predicate_retained=True, retained_real_streams=real,
                  v2_refusals=[label for label, _, _ in strict_refusals],
                  descendant_provider_identity_admitted=True,
                  native_execution=False)
    (HERE / "PARSER-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
