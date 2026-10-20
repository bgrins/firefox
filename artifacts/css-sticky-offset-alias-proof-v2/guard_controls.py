import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CAPSULE=ROOT/"capsule"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resign(p):
    entries=[{"path":str(f.relative_to(p)),"sha256":sha(f)} for f in sorted(p.rglob("*")) if f.is_file() and str(f.relative_to(p)) not in ["FILES.json","FREEZE.json"]]
    (p/"FILES.json").write_text(json.dumps({"files":entries},indent=2)+"\n")
    digest=sha(p/"FILES.json");(p/"FREEZE.json").write_text(json.dumps({"files_sha256":digest})+"\n");return digest

def main():
    out=ROOT/"guards-v1"
    if out.exists():raise RuntimeError("guard output exists")
    out.mkdir();receipts=[]
    base=sha(CAPSULE/"FILES.json")
    work=out/"work";work.mkdir()
    def run(name,flags=["-I","-S"],entry="check.py",edit=None,resign_input=False,expected="",where="normal",wrong_hash=False,shadow=None):
        folder=work/name;shutil.copytree(CAPSULE,folder)
        output=work/(name+"-output")
        marker=work/(name+"-SHADOW")
        if shadow:(folder/shadow).write_text("from pathlib import Path\nPath("+repr(str(marker))+ ").write_text('executed')\n")
        if edit:edit(folder)
        digest=resign(folder) if resign_input else base
        if wrong_hash:digest="0"*64
        if where=="inside":output=folder/"new-output"
        if where=="existing":output.mkdir()
        command=[sys.executable,*flags,str(folder/entry),"--manifest-sha",digest,"--out",str(output)]
        proc=subprocess.run(command,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin"})
        valid=proc.returncode!=0 and expected in proc.stderr and not marker.exists() and (not output.exists() if where!="existing" else not any(output.iterdir()))
        receipts.append({"id":name,"command":command,"exit":proc.returncode,"expected":expected,"stderr":proc.stderr,"stdout":proc.stdout,"shadow_executed":marker.exists(),"pass":valid})
        if not valid:raise RuntimeError(name)
    for entry,shadow in [("check.py","json.py"),("core.py","hashlib.py"),("engine.py","hashlib.py")]:
        for label,flags in [("site",["-I"]),("nonisolated",["-S"]),("optimized",["-I","-S","-O"]),("doubleoptimized",["-I","-S","-OO"])]:
            run(entry.replace(".py","")+"-"+label,flags,entry,expected="Require python3 -I -S without optimization",shadow=shadow)
    run("wrong-hash",wrong_hash=True,expected="external manifest hash")
    run("modified-source",edit=lambda p:(p/"core.py").write_text((p/"core.py").read_text()+"\n"),expected="file hash: core.py")
    run("nested-seal",edit=lambda p:(p/"native/FILES.json").write_text("{}"),expected="unexpected file: native/FILES.json")
    run("empty-directory",edit=lambda p:(p/"empty").mkdir(),expected="unexpected directory: empty")
    run("fifo",edit=lambda p:os.mkfifo(p/"fifo"),expected="nonregular entry: fifo")
    run("directory-link",edit=lambda p:(p/"link").symlink_to(p/"native",target_is_directory=True),expected="nonregular entry: link")
    run("file-link",edit=lambda p:(p/"link").symlink_to(p/"core.py"),expected="nonregular entry: link")
    run("missing-input",edit=lambda p:(p/"core.py").unlink(),expected="missing files")
    run("inside-output",where="inside",expected="output inside capsule")
    run("existing-output",where="existing",expected="output must be absent")
    def bad_case(p):
        rows=json.loads((p/"CASES.json").read_text());rows[-1]["id"]="changed";(p/"CASES.json").write_text(json.dumps(rows))
    run("resealed-roster-difference",edit=bad_case,resign_input=True,expected="complete case roster")
    def bad_binding(p):
        rows=json.loads((p/"BINDINGS.json").read_text());rows[0]["start_byte"]+=1;(p/"BINDINGS.json").write_text(json.dumps(rows))
    run("resealed-binding-difference",edit=bad_binding,resign_input=True,expected="source bindings")
    def bad_compiler(p):
        t=json.loads((p/"TOOLCHAIN.json").read_text());t["compiler_sha256"]="0"*64;(p/"TOOLCHAIN.json").write_text(json.dumps(t))
    run("resealed-compiler-difference",edit=bad_compiler,resign_input=True,expected="tool identity compiler")
    def bad_library(p):
        t=json.loads((p/"LEAN-TOOLCHAIN.json").read_text());t["entries"][0]["sha256"]="0"*64;(p/"LEAN-TOOLCHAIN.json").write_text(json.dumps(t))
    run("resealed-library-difference",edit=bad_library,resign_input=True,expected="transitive toolchain manifest")
    (out/"RESULT.json").write_text(json.dumps({"complete":True,"controls":receipts,"source_manifest":base},indent=2)+"\n")
    shutil.rmtree(work)
    print(json.dumps({"complete":True,"controls":len(receipts)}))
if __name__=="__main__":main()
