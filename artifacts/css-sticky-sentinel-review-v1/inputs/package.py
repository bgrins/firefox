import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
NATIVE="layout/generic/StickyScrollContainer.cpp"
TEST="testing/web-platform/tests/css/css-position/sticky/position-sticky-auto-insets-large-coordinate.html"
PATCH=OUT/"fix-candidate-v1.patch"
GIT=["git","-c","core.fsmonitor=false"]
def get(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT)
def sha(data):return hashlib.sha256(data).hexdigest()
def body(data):
    s=data.decode();a=s.index("nsPoint StickyScrollContainer::DoComputePosition(");b=s.index("\nnsPoint StickyScrollContainer::ComputeTranslationIgnoringScrolling",a)
    return s[a:b]
head=get("rev-parse","HEAD").decode().strip()
index=get("diff","--cached","--raw")
working={p:sha((ROOT/p).read_bytes()) for p in [NATIVE,TEST]}
expected_body=body((OUT/"candidate.cpp").read_bytes())
records=[]
for base in [head,"976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    before=get("show",base+":"+NATIVE)
    assert subprocess.run(GIT+["cat-file","-e",base+":"+TEST],cwd=ROOT,stderr=subprocess.DEVNULL).returncode!=0
    with tempfile.TemporaryDirectory(prefix="sticky-sentinel-apply-") as tmp:
        tmp=Path(tmp);path=tmp/NATIVE;path.parent.mkdir(parents=True);path.write_bytes(before)
        for args in [["apply","--check",str(PATCH)],["apply",str(PATCH)]]:subprocess.run(GIT+args,cwd=tmp,check=True)
        after=path.read_bytes();assert body(after)==expected_body
        assert after.decode().replace(expected_body,body(before),1).encode()==before
        assert (tmp/TEST).read_bytes()==(ROOT/TEST).read_bytes()
        assert {str(x.relative_to(tmp)) for x in tmp.rglob("*") if x.is_file()}=={NATIVE,TEST}
        subprocess.run(GIT+["apply","--reverse",str(PATCH)],cwd=tmp,check=True)
        assert path.read_bytes()==before and not (tmp/TEST).exists()
        records.append({"base":base,"before_sha256":sha(before),"after_sha256":sha(after),"exact_body":True,"other_native_bytes_preserved":True,"exact_WPT":True,"reversed_exactly":True})
assert get("rev-parse","HEAD").decode().strip()==head and get("diff","--cached","--raw")==index
assert {p:sha((ROOT/p).read_bytes()) for p in working}==working
(OUT/"PACKAGING.json").write_text(json.dumps({"patch_sha256":sha(PATCH.read_bytes()),"paths":[NATIVE,TEST],"checks":records,"real_head_index_worktree_preserved":True,"isolated_build":False},indent=2)+"\n")
print(json.dumps({"bases":len(records),"paths":2,"exact_apply_reverse":True}))
