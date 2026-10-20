import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("require Python -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CPP="layout/generic/StickyScrollContainer.cpp"
HEADER="layout/generic/StickyScrollContainer.h"
WPT="testing/web-platform/tests/css/css-position/sticky/position-sticky-large-negative-insets.html"
BASES=["92a6fddf18e5828b17d7491a34663a0d5a9c12ad","976279105b2e78b8666a959eb3f25c9176cefaf8"]
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def sections(patch):
    lines=patch.splitlines(True);result=[];i=0
    while i<len(lines):
        require(lines[i].startswith("--- "),"patch old path")
        old=lines[i][4:].strip();new=lines[i+1][4:].strip();i+=2;hunks=[]
        require(new.startswith("b/"),"patch new path")
        while i<len(lines) and not lines[i].startswith("--- "):
            m=re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n",lines[i]);require(m is not None,"patch hunk")
            start=int(m[1]);i+=1;before=[];after=[]
            while i<len(lines) and not lines[i].startswith(("@@ ","--- ")):
                line=lines[i];require(line[0] in " +-","patch line")
                if line[0] in " -":before.append(line[1:])
                if line[0] in " +":after.append(line[1:])
                i+=1
            require(len(before)==int(m[2] or 1) and len(after)==int(m[4] or 1),"hunk sizes")
            hunks.append((start,before,after))
        result.append((old,new[2:],hunks))
    return result
def apply(source,hunks):
    lines=source.splitlines(True);cursor=0;result=[];reverse=[]
    for start,before,after in hunks:
        pos=max(0,start-1);require(pos>=cursor and lines[pos:pos+len(before)]==before,"exact patch context")
        result+=lines[cursor:pos];reverse.append((len(result)+1,after,before));result+=after;cursor=pos+len(before)
    result+=lines[cursor:];return "".join(result),reverse
def run_receipt(folder):
    data=read(folder/"RUN.json");raw=[json.loads(line) for line in (folder/"raw.json").read_text().splitlines()]
    require(data["complete"] is True and data["status"]=="done","terminal receipt")
    require(data["stable_pins"] is True and data["before"]==data["after"],"stable source pins")
    require(data["rows"]==[x for x in raw if x["action"]=="test_status"],"raw subtests")
    require(data["harness"]==[x for x in raw if x["action"]=="test_end"],"raw harnesses")
    for name,digest in data["before"].items():
        p=folder/"inputs"/name
        if name.startswith("objdir-"):continue
        require((not p.exists()) if digest is None else p.is_file() and sha(p)==digest,"retained input "+name)
    for row in data["rows"]+data["harness"]:
        require(not row.get("known_intermittent"),"intermittent status")
    return data
def audit():
    root=ROOT/"native";patch=root/"fix-candidate-v1.patch"
    require(sha(patch)=="68c14d1d2b0fdb2fad21efc9e670a6ddcdf40740c1e84230225f7bae57251484","exact patch")
    changes=sections(patch.read_text());require([x[1] for x in changes]==[CPP,HEADER,WPT],"exact three paths")
    packaging=read(root/"PACKAGING.json");base_rows=[]
    for base in BASES:
        for old,name,hunks in changes:
            source="" if old=="/dev/null" else (ROOT/"bases"/(base+"-"+Path(name).name)).read_text()
            result,reverse=apply(source,hunks);original,_=apply(result,reverse);require(original==source,"patch reverse")
            expected=(root/"wpt-v1.html").read_text() if name==WPT else (root/("standalone-"+Path(name).name)).read_text()
            require(result==expected,"standalone result")
        base_rows.append({"base":base,"exact_apply_reverse":True})
    expected_cpp="0e3b5f3e85e41a9e65164c489acfba58d12634e9a6658df71dcd3bf141ab4096"
    require(sha(root/"combined-final-StickyScrollContainer.cpp")==expected_cpp,"combined final")
    require((root/"candidate-v2-StickyScrollContainer.cpp").read_bytes()==(root/"combined-final-StickyScrollContainer.cpp").read_bytes(),"final candidate identity")
    require(sha(root/"combined-final-StickyScrollContainer.h")=="e4c44b8a11a2b474d3d03f3c4d4628e63ee60570d5be4ee373b63d1be831722e","final header")
    before=run_receipt(root/"baseline-wpt-v1");after=run_receipt(root/"candidate-wpt-v1")
    for run,source in [(before,"before"),(after,"combined-final")]:
        for name in [CPP,HEADER]:require(run["before"][name]==sha(root/(source+"-"+Path(name).name)),"tested source identity")
        require(run["before"][WPT]==sha(root/"wpt-v1.html"),"unchanged WPT")
        require(len(run["rows"])==60 and len(run["harness"])==1 and run["harness"][0]["status"]=="OK","paired dimensions")
    require(before["exit"]==1 and after["exit"]==0,"paired exits")
    delta={k:{"baseline":v,"candidate":after["before"][k]} for k,v in before["before"].items() if after["before"][k]!=v}
    require(set(delta)=={CPP,HEADER,"objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL","objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox"},"cross-run source changes")
    require(delta==read(root/"PAIRED-WPT.json")["pin_delta"],"delta receipt")
    pairs=[(-1000,-1000),(-1000000,-1000000),(-10000000,-10000000),(-17895600,-17895600),(-17895696,-17895696),(-17895697,-17895697),(-17895698,-17895698),(-1000000000,-1000000000),(-1000000000,-1000),(-1000,-1000000000)]
    old={x["subtest"]:x for x in before["rows"]};new={x["subtest"]:x for x in after["rows"]};expected_names=set();improvements=0
    for axis in ["vertical","horizontal"]:
        for near,far in pairs:
            for scroll in [0,100,400]:
                name=f"{axis}: insets {near}/{far}px, scroll {scroll}px";expected_names.add(name)
                fail=near==far and near<=-17895696
                require(old[name]["status"]==("FAIL" if fail else "PASS") and new[name]["status"]=="PASS","independent case classification")
                if fail:
                    expected=200-scroll;actual=-scroll
                    message=f"assert_approx_equals: Sticky target keeps its normal position expected {expected} +/- 0.1 but got {actual}"
                    require(old[name]["message"]==message,"final oracle failure")
                    improvements+=1
                else:require(old[name].get("message")==new[name].get("message"),"control message")
    require(set(old)==set(new)==expected_names and improvements==24,"exact case roster")
    regress=run_receipt(root/"regressions-wpt-v1")
    require(regress["exit"]==0 and len(regress["rows"])==1408 and all(x["status"]=="PASS" for x in regress["rows"]),"regression rows")
    require([x["status"] for x in regress["harness"]].count("PASS")==3 and all(x["status"] in ["PASS","OK"] for x in regress["harness"]),"regression harnesses")
    for name in [CPP,HEADER]:require(regress["before"][name]==after["before"][name],"regression source")
    build=read(root/"BUILD-v2.json");require(build["exit"]==0 and build["source_pins"]=={n:after["before"][n] for n in [CPP,HEADER]},"build source")
    standalone=run_receipt(root/"standalone-wpt-v1")
    require(standalone["exit"]==0 and len(standalone["rows"])==60 and all(x["status"]=="PASS" for x in standalone["rows"]),"standalone browser rows")
    require({x["subtest"] for x in standalone["rows"]}==expected_names,"standalone roster")
    require(len(standalone["harness"])==1 and standalone["harness"][0]["status"]=="OK","standalone harness")
    for name in [CPP,HEADER]:require(standalone["before"][name]==sha(root/("standalone-"+Path(name).name)),"standalone tested source")
    restored=read(root/"BUILD-restored-v1.json")
    require(restored["exit"]==0 and restored["combined_source_restored"] is True,"restored build")
    require(restored["log_sha256"]==sha(root/"build-restored-v1.log") and restored["standalone_wpt"]["sha256"]==sha(root/"standalone-wpt-v1/RUN.json"),"restoration receipts")
    require(restored["source_pins"]=={n:after["before"][n] for n in [CPP,HEADER]},"restored combined identity")
    probes=[]
    for role in ["release","candidate"]:
        d=read(ROOT/"probe"/role/"RESULT.json");require(d["stable"] and d["before"]==d["after"] and len(d["observations"])==1,"probe stability")
        obs=d["observations"][0];rows=obs["rows"];require(len(rows)==60,"probe rows")
        keys=set();failed=0
        for x in rows:
            near,far=x["insets"];scroll=x["requestedScroll"];key=(x["axis"],near,far,scroll);require(key not in keys,"duplicate probe");keys.add(key)
            for value in [x["sticky"],x["control"]]:
                require(value["actualScroll"]==scroll and value["client"]==100 and value["cbSize"]==1000 and value["targetSize"]==10,"probe geometry")
            require(x["sticky"]["computedPosition"]=="sticky" and x["control"]["computedPosition"]=="static","probe positioning")
            require(x["sticky"]["near"]!="auto" and x["sticky"]["far"]!="auto","explicit probe sides")
            fail=near==far and near<=-17895696
            require(x["control"]["position"]==200-scroll and x["sticky"]["position"]==(-scroll if fail else 200-scroll),"independent probe oracle")
            require(x["calibrated"] and x["matched"]==(not fail),"probe classification");failed+=fail
        require(failed==24,"probe failures");probes.append({"role":role,"rows":60,"failures":failed,"user_agent":obs["userAgent"]})
    return {"status":"pass","patch_sha256":sha(patch),"bases":base_rows,"standalone_browser_rows":60,"paired_rows":60,"improvements":24,"unchanged":36,"regression_rows":1408,"regression_reftests":3,"probes":probes}
if __name__=="__main__":print(json.dumps(audit(),indent=2))
