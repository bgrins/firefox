import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def read(name):
    return json.loads((HERE / name).read_text())
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
def git(*args):
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
def pins(names):
    return {n: sha(ROOT / n) if (ROOT / n).is_file() else None for n in names}

c = read("CONFIG.json")
s = read("STATE.json")
before, final = read("BEFORE.json"), read("FINAL.json")
need(s["status"] == "terminal" and s["restored"] and not s["recovery_errors"], "not restored")
need(s["restore_build_exit"] == 0 and "failure" not in s, "build failure")
need(before == final, "snapshot mismatch")
need(git("rev-parse", "HEAD").decode().strip() == c["head"] == final["head"], "HEAD changed")
for key, args in [
    ("index_diff_sha256", ["diff", "--cached", "--binary"]),
    ("index_entries_sha256", ["ls-files", "--stage", "-z"]),
    ("native_diff_sha256", ["diff", "--binary", "--", "layout", "dom", "servo"])]:
    need(hashlib.sha256(git(*args)).hexdigest() == final[key], key)
need(pins(c["guard_sources"]) == final["sources"] == c["source_pins"], "live source guards")
for n in c["sources"]:
    need((ROOT / n).read_bytes() == (HERE / "original" / n).read_bytes(), "saved body " + n)
modified = [n for n in git("diff", "--name-only").decode().splitlines() if not n.startswith("artifacts/")]
need(modified == c["modified_native_paths"], "complete native roster")
need(not git("ls-files", "--others", "--exclude-standard", "--", "layout", "dom", "servo", "mfbt"), "untracked native")
need(pins(c["existing_tests"]) == c["existing_test_pins"], "existing tests")
need(git("ls-files", "--", *c["existing_tests"]).decode().splitlines() == c["tracked_existing_tests"], "test ownership")
resources = read("RESOURCES.json")
need(pins(resources) == resources, "resource guards")
need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c["must_be_absent"]), "temporary paths")
need(pins(s["restored_binary_pins"]) == s["restored_binary_pins"], "restored binaries")
need(s.get("paired_preservation_passed") and s.get("lint_exit") == 0, "comparison/lint gate")
owned = next(iter(c["install"]))
need(not (ROOT / owned).exists() and not (ROOT / owned).is_symlink() and not git("ls-files", "--", owned), "owned WPT remains")
for n, h in read("TEST-SOURCE-PINS.json").items():
    need(sha(ROOT / n) == h and hashlib.sha256(git("show", "HEAD:" + n)).hexdigest() == h, "comparison test " + n)
runs = {}
for phase, counts in (("baseline", {"PASS":208,"FAIL":8}), ("candidate", {"PASS":212,"FAIL":4})):
    record = s["phases"][phase]
    need(record["build_exit"] == 0 and record["source_before_build"] == record["source_after_build"], "phase build/source")
    expected = {**c["head_pins"], **(c["candidate_pins"] if phase == "candidate" else {})}
    need(record["source_after_build"]["sources"] == expected, "phase source role")
    need(all(record["source_after_build"][k] == before[k] for k in ("head","index_diff_sha256","index_entries_sha256")), "phase HEAD/index")
    run = read(phase + "/RUN.json")
    cleanup = read(phase + "/CLEANUP.json")
    need(cleanup["owned_group_absent"] and not cleanup["errors"], "WPT cleanup")
    need(run["complete"] and run["before"] == run["after"] and not run["infrastructure_faults"], "phase complete/stable")
    expected.update(record["binary_pins"])
    expected.update({**resources, owned: sha(HERE / c["install"][owned])})
    need(all(run["before"][n] == h for n,h in expected.items()), "tested source/binary/resource role")
    events = [json.loads(line) for line in (HERE / phase / "raw.json").read_text().splitlines()]
    for action, key in (("test_status","rows"),("test_start","starts"),("test_end","ends")):
        need([e for e in events if e.get("action") == action] == run[key], "raw " + key)
    need(sum(e.get("action") == "suite_start" for e in events) == sum(e.get("action") == "suite_end" for e in events) == 1, "suite complete")
    names = set(c["expected_subtests"]) | {c["reference_test"]}
    need(len(run["starts"]) == len(run["ends"]) == len(names) == 14 and {e["test"] for e in run["starts"]} == {e["test"] for e in run["ends"]} == names, "file roster")
    need(len(run["rows"]) == len({(r["test"],r["subtest"]) for r in run["rows"]}) == 216, "row roster")
    for test, names in c["expected_subtests"].items():
        need([r["subtest"] for r in run["rows"] if r["test"] == test] == names, "row names")
    need({status:sum(r["status"] == status for r in run["rows"]) for status in counts} == counts == record["subtests"], "counts")
    need(all(e["status"] == ("PASS" if e["test"] == c["reference_test"] else "OK") for e in run["ends"]), "file completion/reference")
    runs[phase] = {(r["test"],r["subtest"]):r for r in run["rows"]}
old,new = runs["baseline"],runs["candidate"]
need(old.keys() == new.keys(), "paired roster")
repaired=[]
for key,a in old.items():
    b=new[key]
    if a["status"] == "PASS": need(b["status"] == "PASS", "lost pass")
    elif b["status"] == "FAIL": need(all(a.get(k) == b.get(k) for k in ("status","message","expected","known_intermittent")), "changed failure")
    else: repaired.append(list(key))
main=next(iter(c["expected_subtests"]))
need(len(repaired) == 4 and all(k[0] == main for k in repaired) and all(r["status"] == "PASS" for k,r in new.items() if k[0] == main), "repair roster")
comparison=read("COMPARISON.json")
need(comparison["repaired"] == repaired and not comparison["regressions"] and not comparison["changed_failures"], "comparison receipt")
for name,base in (("DRAFT-FILES.json",HERE),("REFERENCES.json",ROOT)):
    for n,h in read(name).items(): need(sha(base / n) == h, "frozen input " + n)
staged=len(git("diff","--cached","--name-only","-z").split(b"\0"))-1
need(staged == 925,"staged roster")
receipt=dict(status="CENTRAL_COMPARISON_PASS_RESTORATION_VERIFIED",state_sha256=sha(HERE/"STATE.json"),final_sha256=sha(HERE/"FINAL.json"),draft_sha256=sha(HERE/"DRAFT-FILES.json"),head=c["head"],staged_paths=staged,source_guards=len(c["guard_sources"]),saved_source_bodies=len(c["sources"]),existing_tests=len(c["existing_tests"]),resource_guards=len(resources),candidate_paths=len(c["candidate_sources"]),subtests={phase:s["phases"][phase]["subtests"] for phase in runs},repaired=4,regressions=0,changed_retained_failures=0,reference_pass_both=True,restored_binary_pins=s["restored_binary_pins"],restored=True,restore_build_exit=s["restore_build_exit"],new_accepted_fixes=0,native_range_obligation_open=True)
(HERE/"ROOT-FINAL-CHECK.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
