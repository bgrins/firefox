import gzip, hashlib, json, re
from pathlib import Path


def run(producer, retained):
    inventory = json.loads((producer / "THEOREMS.json").read_text())
    declarations = []
    for path in (producer / "lean").glob("*.lean"):
        declarations += [path.stem + "." + name for name in
                         re.findall(r"^theorem ([A-Za-z0-9_]+)", path.read_text(), re.M)]
    assert len(declarations) == len(set(declarations)) == 172
    assert set(declarations) == set(inventory) and len(inventory) == 172
    audits = re.findall(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",
                        (retained / "AXIOMS.txt").read_text())
    assert len(audits) == len({n for n, _ in audits}) == 172
    assert {n for n, _ in audits} == set(inventory)
    for _, axioms in audits:
        assert {a.strip() for a in axioms.split(",") if a.strip()} <= {"propext", "Quot.sound", "Classical.choice"}
    source_root = producer / "evidence/all-order"
    extraction_counts = {}
    for variant in ["original", "candidate"]:
        records = json.loads((retained / "native" / (variant + "-extraction.json")).read_text())
        extraction_counts[variant] = len(records)
        for record in records:
            raw = (source_root / record["source_file"]).read_text()
            body = record["body"]
            assert raw[record["start"]:record["start"] + len(body)] == body
            assert body.startswith(record["anchor"])
            assert hashlib.sha256(body.encode()).hexdigest() == record["sha256"]
    assert extraction_counts == {"original": 37, "candidate": 38}
    provider = json.loads((retained / "native/PROVIDERS.json").read_text())
    rows = provider["longhands"]
    assert len(rows) == 431 and [r["id"] for r in rows] == list(range(431))
    def opposite(a, b):
        if a >= 431 or b >= 431:
            return False
        x, y = rows[a], rows[b]
        return x["group"] is not None and x["group"] == y["group"] and x["logical"] != y["logical"]
    ordinary = {k: v for k, v in provider["shorthands"].items() if k != "all"}
    assert len(ordinary) == 94 and max(map(len, ordinary.values())) == 19
    for ids in ordinary.values():
        assert len(ids) == len(set(ids))
        assert not any(opposite(a, b) for a in ids for b in ids)
    def cells(text):
        return [tuple(map(int, c.split(":"))) for c in text.split(",")] if text else []
    def forward(before, actions):
        current = list(before)
        for action in actions:
            matches = [i for i, e in enumerate(current) if e[0] == action[0]]
            assert len(matches) <= 1
            if not matches:
                current.append(action)
            else:
                i = matches[0]
                if any(opposite(action[0], e[0]) for e in current[i + 1:]):
                    del current[i]
                    current.append(action)
                else:
                    current[i] = action
        return current
    summaries = {}
    names = None
    for file in sorted((retained / "native").glob("*.tsv.gz")):
        variant = file.name.split(".")[0]
        lines = gzip.decompress(file.read_bytes()).decode().splitlines()
        assert len(lines) == 18
        fields = [line.split("\t") for line in lines]
        assert all(len(f) == 15 and f[0] == "ROW" for f in fields)
        this_names = [f[1] for f in fields]
        assert len(set(this_names)) == 18
        if names is None:
            names = this_names
        assert names == this_names
        bad = []
        panics = []
        for f in fields:
            seed, actions, observed = cells(f[6]), cells(f[9]), cells(f[11])
            expected = forward(seed, actions)
            expected_bits = "".join(str(e[2]) for e in expected)
            expected_set = ",".join(map(str, sorted(e[0] for e in expected)))
            expected_remaining = "" if f[2] == "1" else f[10]
            if f[5] == "0":
                panics.append(f[1])
            if (f[5] != "1" or observed != expected or f[12] != expected_bits or
                    f[13] != expected_set or f[14] != expected_remaining):
                bad.append(f[1])
        summaries[variant] = {"rows": len(lines), "discriminating": len(bad), "panics": len(panics), "names": bad}
    assert summaries["candidate"]["discriminating"] == summaries["original"]["discriminating"] == 0
    assert (retained / "native/candidate.tsv.gz").read_bytes() == (retained / "native/original.tsv.gz").read_bytes()
    for variant, counts in {"mutant_ascending": (8, 0), "mutant_rank_omitted": (4, 0), "mutant_rank_plus": (4, 2), "mutant_remove_bits": (8, 0), "mutant_replace_bits": (6, 0)}.items():
        assert (summaries[variant]["discriminating"], summaries[variant]["panics"]) == counts
    return {"exact_audits": len(audits), "source_records": extraction_counts,
            "ordinary_provider_lists": len(ordinary), "max_expansion": 19,
            "fresh_rows_independent_forward_check": summaries,
            "limits": "Row interpretation uses independently computed forward outcomes from the observed inputs; the separate producer oracle also binds those inputs to its fixed driver roster. This does not prove compiler, value abstraction, or metadata generation correctness."}
