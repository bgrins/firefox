import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize: raise SystemExit("requires -I -S")
sys.dont_write_bytecode=True
import hashlib,json,os,pathlib,shutil,subprocess
root=pathlib.Path(__file__).resolve().parent
src=root/"capsule"
work=root/"guard-work"
work.mkdir(exist_ok=False)
pin="e93989395671b1edb1b9586d77a9898596c526ef4a8b1f0a18df12ccbaf25452"
results=[]
for name,flags,mutation in [
("optimized",["-I","-S","-O"],None),("double-optimized",["-I","-S","-OO"],None),
("nonisolated",["-S"],"shadow"),("site-enabled",["-I"],None),
("extra-directory",["-I","-S"],"directory"),("payload-change",["-I","-S"],"payload"),
("fifo",["-I","-S"],"fifo"),("symlink",["-I","-S"],"symlink")]:
    cap=work/name;shutil.copytree(src,cap)
    if mutation=="shadow": (cap/"json.py").write_text("raise RuntimeError('SHADOW_EXECUTED')")
    if mutation=="directory": (cap/"unexpected").mkdir()
    if mutation=="payload": (cap/"SCOPE.md").write_text("changed")
    if mutation=="fifo": os.mkfifo(cap/"unexpected")
    if mutation=="symlink": (cap/"unexpected").symlink_to(cap/"SCOPE.md")
    out=work/(name+"-output")
    cmd=[sys.executable,*flags,str(cap/"replay.py"),"--manifest-sha",pin,"--out",str(out)]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    assert r.returncode!=0 and not out.exists() and "SHADOW_EXECUTED" not in r.stderr
    results.append({"name":name,"command":cmd,"returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr,"output_created":out.exists()})
    shutil.rmtree(cap)
cmd=[sys.executable,"-I","-S",str(src/"replay.py"),"--manifest-sha",pin,"--verify-only"]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
assert r.returncode==0
results.append({"name":"intact-positive","command":cmd,"returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
work.rmdir()
(root/"GUARDS.json").write_text(json.dumps(results,indent=2)+"\n")
print("PASS eight pre-output rejections and intact positive")
