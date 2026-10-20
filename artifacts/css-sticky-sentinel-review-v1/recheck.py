import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((ROOT/"inputs/CANDIDATE.json").read_text())
assert sha(ROOT/"inputs/before.cpp")==pins["before_sha256"]
assert sha(ROOT/"inputs/candidate.cpp")==pins["candidate_sha256"]
def split_position(s):
    a=s.index("nsPoint StickyScrollContainer::DoComputePosition(")
    b=s.index("nsPoint StickyScrollContainer::ComputeTranslationIgnoringScrolling(",a)
    return s[:a],s[a:b],s[b:]
old=split_position((ROOT/"inputs/before.cpp").read_text())
new=split_position((ROOT/"inputs/candidate.cpp").read_text())
assert old[0]==new[0] and old[2]==new[2]
upstream=split_position((ROOT/"upstream-StickyScrollContainer.cpp").read_text())
assert upstream[1]==old[1]
for edge in ["top","bottom","left","right"]:
    assert new[1].count(f"if (computedOffsets->{edge} != NS_AUTOOFFSET)")==1
assert new[1].index("computedOffsets->top")<new[1].index("computedOffsets->bottom")<new[1].index("computedOffsets->left")<new[1].index("computedOffsets->right")
expected=set(itertools.product([100,8000000,8947840,8947848,8947856,9000000,11666666],["static","relative","sticky"],[0,100]))
runs={}
for run in ["candidate-v2","release-v2"]:
    d=json.loads((ROOT/"inputs/probe"/run/"RESULT.json").read_text());assert d["stable"] and d["before"]==d["after"] and d["profile_removed"]
    rows=d["observations"][0]["rows"];keys=[(r["spacerSize"],r["position"],r["requestedScroll"]) for r in rows]
    assert len(rows)==42 and len(set(keys))==42 and set(keys)==expected
    for r in rows:
        assert r["actualScroll"]==r["requestedScroll"] and r["computedPosition"]==r["position"]
        assert r["cbHeight"]==17000000 and r["spacerHeight"]==r["spacerSize"] and r["targetHeight"]==10
        if r["position"]=="sticky":assert r["topInset"]=="auto" and r["bottomInset"]=="auto"
        assert r["matches"]==(abs(r["targetTop"]-r["spacerTop"]-r["spacerSize"])<=2)
    bad=[r for r in rows if not r["matches"]]
    assert len(bad)==6 and all(r["position"]=="sticky" and r["spacerSize"]>=8947856 for r in bad)
    assert sum(r["matches"] and r["position"]!="sticky" for r in rows)==28
    runs[run]={"rows":42,"sticky_discrepancies":6,"matching":36,"ordinary_controls":28,"stable":True,"raw_sha256":sha(ROOT/"inputs/probe"/run/"RESULT.json")}
print(json.dumps({"complete":True,"source_only_DoComputePosition_delta":True,"exact_upstream_function_applicability":True,"runs":runs},indent=2))
