#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile,sys,shutil
ROOT=Path(__file__).resolve().parent
ALLOWED={"propext","Quot.sound","Classical.choice"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,cwd):return subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
def audit(output,expected):
    sets=re.findall(r"depends on axioms: \[([^\]]*)\]",output,re.S)
    count=len(sets)+output.count("does not depend on any axioms")
    assert count==expected,(count,output)
    for names in sets:assert {n.strip() for n in names.split(",") if n.strip()}<=ALLOWED
    return count

def main():
    tools=json.loads((ROOT/"TOOLS.json").read_text())
    for value in tools.values():assert sha(Path(value["path"]))==value["sha256"]
    lean=tools["lean"]["path"]
    for row in json.loads((ROOT/"SOURCES.json").read_text()):
        assert sha(ROOT/row["snapshot"])==row["sha256"]
    providers=json.loads((ROOT/"ADDITIONAL-PROVIDERS.json").read_text())
    for row in providers:assert sha(ROOT/row["snapshot"])==row["sha256"]
    expected_generated={name:sha(ROOT/name) for name in ["native-generated.cpp","native-before-generated.cpp","EXTRACTIONS.json"]}
    result=run([sys.executable,str(ROOT/"build_native.py")],ROOT);assert result.returncode==0,result.stdout
    assert expected_generated=={name:sha(ROOT/name) for name in expected_generated},"source generation drift"
    result=run([sys.executable,str(ROOT/"recount_runtime.py")],ROOT);assert result.returncode==0,result.stdout
    report={"runtime_recount":json.loads(result.stdout),"kernel":[],"false_claims":[],"axiom_guards":[]}
    with tempfile.TemporaryDirectory(prefix="css-relative-kernel-") as name:
        work=Path(name)
        for filename,count in [("RelativeOverflow.lean",12),("SourceGeometry.lean",21)]:
            shutil.copyfile(ROOT/filename,work/filename)
            result=run([lean,filename],work);assert result.returncode==0,result.stdout
            report["kernel"].append({"module":filename,"audits":audit(result.stdout,count),"output":result.stdout})
        source=(ROOT/"SourceGeometry.lean").read_text()
        fixture="\ndef p0 : SourceGeometry.P := ⟨0,0⟩\ndef f0 : SourceGeometry.Frame := ⟨⟨10,10⟩,p0,some p0⟩\ndef wm0 : SourceGeometry.WM := ⟨false,false,false⟩\n"
        claims=[
            "example : (SourceGeometry.sourceHelper wm0 ⟨100,100⟩ ⟨10,10⟩ ⟨0,17⟩ f0 f0).position.y = 0 := by decide",
            "example : (SourceGeometry.sourceHelper wm0 ⟨100,100⟩ ⟨20,30⟩ p0 f0 f0).size.x = 10 := by decide",
            "example : (SourceGeometry.sourceUpdate ⟨34,0⟩ (SourceGeometry.sourceHelper wm0 ⟨100,100⟩ ⟨10,10⟩ ⟨17,0⟩ f0 f0)).position.x = 51 := by decide",
            "example : (2147483647 + 1 : Int) ≤ 2147483647 := by decide",
        ]
        for i,claim in enumerate(claims):
            f=work/f"False{i}.lean";f.write_text(source+fixture+claim+"\n")
            result=run([lean,str(f)],work);assert result.returncode!=0 and "error:" in result.stdout
            report["false_claims"].append({"claim":claim,"exit":result.returncode,"output":result.stdout})
        for name,body,forbidden in [("injected","axiom injected : False\ntheorem bad : False := injected","injected"),("sorry","theorem bad : False := by sorry","sorryAx")]:
            f=work/(name+".lean");f.write_text("import Lean\n"+body+"\n#print axioms bad\n")
            result=run([lean,str(f)],work);assert result.returncode==0 and forbidden in result.stdout
            sets=re.findall(r"depends on axioms: \[([^\]]*)\]",result.stdout,re.S)
            assert sets and not {n.strip() for n in sets[0].split(",") if n.strip()}<=ALLOWED
            report["axiom_guards"].append({"forbidden":forbidden,"output":result.stdout})
        target=work/"layout/generic/nsContainerFrame.cpp";target.parent.mkdir(parents=True)
        target.write_bytes((ROOT/"sources/nsContainerFrame.cpp").read_bytes())
        for reverse in [False,True]:
            args=["git","apply","--unsafe-paths"]+(["--reverse"] if reverse else [])+[str(ROOT/"proposal.patch")]
            result=run(args,work);assert result.returncode==0,result.stdout
            expected=ROOT/("sources/nsContainerFrame.cpp" if reverse else "candidate-nsContainerFrame.cpp")
            assert target.read_bytes()==expected.read_bytes()
        html=(ROOT/"relative-position-overflow-continuations.html").read_text()
        script=html[html.index("<script>\n")+9:html.rindex("</script>")]
        js=work/"wpt.js";js.write_text(script)
        result=run(["node","--check",str(js)],work);assert result.returncode==0,result.stdout
    result=run([sys.executable,str(ROOT/"run_native.py")],ROOT);assert result.returncode==0,result.stdout
    report["native"]=json.loads(result.stdout)
    report["source_generation_stable"]=True
    report["standalone_apply_reverse"]=True
    report["temporary_products_removed"]=True
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
