import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S")
import argparse, hashlib, json, stat, subprocess, tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
read=lambda p:json.loads(p.read_text())
def need(ok,msg):
    if not ok: raise RuntimeError(msg)
need(sha((here/"FILES.json").read_bytes())==a.manifest_sha,"Manifest pin")
m=read(here/"FILES.json");actual=set()
for p in here.rglob("*"):
    mode=p.lstat().st_mode
    if stat.S_ISDIR(mode): continue
    need(stat.S_ISREG(mode),"Nonregular entry")
    actual.add(p.relative_to(here).as_posix())
need(actual==set(m)|{"FILES.json","FREEZE.json"},"Closed roster")
for name,pin in m.items(): need(sha((here/name).read_bytes())==pin,"Payload hash")
b=read(here/"BINDINGS.json")
need(sha((root/"artifacts/css-hidden-layout-column-runtime-v1/INPUTS.json").read_bytes())==b["runtime_INPUTS_sha256"],"Runtime input")
need(sha((root/"artifacts/css-hidden-layout-native-packaging-v1/FILES.json").read_bytes())==b["native_package_FILES_sha256"],"Native package")
for e in b["bindings"]:
    before=(root/e["before_source"]).read_bytes()
    need(sha(before)==e["before_sha256"] and blob(before)==e["before_blob"],"Original")
    with tempfile.TemporaryDirectory(prefix="hidden-overlay-") as temp:
        work=Path(temp);target=work/e["path"];target.parent.mkdir(parents=True);target.write_bytes(before)
        patch=here/(e["kind"]+"-worktree.patch")
        r=subprocess.run(["/usr/bin/patch","-p1","--batch","--fuzz=0","-i",str(patch)],cwd=work,capture_output=True)
        need(r.returncode==0,"Apply")
        after=target.read_bytes();need(sha(after)==e["after_sha256"] and blob(after)==e["after_blob"],"Overlay final")
        r=subprocess.run(["/usr/bin/patch","-R","-p1","--batch","--fuzz=0","-i",str(patch)],cwd=work,capture_output=True)
        need(r.returncode==0 and target.read_bytes()==before,"Exact reverse")
review=read(here/"REVIEWER.json")
for path,pin in review["external_pins"].items(): need(sha((root/path).read_bytes())==pin,"Reviewer source pin")
need("Herald reviewers (automatically added):\n  #layout-reviewers" in (here/"reviewers-fresh.log").read_text(),"Herald group")
print("PASS: exact private overlay apply/reverse, original prototype preservation, distinct clean-stage/worktree roles and reviewer evidence")
