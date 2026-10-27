import hashlib,json,os,stat,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
GROUPS={
 "quote-research": (["css-quote-scope-append-acceptance-v1","css-quote-ordered-scopes-model-v1","css-quote-ordered-scopes-model-review-v1","css-quote-scope-append-admission-v1","css-quote-scope-append-admission-v2","css-quote-scope-append-coc-execution-v1","css-quote-scope-append-coc-execution-v2","css-quote-scope-append-coc-index-review-v2","css-quote-scope-append-coc-review-v1","css-quote-scope-append-coc-runtime-v1","css-quote-scope-append-coc-runtime-v2","css-quote-scope-append-coc-terminal-review-v2"],"No bug - Record contained-quote append comparison and ordered-scope proof. r?#layout-reviewers"),
 "animation-research": (["css-keyframe-provider-computation-inputs-v1","css-keyframe-active-provider-refresh-hook-audit-v1"],"No bug - Record animated-provider input and refresh constraints. r?#firefox-style-system-reviewers"),
 "followup-research": (["css-counter-scope-append-adjacent-audit-v1","css-quote-provider-freshness-audit-v1"],"No bug - Record counter scope and quote language invalidation investigations. r?#layout-reviewers"),
}
name=sys.argv[1]
if name=="quote-fix":
 files=["layout/base/nsQuoteList.cpp","layout/base/nsQuoteList.h","testing/web-platform/tests/css/css-contain/quote-scoping-append-invalidation.html"]
 message="No bug - Recalculate contained quotes after appending a parent quote. r?#layout-reviewers"
else:
 directories,message=GROUPS[name];files=[]
 for n in directories:
  p=ROOT/"artifacts"/n;assert p.is_dir(),n
  for q in sorted(p.rglob("*")):
   assert not q.is_symlink(),q
   if q.is_file():
    assert not any(x in q.parts for x in ["__pycache__",".git",".lake"]),q
    assert q.stat().st_size<20_000_000,(q,q.stat().st_size)
    files.append(str(q.relative_to(ROOT)))
tracked=set(subprocess.check_output(["git","--no-optional-locks","-c","core.fsmonitor=false","ls-files","-z"],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS="0")).decode().split("\0"))
if name!="quote-fix": assert not set(files)&tracked,"Research must be new, sealed artifact files"
item={"id":name,"files":sorted(files),"message":message,"source_pins":{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files},"source_modes":{n:"100755" if (ROOT/n).stat().st_mode&stat.S_IXUSR else "100644" for n in files}}
if name=="quote-fix":
 item["patch"]="artifacts/css-quote-scope-append-fix-v1/fix-candidate-v1.patch"
 item["patch_sha256"]=hashlib.sha256((ROOT/item["patch"]).read_bytes()).hexdigest()
with (HERE/(name+"-plan.json")).open("x") as f:json.dump(item,f,indent=2,sort_keys=True);f.write("\n")
print(name,len(files),sum((ROOT/n).stat().st_size for n in files))
