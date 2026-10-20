import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json,re,subprocess
from pathlib import Path

MUTANTS=["auto_reserved_too","maximum_instead_of_minimum","reserve_two_units","negative_values_lost","wrong_side"]
def write(p,v):p.write_text(json.dumps(v,indent=2)+"\n")
def require(c,s):
    if not c:raise RuntimeError(s)
def run(root,out,tool,core):
    transfer=json.loads((root/"TRANSFER-v1.json").read_text())
    for suffix,target in [("/lean/OffsetEncoding.lean","lean/OffsetEncoding.lean"),("/native-v3/CASES.json","CASES-v1.json")]:
        matches=[r for r in transfer if r["source"].endswith(suffix)]
        require(len(matches)==1 and core.sha((root/target).read_bytes())==matches[0]["sha256"],"v1 byte transfer")
    cases=json.loads((root/"CASES.json").read_text())
    require(cases==core.cases(),"complete case roster")
    require(cases[:216]==json.loads((root/"CASES-v1.json").read_text()),"historical case transfer")
    for c in cases:core.validate(c)
    require(core.native("candidate")[1]==json.loads((root/"BINDINGS.json").read_text()),"source bindings")
    require(core.provider()==json.loads((root/"PROVIDER.json").read_text()),"numeric provider binding")
    for b in json.loads((root/"BINDINGS.json").read_text())+[core.provider()]:
        require(core.sha((root/b["path"]).read_bytes()[b["start_byte"]:b["end_byte"]])==b["sha256"],"exact byte binding")
    negatives=[]
    for name,c,reason in core.negative_cases():
        try:core.validate(c)
        except ValueError as e:require(str(e)==reason,"negative reason");negatives.append({"id":name,"reason":reason})
        else:raise RuntimeError("invalid admitted: "+name)
    out.mkdir(parents=True);write(out/"NEGATIVES.json",negatives)
    expected={n:[core.oracle(c,n=="before") for c in cases] for n in ["before","candidate"]}
    write(out/"EXPECTED.json",expected)
    work=out/"lean";work.mkdir()
    modules=["OffsetEncoding","OffsetSource","ModelMutants"]
    roster=json.loads((root/"AUDITS.json").read_text())
    names=[]
    for m in modules:
        text=(root/"lean"/(m+".lean")).read_text();(work/(m+".lean")).write_text(text)
        names += [m+"."+n for n in re.findall(r"^theorem (\w+)",text,re.M)]
    require(names==roster["declarations"],"theorem roster")
    require(names[:12]==json.loads((root/"AUDIT-ROSTER-v1.json").read_text())["declarations"],"v1 theorem roster transfer")
    require(set(roster["allowed_axioms"])=={"propext","Classical.choice","Quot.sound"},"axiom policy")
    require(roster["generated_additions"]==["Calibration.before_rows","Calibration.candidate_rows"],"generated audit roster")
    def integer(v):return "("+str(v)+")" if v<0 else str(v)
    inputs="["+",\n".join("⟨"+str(c["side"])+", "+str(c["auto"]).lower()+", "+integer(c["resolved"])+", "+integer(c["basis"])+"⟩" for c in cases)+"]"
    def listrows(rows):return "["+",\n".join("["+", ".join(integer(v) for v in row)+"]" for row in rows)+"]"
    calibration="import OffsetSource\nset_option maxRecDepth 100000\nset_option maxHeartbeats 0\nnamespace Calibration\ndef inputs : List OffsetSource.Input := "+inputs+"\n"
    for n,fn in [("before","observeOld"),("candidate","observe")]:
        calibration+="theorem "+n+"_rows : inputs.map (fun c => OffsetSource.row (OffsetSource."+fn+" c)) = "+listrows(expected[n])+" := by decide +kernel\n"
    calibration+="end Calibration\n";(work/"Calibration.lean").write_text(calibration)
    names += ["Calibration.before_rows","Calibration.candidate_rows"]
    (work/"Audit.lean").write_text("import Calibration\nimport ModelMutants\n"+"\n".join("#print axioms "+n for n in names)+"\n")
    driver="import Calibration\nimport ModelMutants\ndef emit (name : String) (o : OffsetSource.Observation) : IO Unit :=\n  IO.println (name ++ \" \" ++ String.intercalate \" \" ((OffsetSource.row o).map toString))\ndef main : IO Unit := do\n  for c in Calibration.inputs do\n    emit \"before\" (OffsetSource.observeOld c)\n    emit \"candidate\" (OffsetSource.observe c)\n"
    for i,n in enumerate(MUTANTS,1):driver+="    emit \""+n+"\" (ModelMutants.observe "+str(i)+" c)\n"
    (work/"Driver.lean").write_text(driver)
    commands=[];env={"PATH":"/usr/bin:/bin","LEAN_PATH":str(work)}
    for m in modules+["Calibration","Audit"]:
        command=[tool["lean"],"-o",str(work/(m+".olean")),str(work/(m+".lean"))]
        proc=subprocess.run(command,cwd=work,env=env,text=True,capture_output=True);(work/(m+".log")).write_text(proc.stdout+proc.stderr)
        commands.append({"name":m,"command":command,"exit":proc.returncode});write(out/"LEAN-COMMANDS.json",commands)
        require(proc.returncode==0,"Lean compile "+m)
        require("warning:" not in proc.stdout+proc.stderr,"Lean warning "+m)
    allowed={"propext","Classical.choice","Quot.sound"};audits={}
    for line in (work/"Audit.log").read_text().splitlines():
        match=re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]",line)
        if match:name,axioms=match[1],([] if not match[2] else match[2].split(", "))
        else:
            match=re.fullmatch(r"'([^']+)' does not depend on any axioms",line);require(match is not None,"audit grammar");name,axioms=match[1],[]
        require(name not in audits and set(axioms)<=allowed,"unsupported axiom");audits[name]=axioms
    require(list(audits)==names,"audit roster completeness");write(out/"AUDITS.json",audits)
    command=[tool["lean"],"--run",str(work/"Driver.lean")]
    proc=subprocess.run(command,cwd=work,env=env,text=True,capture_output=True);(work/"Driver.log").write_text(proc.stdout);(work/"Driver-stderr.log").write_text(proc.stderr)
    commands.append({"name":"Driver","command":command,"exit":proc.returncode});write(out/"LEAN-COMMANDS.json",commands)
    require(proc.returncode==0 and not proc.stderr,"Lean driver")
    leanrows={name:[] for name in ["before","candidate",*MUTANTS]}
    for line in proc.stdout.splitlines():
        parts=line.split();require(len(parts)==6 and parts[0] in leanrows,"driver schema");leanrows[parts[0]].append(list(map(int,parts[1:])))
    for name,rows in leanrows.items():require(len(rows)==len(cases),"Lean rows "+name)
    for name in expected:require(leanrows[name]==expected[name],"Lean independent oracle "+name)
    write(out/"LEAN-ROWS.json",leanrows)
    text_input="".join(f"{c['side']} {int(c['auto'])} {c['resolved']} {c['basis']}\n" for c in cases);(out/"INPUT.txt").write_text(text_input)
    native=out/"native";native.mkdir();commands=[];results={};mutations={}
    for name,mode in [(name,mode) for name in ["before","candidate","candidate-formatted"] for mode in ["debug","optimized"]]+[(n,"optimized") for n in MUTANTS]:
        identity=mode+"-"+name;folder=native/identity;folder.mkdir();source,bindings=core.native(name);(folder/"source.cpp").write_text(source)
        flags=["-O0"] if mode=="debug" else ["-O2"]
        command=[tool["compiler"],"-isysroot",tool["sdk"],"-std=c++17","-fsanitize=undefined","-fno-sanitize-recover=all",*flags,"-MD","-MF",str(folder/"deps.d"),str(folder/"source.cpp"),"-o",str(folder/"probe")]
        proc=subprocess.run(command,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin","TMPDIR":str(folder)})
        (folder/"compile.log").write_text(proc.stdout+proc.stderr);commands.append({"name":identity,"command":command,"compile_exit":proc.returncode,"source_sha256":core.sha(source.encode())});write(out/"NATIVE-COMMANDS.json",commands)
        require(proc.returncode==0,"native compilation "+identity)
        dependencies=(folder/"deps.d").read_text().replace("\\\n"," ").split(":",1)[1].split()
        headers=sorted(set(dependencies)-{str(folder/"source.cpp")})
        require(headers==[entry["path"] for entry in json.loads((root/"CPP-HEADERS.json").read_text())["entries"]],"exact native header closure")
        proc=subprocess.run([str(folder/"probe")],input=text_input,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin"})
        (folder/"raw.txt").write_text(proc.stdout);(folder/"stderr.log").write_text(proc.stderr);commands[-1]["run_exit"]=proc.returncode;write(out/"NATIVE-COMMANDS.json",commands)
        require(proc.returncode==0 and not proc.stderr,"native execution "+identity)
        rows=[list(map(int,line.split())) for line in proc.stdout.splitlines()]
        require(len(rows)==len(cases) and all(len(r)==5 for r in rows),"native row schema")
        model="candidate" if name=="candidate-formatted" else name
        require(rows==leanrows[model],"native / Lean concrete agreement "+identity)
        results[identity]=core.sha(proc.stdout.encode())
        if name in MUTANTS:
            diffs=[i for i,(a,b) in enumerate(zip(rows,expected["candidate"])) if a!=b];require(diffs,"semantic mutant survived")
            i=diffs[0];mutations[name]={"different_cases":len(diffs),"first_index":i,"input":cases[i],"native":rows[i],"lean":leanrows[name][i],"expected":expected["candidate"][i]}
    write(out/"MUTANTS.json",mutations)
    cleanup=[]
    for f in sorted(out.rglob("*")):
        if f.is_file() and (f.name=="probe" or f.suffix in [".olean",".ilean",".ir"] or f.name.endswith((".olean.private",".olean.server"))):
            cleanup.append({"path":str(f.relative_to(out)),"sha256":core.sha(f.read_bytes()),"bytes":f.stat().st_size});f.unlink()
    write(out/"CLEANUP.json",cleanup)
    return {"complete":True,"cases":len(cases),"original_cases_preserved":216,"audited_results":len(audits),"correct_native_runs":6,"semantic_native_mutants":len(mutations),"semantic_lean_mutants":5,"numeric_provider_negatives":len(negatives),"raw_hashes":results,"compiler_products_removed":len(cleanup)}
