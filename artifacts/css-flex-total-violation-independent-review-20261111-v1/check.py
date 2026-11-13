#!/usr/bin/env python3
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
M = 2**31 - 1
LO = -2**31

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    inputs = json.loads((ROOT / "INPUTS.json").read_text())
    for name, row in inputs.items():
        assert digest(ROOT / "inputs" / name) == row["sha256"]
        assert digest(REPO / row["path"]) == row["sha256"]
    for name, sha in json.loads((ROOT / "EVIDENCE.json").read_text()).items():
        assert digest(REPO / name) == sha, name
    assert 'id="resolve-flexible-lengths"' in (ROOT / "css-flexbox-1.html").read_text()
    target = REPO / "artifacts/css-flex-total-violation-target-20261111-v1"
    assert digest(target / "FILES.json") == "8137292f61dcf0577423568d4dd1cea16cd6b58861657ad514f4e496371284f1"
    manifest = json.loads((target / "FILES.json").read_text())
    for name, sha in manifest.items():
        assert digest(target / name) == sha, name
    names = ["PrefixTarget", "DifferenceTarget", "FoldTarget", "SelectionTarget",
             "ProgressTarget", "CompatibilityTarget", "WitnessTarget", "UniversalTarget"]
    expected = ["'FlexViolation." + name + "' does not depend on any axioms" for name in names]
    assert (target / "elaboration-1/Audit.stdout").read_text().splitlines() == expected
    assert (target / "elaboration-1/Audit.stderr").read_bytes() == b""
    assert M * (2**32 - 1) == 9223372030412324865 < 2**63 - 1
    items = [(b, mn, mx) for b in [LO, -1, 0, 1, M]
             for mn, mx in [(0, 0), (0, 1), (1, 1), (0, M), (M, M)]]
    checked = 0
    for length in range(4):
        for xs in itertools.product(items, repeat=length):
            ds = [min(max(b, mn), mx) - b for b, mn, mx in xs]
            total = sum(ds)
            branch = [i for i, (b, mn, mx) in enumerate(xs)
                      if total == 0 or (total > 0 and b < mn)
                      or (total < 0 and b >= mn and b > mx)]
            relational = [i for i, d in enumerate(ds)
                          if total == 0 or (total > 0 and d > 0) or (total < 0 and d < 0)]
            assert branch == relational and (length == 0 or branch)
            assert all(LO <= b <= M and 0 <= mn <= mx <= M for b, mn, mx in xs)
            assert all(-(2**32 - 1) <= d <= 2**32 - 1 for d in ds)
            assert all(-2**63 <= sum(ds[:k]) <= 2**63 - 1 for k in range(length + 1))
            checked += 1
    fallback_items = [(0, 1, 1), (0, 0, 1)]
    fallback_sign_selected = [i for i, (b, mn, mx) in enumerate(fallback_items) if b < mn]
    fallback_native_final = list(range(len(fallback_items)))
    assert fallback_sign_selected == [0] and fallback_native_final == [0, 1]
    wrapped = (2400000000 - LO) % 2**32 + LO
    assert wrapped == -1894967296
    cases = []
    for n, m in [(5, 1000), (3, 10000000), (4, 10000000),
                 (5, 10000000), (7, 10000000), (357, 100000), (359, 100000)]:
        weight = Fraction(1000, 65536)
        deficit = n * m
        first_subject = 1000 - Fraction(deficit) * weight / (deficit + weight)
        first_primary = m - Fraction(deficit * m, 1) / (deficit + weight)
        total_adjustment_au = n * (m - first_primary) * 60
        expected_size = max(Fraction(0), Fraction(1000) - Fraction(deficit, 65536))
        assert first_subject > 0 and 0 < first_primary < m
        cases.append(dict(n=n, m=m, expected=str(expected_size),
                          first_positive_total_au=str(total_adjustment_au),
                          exceeds_signed32=total_adjustment_au > M))
    repair = REPO / "artifacts/css-flex-total-violation-repair-20261111-v1"
    browser = {}
    for filename in ["before.wptreport.json", "after.wptreport.json"]:
        raw = repair / filename
        data = json.loads(raw.read_text())
        subtests = [s for r in data["results"] for s in r["subtests"]]
        browser[filename] = dict(sha256=digest(raw), files=len(data["results"]),
            subtests=dict(Counter(s["status"] for s in subtests)),
            harnesses=dict(Counter(r["status"] for r in data["results"])),
            build=data["run_info"]["browser_build_id"])
    assert browser["before.wptreport.json"]["subtests"] == {"PASS":12,"FAIL":16}
    assert browser["after.wptreport.json"]["subtests"] == {"PASS":211}
    assert sum(browser["after.wptreport.json"]["harnesses"].values()) == 20
    assert all(k in ["PASS", "OK"] for k in browser["after.wptreport.json"]["harnesses"])
    print(json.dumps(dict(status="PASS review diagnostics", target_files=len(manifest),
                          finite_lists=checked, wpt_formula_cases=cases, browser=browser,
                          wrap32_witness=wrapped,
                          final_iteration_boundary=dict(sign_selected=fallback_sign_selected,
                                                        native_final=fallback_native_final),
                          correctness_proofs=0,
                          native_commands=0, lean_commands=0), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
