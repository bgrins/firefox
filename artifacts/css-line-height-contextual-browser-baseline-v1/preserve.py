import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS="0")
read=lambda p:json.loads(p.read_bytes())
def digest(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def save(name,value):
    with (HERE/name).open("x") as f:json.dump(value,f,indent=2,sort_keys=True);f.write("\n")
spec=importlib.util.spec_from_file_location("preserve",ROOT/"artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
signing=ROOT/"artifacts/css-local-signing-20261028-v33"
epoch=read(signing/"INITIAL-EPOCH.json")
selection=read(signing/"random-selection.json")
index=h.index_state(ROOT,ENV)
assert index["head"]==epoch["semantic_index"]["head"]=="b04304be4b2083686920e8b3788e8e7614d26496"
assert index["working_diff"]==epoch["semantic_index"]["working_diff"]
assert h.git(ROOT,ENV,"diff","--cached","--binary","--full-index",index["head"])==(signing/"random-staged.patch").read_bytes()
selected=set(selection["files"])
assert len(selected)==165
assert set(h.git(ROOT,ENV,"diff","--cached","--name-only").decode().splitlines())==selected
prior_entries=b"".join(r+b"\0" for r in h.git(ROOT,ENV,"ls-files","--stage","-z").split(b"\0") if r and r.split(b"\t",1)[1].decode() not in selected)
assert hashlib.sha256(prior_entries).hexdigest()==epoch["semantic_index"]["entries"]
for name in ("pins","staged_working","committed_research_working_payloads"):
    assert {n:h.fingerprint(ROOT,n) for n in epoch[name]}==epoch[name],name
assert all(digest(ROOT/n)==v for n,v in selection["source_pins"].items())
for n,identity in epoch["installed_identities"].items():
    s=(ROOT/n).lstat();assert stat.S_ISREG(s.st_mode) and [s.st_dev,s.st_ino]==identity
assert h.git(ROOT,ENV,"diff","--name-only").decode().splitlines()==epoch["modified_native_paths"]
untracked=set(h.git(ROOT,ENV,"ls-files","--others","--exclude-standard","--","layout","dom","servo","mfbt").decode().splitlines())
assert untracked==set(epoch["untracked_native"])
nested=h.index_state(ROOT/"artifacts/css-spec-lean",ENV)
assert h.semantic_index(nested)==epoch["nested_semantic_index"]
controls={n:digest(ROOT/"artifacts/css-registered-number-native-runtime-v1"/n) for n in ["CURRENT-EPOCH.json","OWNED.json","ROLE.json"]}
assert all(digest(signing/("PRE-"+n))==v for n,v in controls.items())
inputs=read(HERE/"INPUTS.json")
assert all(digest(ROOT/n)==v for n,v in inputs["source_pins"].items())
base=read(ROOT/"artifacts/css-line-height-contextual-number-repair-v1/SOURCE-ROLES.json")
assert all(digest(ROOT/n)==v["base_sha256"] for n,v in base.items())
binaries=read(ROOT/"artifacts/css-random-ordinary-observation-v1/BINARY-PRE.json")
for n,v in binaries.items():
    p=ROOT/n;s=p.stat();ls=p.lstat()
    assert digest(p)==v["sha256"] and [s.st_dev,s.st_ino]==v["identity"] and [ls.st_dev,ls.st_ino]==v["entry_identity"]
assert h.index_state(ROOT,ENV)==index and h.index_state(ROOT/"artifacts/css-spec-lean",ENV)==nested
snapshot={"index":index,"nested_index":nested,"controls":controls,"binary_pins":binaries,"source_pins":inputs["source_pins"],"staged_selection_sha256":digest(signing/"random-selection.json"),"fixture_sha256":digest(HERE/"observed.html"),"preserved_full_epoch_payloads":True,"native_candidate_applied":False}
mode=sys.argv[1]
if mode=="pre":save("PRE.json",snapshot)
elif mode=="post":
    assert snapshot==read(HERE/"PRE.json")
    save("POST.json",snapshot)
else:raise ValueError(mode)
print("Full source/binary/research and exact staged165 preservation verified",mode,flush=True)
