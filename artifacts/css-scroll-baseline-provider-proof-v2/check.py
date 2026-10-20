import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without -O/-OO')
sys.dont_write_bytecode = True
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, re, stat, subprocess
ROOT=Path(__file__).resolve().parent
def require(value, message):
    if not value: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        require(key not in result, 'duplicate JSON key: '+key)
        result[key]=value
    return result
def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)
def authenticate():
    for name in ['FILES.json','FREEZE.json']:
        require(stat.S_ISREG((ROOT/name).lstat().st_mode), 'nonregular root seal: '+name)
    manifest=read_json(ROOT/'FILES.json')
    require(isinstance(manifest,list) and manifest, 'invalid manifest')
    expected_files={'FILES.json','FREEZE.json'};expected_dirs={''}
    for row in manifest:
        require(isinstance(row,dict) and set(row)=={'path','bytes','sha256'}, 'invalid manifest row')
        name=row['path'];require(isinstance(name,str), 'invalid manifest path')
        path=PurePosixPath(name)
        require(name==path.as_posix() and bool(path.parts) and not path.is_absolute()
            and all(part not in ('','.','..') for part in path.parts), 'invalid manifest path')
        require(name not in expected_files, 'duplicate / reserved manifest path')
        require(type(row['bytes']) is int and row['bytes']>=0, 'invalid input size')
        require(isinstance(row['sha256'],str) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'invalid digest')
        require(not any(part=="__pycache__" for part in path.parts) and path.suffix not in {".pyc",".olean",".o",".so",".dylib"}, "generated binary is not a source input")
        expected_files.add(name)
        for parent in path.parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    actual_files=set();actual_dirs={''}
    def visit(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                rel=Path(entry.path).relative_to(ROOT).as_posix()
                mode=entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    require(rel in expected_dirs, 'unexpected directory: '+rel)
                    actual_dirs.add(rel);visit(entry.path)
                else:
                    require(stat.S_ISREG(mode), 'nonregular entry: '+rel)
                    actual_files.add(rel)
    visit(ROOT)
    require(actual_files==expected_files, 'file roster mismatch')
    require(actual_dirs==expected_dirs, 'directory roster mismatch')
    for row in manifest:
        path=ROOT/row['path']
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'], 'input mismatch: '+row['path'])
    freeze=read_json(ROOT/'FREEZE.json')
    require(freeze['FILES_sha256']==sha(ROOT/'FILES.json'), 'manifest seal mismatch')
    require(freeze['check_sha256']==sha(ROOT/'check.py'), 'checker seal mismatch')
    return manifest
initial=authenticate()
def validate_sources():
    import importlib.util
    def load(name,path):
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module
    bound=load("bound_sources",ROOT/"source_bindings.py").bindings()
    require(bound==read_json(ROOT/"SOURCE-BINDINGS.json"),"source binding mismatch")
    case_module=load("case_schema",ROOT/"native/cases.py")
    require(len(case_module.read())==1536,"case roster")
    pins=read_json(ROOT/"SOURCE-PINS.json")
    for name,digest in pins.items():
        require(sha(ROOT/name)==digest,"frozen source transfer: "+name)
    require(authenticate()==initial,"closure after imports")
validate_sources()
config=read_json(ROOT/"TOOLCHAIN.json")
for tool in ["lean","clang"]:
    require(sha(Path(config[tool]))==config[tool+"_sha256"], "toolchain mismatch")
modules=read_json(ROOT/"MODULES.json")
require(type(modules) is list and len(set(modules))==len(modules), "module roster")
require({p.name for p in (ROOT/"lean").iterdir()}=={x+".lean" for x in modules+["Audit"]}, "Lean module closure")
for name in modules:
    source=(ROOT/"lean"/(name+".lean")).read_text()
    require(not re.search(r"\b(sorry|admit|axiom|native_decide)\b",source), "unsupported proof token")
entries=[]
for module in modules:
    source=(ROOT/"lean"/(module+".lean")).read_text()
    namespaces=re.findall(r"^namespace ([A-Za-z0-9_.]+)$",source,re.M)
    require(len(namespaces)==1,"supported single namespace profile")
    starts=list(re.finditer(r"^(?:theorem|def|structure|inductive|end|#print)\b",source,re.M))
    for index,match in enumerate(starts):
        if not source[match.start():].startswith("theorem "): continue
        name=re.match(r"theorem\s+(\w+)",source[match.start():]).group(1)
        declaration=source[match.start():starts[index+1].start() if index+1<len(starts) else len(source)].strip()
        entries.append({"name":namespaces[0]+"."+name,"module":module,"complete_declaration":declaration,
            "sha256":hashlib.sha256(declaration.encode()).hexdigest()})
require(entries==read_json(ROOT/"DECLARATIONS.json"),"declaration inventory mismatch")
require([e["name"] for e in entries]==read_json(ROOT/"AUDIT-NAMES.json"),"audit inventory mismatch")
p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);args=p.parse_args()
require(args.output.is_absolute(),"absolute output required")
out=args.output.resolve()
require(not out.exists() and not out.is_relative_to(ROOT),"absent external output required")
out.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith(("LEAN_","PYTHON"))}
commands=[]
def run(command):
    p=subprocess.run(command,env=env,cwd=out,capture_output=True,text=True)
    commands.append({"command":command,"exit":p.returncode,"stdout":p.stdout,"stderr":p.stderr})
    (out/"COMMANDS.json").write_text(json.dumps(commands,indent=2)+"\n")
    require(p.returncode==0,"subcommand failed: "+p.stdout+p.stderr)
    require(not p.stderr,"subcommand diagnostic")
    require(authenticate()==initial,"inputs changed during replay")
    return p
bindingRun=run([sys.executable,"-I","-S",str(ROOT/"source_bindings.py")])
require(json.loads(bindingRun.stdout)==read_json(ROOT/"SOURCE-BINDINGS.json"),"source extraction drift")
run([sys.executable,"-I","-S",str(ROOT/"compile.py"),"--output",str(out/"proof")])
records=read_json(out/"proof/COMMANDS.json")
audit=records[-1]["stdout"]
(out/"AUDIT.txt").write_text(audit)
rows=re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",audit)
require([r[0] for r in rows]==read_json(ROOT/"AUDIT-NAMES.json"),"kernel audit roster")
for _,_,axioms in rows:
    require({a.strip() for a in axioms.split(",")}<={"","propext","Quot.sound","Classical.choice"},"unapproved axiom")
run([sys.executable,"-I","-S",str(ROOT/"native/cases.py")])
run([sys.executable,"-I","-S",str(ROOT/"native/build.py"),"--output",str(out/"native"),"--olean",str(out/"proof")])
run([sys.executable,"-I","-S",str(ROOT/"model_mutants.py"),"--output",str(out/"model-mutants"),"--olean",str(out/"proof")])
require(authenticate()==initial,"final closure")
result={"replay":"PASS","modules":len(records),"audits":len(rows),
    "source_bindings":len(read_json(ROOT/"SOURCE-BINDINGS.json")),
    "native":read_json(out/"native/RESULT.json"),
    "model_mutants":len(read_json(out/"model-mutants/RESULTS.json")),
    "scope":"Conditional complete scroll-provider dispatch/conversion; no child-provider, geometry lifecycle or full CSS/layout closure."}
(out/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
