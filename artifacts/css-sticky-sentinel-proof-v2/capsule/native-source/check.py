import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse, hashlib, importlib.util, json, os, stat, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def require(condition,message):
    if not condition:raise RuntimeError(message)
def readjson(path):return json.loads(path.read_text())
def authenticate(expected):
    manifest=ROOT/"FILES.json"
    require(sha(manifest.read_bytes())==expected,"external manifest hash")
    entries=readjson(manifest)["files"]
    names=[e["path"] for e in entries]
    require(len(names)==len(set(names)),"duplicate manifest path")
    for name in names:
        require(isinstance(name,str) and str(Path(name))==name and not Path(name).is_absolute() and ".." not in Path(name).parts and name not in ["FILES.json","FREEZE.json"],"manifest path")
    wanted=set(names)|{"FILES.json","FREEZE.json"}
    directories={str(p) for name in wanted for p in Path(name).parents if str(p)!="."}
    found=set()
    def walk(path):
        for child in path.iterdir():
            name=str(child.relative_to(ROOT));mode=child.lstat().st_mode
            if stat.S_ISDIR(mode):
                require(name in directories,"unexpected directory: "+name);walk(child)
            else:
                require(stat.S_ISREG(mode),"nonregular entry: "+name)
                require(name in wanted,"unexpected file: "+name);found.add(name)
    walk(ROOT);require(found==wanted,"missing files")
    for entry in entries:require(sha((ROOT/entry["path"]).read_bytes())==entry["sha256"],"file hash: "+entry["path"])
    require(readjson(ROOT/"FREEZE.json")["files_sha256"]==expected,"freeze binding")
    return entries

def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+".py"))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def write(path,value):path.write_text(json.dumps(value,indent=2)+"\n")
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--manifest-sha",required=True);parser.add_argument("--out",required=True)
    args=parser.parse_args();entries=authenticate(args.manifest_sha)
    out=Path(args.out).resolve()
    require(out!=ROOT and ROOT not in out.parents,"output inside capsule")
    require(not out.exists(),"output must be absent")
    tool=readjson(ROOT/"TOOLCHAIN.json");compiler=Path(tool["compiler"])
    require(sha(compiler.read_bytes())==tool["compiler_sha256"],"compiler identity")
    version=subprocess.run([str(compiler),"--version"],capture_output=True,text=True,check=True,env={"PATH":"/usr/bin:/bin"}).stdout
    require(version==tool["version"],"compiler version")
    core=load("core");controls=load("controls")
    before=(ROOT/"inputs/before.cpp").read_text();after=(ROOT/"inputs/candidate.cpp").read_text()
    old_body=core.extract(before,core.SIGNATURES[2])[0];new_body=core.extract(after,core.SIGNATURES[2])[0]
    require(before.replace(old_body,new_body)==after,"only DoComputePosition differs")
    cases=readjson(ROOT/"CASES.json")
    require(cases==core.cases(),"exact generated case roster")
    require(len({c["id"] for c in cases})==len(cases),"duplicate case id")
    for c in cases:core.validate(c)
    require(core.translation("new")[1]==readjson(ROOT/"BINDINGS.json"),"exact extraction bindings")
    require(core.providers()==readjson(ROOT/"PROVIDERS.json"),"exact provider slices")
    for binding in readjson(ROOT/"BINDINGS.json")+readjson(ROOT/"PROVIDERS.json"):
        data=(ROOT/binding["file"]).read_bytes()[binding["start_byte"]:binding["end_byte"]]
        require(sha(data)==binding["sha256"],"byte slice")
    negatives=[]
    for name,case,reason in controls.rejections(core):
        try:core.validate(case)
        except ValueError as e:require(str(e)==reason,"unexpected rejection "+name+": "+str(e));negatives.append({"id":name,"reason":str(e)})
        else:raise RuntimeError("accepted invalid provider: "+name)
    out.mkdir(parents=True);write(out/"REJECTIONS.json",negatives)
    protocol=core.encode(cases);(out/"INPUT.txt").write_text(protocol)
    expected={v:[core.oracle(c,v) for c in cases] for v in ["old","new"]}
    for v,rows in expected.items():(out/(v+"-expected.jsonl")).write_text("".join(json.dumps(row,sort_keys=True)+"\n" for row in rows))
    commands=[];outputs={};mutants={}
    variants=[(v,mode) for v in ["old","new"] for mode in ["debug","release"]]+[(v,"debug") for v in ["restored","all_auto_only","numeric_edges","swapped_masks","effective_activation","missing_finite_clamp","reordered"]]
    for variant,mode in variants:
        name=variant+"-"+mode;work=out/name;work.mkdir()
        code,bindings=core.translation(variant);(work/"source.cpp").write_text(code);write(work/"BINDINGS.json",bindings)
        flags=["-O0","-DDEBUG"] if mode=="debug" else ["-O2","-DNDEBUG"]
        command=[str(compiler),"-isysroot",tool["sdk"],"-std=c++20",*flags,"-fsanitize=undefined","-fno-sanitize-recover=all","-MD","-MF",str(work/"deps.d"),str(work/"source.cpp"),"-o",str(work/"probe")]
        run=subprocess.run(command,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin","TMPDIR":str(work)})
        (work/"compile.log").write_text(run.stdout+run.stderr);commands.append({"name":name,"compile":command,"compile_exit":run.returncode,"source_sha256":sha(code.encode())})
        write(out/"COMMANDS.json",commands);require(run.returncode==0,"compile "+name)
        run=subprocess.run([str(work/"probe")],input=protocol,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin"})
        (work/"raw.jsonl").write_text(run.stdout);(work/"stderr.log").write_text(run.stderr)
        commands[-1].update(run_exit=run.returncode,output_sha256=sha(run.stdout.encode()))
        write(out/"COMMANDS.json",commands);require(run.returncode==0 and not run.stderr,"execution "+name)
        rows=[json.loads(line) for line in run.stdout.splitlines()];require(len(rows)==len(cases),"row count "+name)
        outputs[name]=rows
        if variant in expected:require(rows==expected[variant],"independent oracle/trace "+name)
        else:
            differences=[i for i,(a,b) in enumerate(zip(rows,expected["new"])) if (a["value"],a["frames"])!=(b["value"],b["frames"])]
            require(differences,"undetected semantic mutant "+name);i=differences[0]
            mutants[variant]={"different_cases":len(differences),"first_id":cases[i]["id"],"input":cases[i],"expected":expected["new"][i],"actual":rows[i]}
    for v in ["old","new"]:require(outputs[v+"-debug"]==outputs[v+"-release"],"debug/release "+v)
    changes=[c["id"] for c,a,b in zip(cases,expected["old"],expected["new"]) if (a["value"],a["frames"])!=(b["value"],b["frames"])]
    write(out/"MUTANTS.json",mutants);write(out/"OLD-NEW.json",{"changed":len(changes),"ids":changes})
    require(sha(compiler.read_bytes())==tool["compiler_sha256"],"compiler changed during replay")
    authenticate(args.manifest_sha)
    write(out/"RESULT.json",{"complete":True,"cases":len(cases),"correct_variant_runs":4,"compiled_mutants":len(mutants),"rejections":len(negatives),"binding_count":len(core.translation("new")[1]),"source_manifest":args.manifest_sha,"native_scope":"extracted consumers/callers with admitted providers; no whole geometry or browser equivalence"})
    print(json.dumps(readjson(out/"RESULT.json")))
if __name__=="__main__":main()
