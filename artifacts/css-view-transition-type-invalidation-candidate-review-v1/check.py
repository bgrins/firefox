import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use python3 -I -S, without optimization")
from pathlib import Path
import hashlib, json, stat
root = Path(__file__).resolve().parent
hash_bytes = lambda data: hashlib.sha256(data).hexdigest()
def regular(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise RuntimeError("not regular: " + str(path))
for name in ("FILES.json", "FREEZE.json"):
    regular(root / name)
freeze = json.loads((root / "FREEZE.json").read_text())
if hash_bytes((root / "FILES.json").read_bytes()) != freeze["files_sha256"]:
    raise RuntimeError("manifest mismatch")
if hash_bytes(Path(__file__).read_bytes()) != freeze["checker_sha256"]:
    raise RuntimeError("checker mismatch")
files = json.loads((root / "FILES.json").read_text())
expected = set(files) | {"FILES.json", "FREEZE.json"}
dirs = set()
for name in files:
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or str(p) != name:
        raise RuntimeError("unsafe path")
    dirs.update(str(parent) for parent in p.parents if str(parent) != ".")
actual = set()
def walk(directory):
    for p in directory.iterdir():
        name = str(p.relative_to(root))
        mode = p.lstat().st_mode
        if stat.S_ISDIR(mode):
            if name not in dirs:
                raise RuntimeError("extra directory: " + name)
            walk(p)
        elif stat.S_ISREG(mode):
            actual.add(name)
        else:
            raise RuntimeError("nonregular entry: " + name)
walk(root)
if actual != expected:
    raise RuntimeError("roster mismatch")
for name, digest in files.items():
    if hash_bytes((root / name).read_bytes()) != digest:
        raise RuntimeError("input mismatch: " + name)

def require(ok, message):
    if not ok: raise RuntimeError(message)

def load(name): return json.loads((root/name).read_text())

pairs=[]
for phase in ["baseline","candidate-results"]:
    run=load(phase+"/RUN.json")
    require(run["before"]==run["after"] and len(run["before"])==43,"unstable pins")
    raw=[json.loads(line) for line in (root/phase/"raw.json").read_text().splitlines()]
    rows=[x for x in raw if x["action"]=="test_status"]
    ends=[x for x in raw if x["action"]=="test_end"]
    table={(x["test"],x["subtest"]):{k:x.get(k) for k in ["status","expected","message"]} for x in rows}
    require(len(table)==len(rows)==42,"row count or duplicate")
    require(len(ends)==3 and all(x["status"]=="OK" for x in ends),"harness status")
    require(sum(x["action"]=="suite_end" for x in raw)==1,"suite end")
    pairs.append((run,table))
b,c=pairs
require(b[1].keys()==c[1].keys(),"paired roster")
changes=[k for k in b[1] if b[1][k]!=c[1][k]]
require(len(changes)==6 and all(b[1][k]["status"]=="FAIL" and c[1][k]["status"]=="PASS" for k in changes),"unexpected changes")
require(all(x["status"]=="PASS" for x in c[1].values()),"candidate failures")
changed_pins={k for k in b[0]["before"] if b[0]["before"][k]!=c[0]["before"][k]}
native={"dom/view-transitions/ViewTransition.cpp","dom/view-transitions/ViewTransition.h","dom/view-transitions/ViewTransitionTypeSet.cpp"}
binaries={"objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox","objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL"}
require(changed_pins==native|binaries,"unexpected source change")
final=load("FINAL-SOURCE-v2.json")
require(hash_bytes((root/"fix-candidate-v2.patch").read_bytes())==final["patch_sha256"],"patch mismatch")
for name,digest in final["pins"].items():
    local=root/("formatted/"+name.replace("/","__") if name in native else "wpt-v2.html")
    require(hash_bytes(local.read_bytes())==digest==c[0]["before"][name],"final input mismatch")
build=load("BUILD-v1.json");require(build["terminal_exit"]==0,"build failure")
require(hash_bytes((root/"build-v1.log").read_bytes())==build["log_sha256"],"build log")
require(build["native_pins"]=={k:final["pins"][k] for k in native},"build sources")
gates=load("NATIVE-GATES-v1.json")
for kind in ["native","wpt"]:
    require(gates[kind+"_lint_exit"]==0,"lint failure")
    require(hash_bytes((root/(kind+"-lint-v1.log")).read_bytes())==gates[kind+"_lint_log_sha256"],"lint log")
for label in ["integration","standalone"]:
    p=load("PACKAGING.json")[label]
    require(p["exact_apply_reverse"] and p["pins"]==final["pins"] and p["sha256"]==final["patch_sha256"],"packaging mismatch")
print(json.dumps({"status":"PASS","inputs":len(files),"paired_rows":42,"improvements":6,"unchanged":36,"candidate_harness_OK":3,"scope":"retained native/WPT evidence and source review; no isolated upstream runtime"}))
