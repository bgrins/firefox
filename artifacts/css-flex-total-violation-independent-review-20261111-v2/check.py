#!/usr/bin/env python3
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT.parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inventory(name, expected):
    p = ARTIFACTS / name
    assert sha(p / "FILES.json") == expected
    files = json.loads((p / "FILES.json").read_text())
    for name, digest in files.items():
        assert sha(p / name) == digest, (p, name)
    return len(files)

def fold(ds, lower, upper, check_difference=True, check_sum=True):
    acc = 0
    for d in ds:
        nxt = acc + d
        if check_difference and not lower <= d <= upper:
            return None
        if check_sum and not lower <= nxt <= upper:
            return None
        acc = nxt
    return acc

def main():
    old = ARTIFACTS / "css-flex-total-violation-target-20261111-v1"
    new = ARTIFACTS / "css-flex-total-violation-target-20261111-v2"
    counts = {
      "target_v1": inventory(old.name, "8137292f61dcf0577423568d4dd1cea16cd6b58861657ad514f4e496371284f1"),
      "target_v2": inventory(new.name, "35da97fd01118325fb0dbf706fe60dae24cf95f712e1e316f26134b38c321190"),
      "review_v1": inventory("css-flex-total-violation-independent-review-20261111-v1", "c001ab40e5d5d2237b788823a5cb32ce8594e60448c75d3e6dc0578c20312578")}
    paths = ["proof/FlexViolation/Model.lean", "proof/FlexViolation/Target.lean", "CONTRACT.md"]
    diff = "".join("".join(difflib.unified_diff((old / path).read_text().splitlines(True),
        (new / path).read_text().splitlines(True), fromfile="v1/"+path, tofile="v2/"+path))
        for path in paths)
    assert diff == (new / "TARGET-DELTA.patch").read_text()
    oldmodel = (old / paths[0]).read_text()
    newmodel = (new / paths[0]).read_text()
    a = """    let next := acc + adjustment item
    if lower ≤ next ∧ next ≤ upper then checkedFold lower upper next rest"""
    b = """    let contribution := adjustment item
    let next := acc + contribution
    if lower ≤ contribution ∧ contribution ≤ upper ∧ lower ≤ next ∧ next ≤ upper then
      checkedFold lower upper next rest"""
    added = """def subtractionWitness : List Item :=
  [{ identity := 0, before := max32, minimum := 0, maximum := 0 },
   { identity := 1, before := 1, minimum := 0, maximum := 0 },
   { identity := 2, before := min32, minimum := max32, maximum := max32 }]

"""
    assert a in oldmodel and added in newmodel
    assert oldmodel.replace(a,b).replace("end FlexViolation",added+"end FlexViolation") == newmodel
    oldtarget = (old / paths[1]).read_text()
    newtarget = (new / paths[1]).read_text()
    a = "  positiveWitness.filter (selected (kind (wrap32 (total positiveWitness)))) = []"
    b = a + """ ∧
  Acquired subtractionWitness ∧ total subtractionWitness = max32 ∧
  oldFold subtractionWitness = none ∧ wideFold subtractionWitness = some max32"""
    assert oldtarget.replace(a,b) == newtarget
    audit = (new / "elaboration-1/Audit.stdout").read_text().splitlines()
    names = ["PrefixTarget", "DifferenceTarget", "FoldTarget", "SelectionTarget",
             "ProgressTarget", "CompatibilityTarget", "WitnessTarget", "UniversalTarget"]
    assert audit == ["'FlexViolation."+n+"' does not depend on any axioms" for n in names]
    assert (new / "elaboration-1/Audit.stderr").read_bytes() == b""
    M, LO = 2**31-1, -2**31
    items = [(M,0,0),(1,0,0),(LO,M,M)]
    assert all(LO <= b <= M and 0 <= mn <= mx <= M for b,mn,mx in items)
    ds = [min(max(b,mn),mx)-b for b,mn,mx in items]
    assert ds == [-2147483647,-1,4294967295]
    prefixes = [sum(ds[:i]) for i in range(4)]
    assert all(LO <= x <= M for x in prefixes)
    assert fold(ds,LO,M,check_difference=False) == M
    assert fold(ds,LO,M) is None
    assert fold(ds,-2**63,2**63-1) == M
    positive = [0]+[600000000]*4
    assert fold(positive,LO,M,check_sum=False) == 2400000000
    assert fold(positive,LO,M) is None
    assert fold(positive,-2**63,2**63-1) == 2400000000
    assert fold([],LO,M) == 0
    assert fold([1,-1],LO,M) == 0
    result = dict(status="PASS amendment review diagnostics", inventories=counts,
        subtraction_deltas=ds, prefixes=prefixes, strict_old_result=None, wide_result=M,
        sum_only_wrong_result=M, difference_only_wrong_result=2400000000,
        unchanged_semantic_declarations="exact except checkedFold and added witness",
        final_iteration_boundary="inherited; no unconditional whole-helper refinement",
        correctness_proofs=0, native_commands=0, lean_commands=0)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
