import collections, hashlib, json
from pathlib import Path
R = Path(__file__).resolve().parent
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pair = json.loads((R / "evidence/PAIR.json").read_text())
expected = json.loads((R / "inputs/EXPECTED.json").read_text())
keys = {(t, s) for t, names in expected.items() for s in names}
assert len(keys) == 82
all_rows = []
for phase in pair["phases"]:
    variant = phase["variant"]
    raw = R / "evidence" / variant / "raw.json"
    assert H(raw) == phase["raw_sha256"]
    rows, ends, suite = {}, {}, 0
    for line in raw.read_text().splitlines():
        e = json.loads(line)
        if e.get("action") == "test_status":
            k = (e["test"], e["subtest"])
            assert k not in rows, k
            rows[k] = e["status"]
        elif e.get("action") == "test_end":
            assert e["test"] not in ends
            ends[e["test"]] = e["status"]
        elif e.get("action") == "suite_end":
            suite += 1
    assert rows.keys() == keys
    assert ends.keys() == expected.keys() and set(ends.values()) == {"OK"}
    assert suite == 1
    assert rows == {(r["test"], r["subtest"]): r["status"] for r in phase["results"]["rows"]}
    assert phase["source_before"] == phase["source_after"] == pair["source_pins"][variant]
    assert phase["binaries_before"] == phase["binaries_after"]
    all_rows.append(rows)
a,b = all_rows
changes = [{"test": t, "subtest": s, "before": a[t,s], "after": b[t,s]} for t,s in sorted(keys) if a[t,s] != b[t,s]]
assert len(changes) == 4 and all(c["before"] == "FAIL" and c["after"] == "PASS" for c in changes)
assert all(c["test"] == "/css/css-values/map-taint-equality.html" for c in changes)
assert set(b.values()) == {"PASS"}
assert sorted(changes,key=lambda x:x["subtest"]) == sorted(pair["comparison"]["changes"],key=lambda x:x["subtest"])
build = pair["candidate_build"]
assert build["exit"] == 0
assert H(R/"evidence/candidate-build.log") == build["log_sha256"]
assert build["sources_before"] == build["sources_after"] == pair["source_pins"]["candidate"]
assert build["binaries_before"] == pair["phases"][0]["binaries_before"]
assert build["binaries_after"] == pair["phases"][1]["binaries_before"] == pair["final_binaries"]
assert build["binaries_before"]["XUL"] != build["binaries_after"]["XUL"]
assert pair["complete"] and pair["candidate_binary_validated"]
association = json.loads((R/"inputs/evidence/BUILD-ASSOCIATION.json").read_text())
assert H(R/"inputs/evidence/BUILD-ASSOCIATION.json") == pair["association_sha256"]
assert H(R/"inputs/evidence/BUILD-MATRIX.json") == association["build_matrix_sha256"]
assert association["combined_build"]["build_exit"] == 0
assert association["combined_build"]["binaries"] == pair["phases"][0]["binaries_before"]
for path, digest in pair["stable_pins"].items():
    assert pair["initial_pins"][path] == digest
print(json.dumps({"baseline":dict(collections.Counter(a.values())),"candidate":dict(collections.Counter(b.values())),"harness_per_phase":9,"unchanged_subtests":78,"changes":changes,"build_monitor_export_errors":(R/"evidence/candidate-build.log").read_text().count("KeyError: 'export'")},indent=2))
