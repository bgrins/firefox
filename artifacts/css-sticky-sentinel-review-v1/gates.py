import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import collections,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read_run(folder,baseline=False):
    if baseline:
        receipt=ROOT/"inputs/baseline-RUN.json";raw=ROOT/"inputs/baseline-raw.json"
    else:
        receipt=ROOT/"inputs"/folder/"RUN.json";raw=ROOT/"inputs"/folder/"raw.json"
    d=json.loads(receipt.read_text());assert d["before"]==d["after"] and d["stable_pins"]
    events=[json.loads(s) for s in raw.read_text().splitlines()]
    sub=[e for e in events if e.get("action")=="test_status"]
    ends=[e for e in events if e.get("action")=="test_end"]
    assert sub==d["rows"] and ends==d["harness"]
    return d,sub,ends
b,bs,be=read_run("",True);c,cs,ce=read_run("candidate-wpt-v2")
assert b["complete"] and c["complete"] and b["exit"]==1 and c["exit"]==0
assert len(bs)==len(cs)==24
key=lambda r:(r["test"],r["subtest"])
bm={key(r):r["status"] for r in bs};cm={key(r):r["status"] for r in cs}
assert len(bm)==24 and bm.keys()==cm.keys()
assert collections.Counter(bm.values())=={"PASS":20,"FAIL":4} and set(cm.values())=={"PASS"}
assert [r["status"] for r in be]==["OK"] and [r["status"] for r in ce]==["OK"]
changed=sorted(k for k in b["before"] if b["before"][k]!=c["before"][k])
assert changed==["layout/generic/StickyScrollContainer.cpp","objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL","objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox"]
assert c["before"]["layout/generic/StickyScrollContainer.cpp"]==sha(ROOT/"inputs/candidate.cpp")
assert c["before"]["testing/web-platform/tests/css/css-position/sticky/position-sticky-auto-insets-large-coordinate.html"]==sha(ROOT/"inputs/wpt.html")
r,rs,re_=read_run("regressions-wpt-v2");assert r["complete"] and r["exit"]==0
assert len(rs)==1328 and all(x["status"]=="PASS" for x in rs)
assert collections.Counter(x["status"] for x in re_)=={"PASS":3,"OK":5}
t,ts,te=read_run("timelines-wpt-v2");assert t["exit"]==0 and not t["complete"]
assert collections.Counter(x["status"] for x in ts)=={"PASS":8,"FAIL":2}
assert collections.Counter(x["status"] for x in te)=={"PASS":1,"OK":6}
meta=ROOT/"inputs/single-axis-expected.ini"
assert t["before"]["testing/web-platform/meta/css/css-position/sticky/position-sticky-single-axis-basic.html.ini"]==sha(meta)
expected_names=set(re.findall(r"^  \[(.*)\]\n    expected: FAIL$",meta.read_text(),re.M))
assert {x["subtest"] for x in ts if x["status"]=="FAIL"}==expected_names and len(expected_names)==2
assert all(x.get("expected",x["status"])==x["status"] for x in ts+te)
patch=(ROOT/"inputs/fix-candidate-v1.patch").read_text();chunks=patch.split("--- ")[1:];assert len(chunks)==2
first=chunks[0].splitlines(keepends=True)[3:]
old="".join(s[1:] for s in first if s.startswith((" ","-")))
new="".join(s[1:] for s in first if s.startswith((" ","+")))
for file,target in [("inputs/before.cpp","inputs/candidate.cpp"),("upstream-StickyScrollContainer.cpp",None)]:
    data=(ROOT/file).read_text();assert data.count(old)==1
    updated=data.replace(old,new,1);assert updated.replace(new,old,1)==data
    if target:assert updated==(ROOT/target).read_text()
second=chunks[1].splitlines(keepends=True)[3:]
assert all(s.startswith("+") for s in second)
assert "".join(s[1:] for s in second)==(ROOT/"inputs/wpt.html").read_text()
pack=json.loads((ROOT/"inputs/PACKAGING.json").read_text());assert pack["patch_sha256"]==sha(ROOT/"inputs/fix-candidate-v1.patch")
print(json.dumps({"complete":True,"paired":{"baseline":{"PASS":20,"FAIL":4},"candidate":{"PASS":24},"improvements":4,"changed_pins":changed},"regressions":{"PASS_subtests":1328,"PASS_reftests":3},"followup":{"PASS_subtests":8,"expected_FAIL":2,"PASS_reftests":1,"mach_exit":0,"wrapper_complete":False,"pinned_metadata_verified":True},"independent_in_memory_patch_apply_reverse":True,"historical_git_packaging":"Retained producer receipts; reviewer performed no Git operations"},indent=2))
