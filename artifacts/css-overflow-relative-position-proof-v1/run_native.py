#!/usr/bin/env python3
from pathlib import Path
import itertools
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
CLANG = "/usr/bin/clang++"

def physical(w, extent, logical):
    v, lr, rev = w
    i, b = logical
    x, y = extent
    return ((b if lr else x-b), (y-i if rev else i)) if v else ((x-i if rev else i), b)

def logical(w, extent, point):
    v, lr, rev = w
    x, y = point
    cx, cy = extent
    return ((cy-y if rev else y), (x if lr else cx-x)) if v else ((cx-x if rev else x), y)

def oracle(a, before=False):
    w = a[:3]
    c, previous_size, previous_used = a[3:5], a[5:7], a[7:9]
    present, previous_normal, size, offset, style = a[9], a[10:12], a[12:14], a[14:16], a[16]
    previous_position = previous_normal if not before and style == 1 and present else previous_used
    previous_extent = [x-y for x,y in zip(c,previous_size)]
    i = logical(w, previous_extent, previous_position)[0]
    extent = [x-y for x,y in zip(c,size)]
    normal = physical(w,extent,(i,0))
    if style != 1:
        return [[*normal,*size,0,0,0,1]]
    if before:
        return [[*normal,*size,0,0,0,1]] + [
            [*(x+k*y for x,y in zip(normal,offset)),*size,1,*normal,1] for k in [2,0]]
    return [[*(x+k*y for x,y in zip(normal,offset)),*size,1,*normal,1] for k in [1,2,0]]

def main():
    subprocess.run(["python3",str(ROOT/"build_native.py")],check=True)
    modes=[(0,0,0),(0,0,1),(1,0,0),(1,0,1),(1,1,0),(1,1,1)]
    cases=[]
    for wm,style,present,offset,size in itertools.product(modes,range(3),[0,1],[(0,0),(1020,-1020),(-1020,1020)],[(6000,4800),(9000,0)]):
        cases.append([*wm,9600,12000,6000,4800,1020,-1020,present,0,0,*size,*offset,style])
    generated=(ROOT/"native-generated.cpp").read_text()
    variants={
      "candidate":generated,
      "used-inline":generated.replace("prevInFlow->GetLogicalNormalPosition(wm, containerSize).I(wm)","prevInFlow->IStart(wm, containerSize)"),
      "missing-apply":generated.replace("isRelative ? aFlags | ReflowChildFlags::ApplyRelativePositioning\n                     : aFlags", "aFlags"),
      "used-cache-update":generated.replace("nsPoint normalPosition = cont->GetNormalPosition(&hasProperty);", "nsPoint normalPosition = cont->GetNormalPosition(&hasProperty);\n        normalPosition = cont->GetPosition();"),
      "ignore-returned-size":generated.replace("const LogicalSize convertedSize = aDesiredSize.Size(aWM);", "const LogicalSize convertedSize{nsSize{6000,4800}};"),
    }
    before = (ROOT/"native-before-generated.cpp").read_text()
    variants["before"] = before
    assert all(value != generated for name,value in variants.items() if name != "candidate")
    report={"cases":len(cases),"candidate":[],"mutants":[],"boundary_failures":[]}
    with tempfile.TemporaryDirectory(prefix="css-relative-native-") as name:
        work=Path(name)
        for opt in ["O0","O2"]:
            for variant,body in variants.items():
                source=work/(variant+".cpp");source.write_text(body)
                exe=work/(variant+opt)
                build=subprocess.run([CLANG,"-std=c++17","-"+opt,"-fsanitize=undefined","-fno-sanitize-recover=all",str(source),"-o",str(exe)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                assert build.returncode==0,build.stdout
                tested=0
                witness=None
                for a in cases:
                    result=subprocess.run([str(exe),*map(str,a)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    assert result.returncode==0,(variant,a,result.stderr)
                    actual=[list(map(int,line.split())) for line in result.stdout.splitlines()]
                    expected=oracle(a, variant == "before");tested+=1
                    if actual != expected:
                        witness={"input":a,"expected":expected,"actual":actual}
                        break
                if variant in ["candidate", "before"]:
                    assert witness is None,(opt,witness)
                    report["candidate"].append({"variant":variant,"optimization":opt,"rows":tested,"all_match":True,"build_log":build.stdout})
                else:
                    assert witness is not None,variant
                    report["mutants"].append({"optimization":opt,"variant":variant,"tested_before_witness":tested,"witness":witness,"build_log":build.stdout})
                if variant in ["candidate", "before"]:
                    a = [0,0,1,2147483647,100,1,1,-1,0,1,-1,0,1,1,0,0,1]
                    result=subprocess.run([str(exe),*map(str,a)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    assert result.returncode != 0 and "signed integer overflow" in result.stderr
                    report["boundary_failures"].append({"variant":variant,"optimization":opt,"input":a,
                        "reason":"IEnd adds logical start+size before subtraction; abstract final position fits",
                        "exit":result.returncode,"output":result.stderr})
    report["temporary_products_removed"]=True
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
