import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,stat,subprocess
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
    require(all('__pycache__' not in Path(n).parts and not n.endswith(('.pyc','.olean','.ilean','.ir','.olean.private','.olean.server')) for n in names),'forbidden capsule cache')
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

def authenticate_tools():
    tool=readjson(ROOT/"TOOLCHAIN.json");library=readjson(ROOT/"LEAN-TOOLCHAIN.json")
    root=Path(library["root"])
    require(Path(tool["lean"])==root/"bin/lean","Lean path binding")
    for name in ["lean","compiler"]:
        require(sha(Path(tool[name]).read_bytes())==tool[name+"_sha256"],"tool identity "+name)
        version=subprocess.run([tool[name],"--version"],capture_output=True,text=True,check=True,env={"PATH":"/usr/bin:/bin"}).stdout
        require(version==tool[name+"_version"],"tool version "+name)
    seen={};directories=[]
    for part in ["bin","lib"]:
        for f in [root/part,*sorted((root/part).rglob("*"))]:
            mode=f.lstat().st_mode;name=str(f.relative_to(root))
            if stat.S_ISDIR(mode):directories.append(name)
            elif stat.S_ISLNK(mode):seen[name]={"path":name,"symlink":str(f.readlink()),"sha256":sha(f.read_bytes())}
            elif stat.S_ISREG(mode):seen[name]={"path":name,"sha256":sha(f.read_bytes())}
            else:raise RuntimeError("nonregular toolchain entry")
    require(directories==library["directories"],"toolchain directory roster")
    require(list(seen.values())==library["entries"],"transitive toolchain manifest")
    for entry in readjson(ROOT/"CPP-HEADERS.json")["entries"]:
        require(sha(Path(entry["path"]).read_bytes())==entry["sha256"],"C++ header identity")
    return tool

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--manifest-sha",required=True);parser.add_argument("--out");parser.add_argument("--verify-only",action="store_true")
    args=parser.parse_args();authenticate(args.manifest_sha)
    if args.verify_only:
        roles=load("source_roles").authenticate(ROOT);authenticate_tools();print(json.dumps({"verified":True,"roles":roles}));return
    require(args.out is not None,"output required")
    out=Path(args.out).resolve();require(out!=ROOT and ROOT not in out.parents,"output inside capsule");require(not out.exists(),"output must be absent")
    source_roles=load("source_roles").authenticate(ROOT)
    tool=authenticate_tools()
    core=load("core");engine=load("engine")
    result=engine.run(ROOT,out,tool,core)
    authenticate_tools();authenticate(args.manifest_sha)
    require(load("source_roles").authenticate(ROOT)==source_roles,"source roles changed")
    result["source_roles"]=source_roles
    write(out/"SOURCE-ROLES.json",source_roles)
    result["source_manifest"]=args.manifest_sha
    result["scope"]="Complete widened normalization, geometry, two-coordinate position/translation and range callers under explicit executed-expression bounds; geometry providers and timeline/scheduling remain admitted."
    write(out/"RESULT.json",result);print(json.dumps(result))
if __name__=="__main__":main()
