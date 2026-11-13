import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUTHOR = ROOT / "artifacts/css-flex-scaled-weight-overflow-20261111-v1"
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(AUTHOR / "FILES.json") == "9a1bf9c782a3061ea6e3216c463803644572eea3865f20d76d81fa6891039ceb"
files = json.loads((AUTHOR / "FILES.json").read_text())
for n, h in files.items():
    assert sha(AUTHOR / n) == h, n
prior_review = ROOT / "artifacts/css-flex-scaled-weight-independent-review-20261111-v1"
assert sha(prior_review / "FILES.json") == "c9abf6dc29b07835d2e9340582b0fa98db367981363fcf2202477e547aa6de7a"
for n,h in json.loads((prior_review / "FILES.json").read_text()).items():
    assert sha(prior_review / n) == h
old = (AUTHOR / "before.cpp").read_text()
new = old.replace("float GetWeight(bool aIsUsingFlexGrow)", "double GetWeight(bool aIsUsingFlexGrow)").replace("return mFlexShrink * mFlexBaseSize;", "return double(mFlexShrink) * mFlexBaseSize;")
assert new == (ROOT / "layout/generic/nsFlexContainerFrame.cpp").read_text()
assert (AUTHOR / "native-only.patch").read_text().splitlines()[2:] == (prior_review / "reviewed.patch").read_text().splitlines()[2:]
test = "/css/css-flexbox/flex-shrink-large-finite-scaled-weights.html"
def rows(p):
    data = json.loads(p.read_text())["results"]
    assert len(data) == len({r["test"] for r in data})
    return {r["test"]:r for r in data}
before = rows(AUTHOR / "before/wptreport.json")
after = rows(AUTHOR / "after/wptreport.json")
assert set(before) == {test} and len(after) == 30
assert before[test]["status"] == after[test]["status"] == "OK"
assert Counter(s["status"] for s in before[test]["subtests"]) == {"PASS":48,"FAIL":24}
assert Counter(s["status"] for s in after[test]["subtests"]) == {"PASS":72}
assert {s["name"] for s in before[test]["subtests"]} == {s["name"] for s in after[test]["subtests"]}
assert len({s["name"] for s in after[test]["subtests"]}) == 72
prior = rows(ROOT / "artifacts/css-flex-measured-base-repair-20261111-v2/after.wptreport.json")
assert len(prior) == 28
for name, r in prior.items():
    assert r["status"] == after[name]["status"]
    assert {(s["name"],s["status"]) for s in r["subtests"]} == {(s["name"],s["status"]) for s in after[name]["subtests"]}
assert all(r["status"] in ["PASS","OK"] for r in after.values())
assert Counter(s["status"] for r in after.values() for s in r["subtests"]) == {"PASS":355}
for phase,code in [("before",1),("after",0)]:
    commands=json.loads((AUTHOR/phase/"COMMANDS.json").read_text())
    assert len(commands)==1 and commands[0]["exit"]==code
    follow=json.loads((AUTHOR/phase/"LIFECYCLE-FOLLOWUP.json").read_text())
    assert follow["pgid"]==commands[0]["pgid"] and follow["child_exit"]==code
    assert follow["probe"]=="absent" and follow["matching_rows"]==[] and follow["inputs_unchanged"]
    pins=json.loads((AUTHOR/phase/"INPUTS.json").read_text())
    assert sha(ROOT/('testing/web-platform/tests'+test)) == pins['testing/web-platform/tests'+test]
solver=json.loads((AUTHOR/"solver/run-1/RESULTS.json").read_text())
for name,answer in [("finite-weight-bound","unsat"),("overflow-witness","sat")]:
    assert solver[name]["exit"]==0 and solver[name]["output"].splitlines()[0]==answer
    assert sha(AUTHOR/"solver/run-1"/(name+".smt2"))==solver[name]["query_sha256"]
patch=(AUTHOR/"standalone.patch").read_text()
assert [s.split(" b/")[1] for s in patch.splitlines() if s.startswith("diff --git ")] == ["layout/generic/nsFlexContainerFrame.cpp","testing/web-platform/tests"+test]
transport=json.loads((AUTHOR/"PATCH-RESULT.json").read_text())
assert transport["patch_sha256"]==sha(AUTHOR/"standalone.patch")
assert transport["head_and_combined_apply_reverse"] and transport["scratch_removed"]
result={"status":"PASS","author_files":len(files),"prior_source_review_authenticated":True,"fixed_new_cases":72,"baseline_fail":24,"baseline_pass":48,"all_fixed_subtests":355,"all_fixed_files":30,"preserved_prior_files":28,"solver_recorded_answers":["unsat","sat"],"independent_build_browser_solver_execution":False,"fresh_process_probe":False,"lifecycle":"authenticated root followups; original wrapper failures retained"}
(HERE/"CHECK.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
