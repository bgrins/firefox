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

def expected(alpha, beta, active, pseudo):
    out = dict(alpha=alpha, beta=beta, active=active, childMatches=False,
        color="rgb(0, 0, 255)" if beta else "rgb(0, 128, 0)" if alpha else "rgb(10, 20, 30)",
        width="61px" if beta else "43px" if alpha else "17px")
    if pseudo:
        out.update(rootBefore="0.8" if alpha else "0.2",
            childBefore="0.75" if alpha else "0.25",
            groupOpacity="0.7" if alpha else "0.3", groupAnimationDuration="100s")
    return out

def require(condition, message):
    if not condition: raise RuntimeError(message)

def check_rows(prefix, pseudo):
    raw=json.loads((root/"evidence"/(prefix+"raw.json")).read_text())
    run=json.loads((root/"evidence"/(prefix+"RUN.json")).read_text())
    require(raw["complete"] and run["complete"] and run["pins_before"]==run["pins_after"], "runtime incomplete or unstable")
    operations=["add","delete","clear","add-existing","delete-missing","clear-empty"]
    labels=[p+"/"+op for p in (["ready"] if pseudo else ["synchronous","ready"]) for op in operations]
    if not pseudo: labels += [p+"/"+op for p,ops in [("completed",["clear","add","delete"]),("old-during-new",["add","delete","clear"])] for op in ops]
    require([x["label"] for x in raw["rows"]]==labels,"case roster")
    fails=[]
    for row in raw["rows"]:
        phase,op=row["label"].split("/")
        alpha=phase in ("ready","synchronous") and op in ("add","add-existing")
        oldalpha=phase in ("ready","synchronous") and op in ("delete","clear","add-existing")
        beta=phase=="old-during-new";active=phase!="completed"
        before=expected(oldalpha,beta,active,pseudo);after=expected(alpha,beta,active,pseudo)
        for k,v in before.items(): require(row["before"][k]==v,"before calibration: "+row["label"]+"/"+k)
        for k,v in after.items(): require(row["refreshed"][k]==v,"refresh calibration: "+row["label"]+"/"+k)
        differences=[k for k,v in after.items() if row["actual"][k]!=v]
        changed=phase in ("synchronous","ready") and op in ("add","delete","clear")
        wanted=["color","width"]+(["rootBefore","childBefore","groupOpacity"] if pseudo else []) if changed else []
        require(differences==wanted,"unexpected runtime difference: "+row["label"])
        if differences: fails.append(row["label"])
        if phase in ("synchronous","ready"):
            require(row["operation"]["types"]==(["alpha"] if alpha else []),"public membership")
            require(row["operation"]["activeIdentity"],"owner identity")
        if pseudo:
            require(row["actual"]["groupAnimationName"]=="-ua-view-transition-group-anim-root","group animation")
            require(any(a["name"]=="-ua-view-transition-group-anim-root" and a["state"]=="running" and a["pseudo"]=="::view-transition-group(root)" for a in row["operation"]["animations"]),"group animation not running")
    return {"rows":len(labels),"discrepancies":len(fails),"passing":len(labels)-len(fails)}

anchors={"view-transitions-2.html":["viewtransitiontypeset","dom-viewtransition-types","the-active-view-transition-type-pseudo"],"webidl.html":["es-set-add","es-set-delete","es-set-clear"],"cssom.html":["dom-window-getcomputedstyle"]}
for name,ids in anchors.items():
    source=(root/"spec"/name).read_text()
    for identity in ids: require('id="'+identity+'"' in source,"missing spec anchor")
print(json.dumps({"integrity":"PASS","inputs":len(files),"ordinary":check_rows("",False),"pseudos":check_rows("pseudos-",True),"scope":"retained baseline and source proposal; no candidate execution"}))
