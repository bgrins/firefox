import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse, hashlib, json, os, re, stat, subprocess
from pathlib import Path, PurePosixPath
ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok: raise RuntimeError(message)

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result

def read(path): return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate(root):
    for name in ["FILES.json", "FREEZE.json"]:
        require(stat.S_ISREG((root/name).lstat().st_mode), "nonregular seal")
    rows = read(root/"FILES.json")
    require(isinstance(rows, list) and rows, "empty manifest")
    files = {"FILES.json", "FREEZE.json"}; directories = {""}
    for row in rows:
        require(isinstance(row,dict) and set(row)=={"path","bytes","sha256"}, "manifest shape")
        name = row["path"]; require(isinstance(name,str), "path type")
        path = PurePosixPath(name)
        require(name == path.as_posix() and path.parts and not path.is_absolute()
                and all(v not in [".", "..", ""] for v in path.parts), "path escape")
        require(name not in files, "duplicate path")
        require(type(row["bytes"]) is int and row["bytes"] >= 0, "size")
        require(isinstance(row["sha256"],str) and re.fullmatch("[0-9a-f]{64}",row["sha256"]), "hash")
        files.add(name)
        for parent in path.parents:
            if str(parent) != ".": directories.add(str(parent))
    found_files=set(); found_dirs={""}
    def visit(directory):
        for entry in os.scandir(directory):
            relative = Path(entry.path).relative_to(root).as_posix()
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                require(relative in directories, "extra directory")
                found_dirs.add(relative); visit(entry.path)
            else:
                require(stat.S_ISREG(mode), "nonregular entry")
                found_files.add(relative)
    visit(root)
    require(files==found_files and directories==found_dirs, "closed roster")
    for row in rows:
        file=root/row["path"]
        require(file.stat().st_size==row["bytes"] and digest(file)==row["sha256"], "input mismatch: "+row["path"])
    require(read(root/"FREEZE.json")["FILES_sha256"]==digest(root/"FILES.json"), "manifest seal")
    return rows

initial = authenticate(ROOT)
for name, expected in read(ROOT/"AUTHENTICATION.json")["pins"].items():
    require(digest(ROOT/"capsule"/name)==expected, "producer pin")
authenticate(ROOT/"capsule")
r=read(ROOT/"replay/RESULT.json")
require(r["complete"] and (r["audits"],r["compiled_modules"],r["source_bindings"])==(90,8,25), "replay results")
require(r["calibration"]["cases"]==1755 and len(r["calibration"]["original_disagreements"])==5, "case counts")
require({k:len(v) for k,v in r["calibration"]["native_mutants"].items()}=={"reverse-order":12,"omit-native-delete":9}, "native mutants")
require(r["lean_mutants"]=={"duplicate-initialization":1,"forgot-native-delete":1,"ignored-root-state":1}, "Lean mutants")
require((ROOT/"replay/CALIBRATION.txt").read_bytes()==(ROOT/"replay/native/candidate.txt").read_bytes(), "native/model rows")
require(len((ROOT/"replay/CALIBRATION.txt").read_text().splitlines())==1755, "row count")
guards=read(ROOT/"INTEGRITY.json")
require(len(guards)==12 and all(x["passed"] and x["exit"]!=0 and not x["output_created"] and not x["shadow_executed"] for x in guards), "guards")
challenge=(ROOT/"CHALLENGES.log").read_text()
require("error:" not in challenge and len(re.findall(r"'IndependentReview[.]",challenge))==12, "challenge audits")
for axioms in re.findall(r"depends on axioms: \[([^\]]*)\]",challenge):
    require(set(axioms.split(", ")) <= {"propext","Classical.choice","Quot.sound"}, "challenge axiom")
require(digest(ROOT/"Challenges.lean")==read(ROOT/"CHALLENGES-RESULT.json")["source_sha256"], "challenge source")
p=argparse.ArgumentParser(); p.add_argument("--replay", type=Path); args=p.parse_args()
if args.replay:
    output=args.replay.resolve()
    require(output!=ROOT and ROOT not in output.parents and not output.exists(), "fresh external output required")
    command=[sys.executable,"-I","-S",str(ROOT/"capsule/check.py"),"--output",str(output)]
    result=subprocess.run(command,text=True,capture_output=True)
    require(result.returncode==0,result.stdout+result.stderr)
    config=read(ROOT/"capsule/TOOLCHAIN.json")
    require(digest(Path(config["lean"]))==config["lean_sha256"], "Lean executable")
    env={k:v for k,v in os.environ.items() if not k.startswith(("LEAN_","PYTHON"))}
    env["LEAN_PATH"]=str(output/"lean")
    result=subprocess.run([config["lean"],str(ROOT/"Challenges.lean")],env=env,text=True,capture_output=True)
    (output/"INDEPENDENT-CHALLENGES.log").write_text(result.stdout+result.stderr)
    require(result.returncode==0 and len(re.findall(r"'IndependentReview[.]",result.stdout))==12,"fresh challenges")
require(authenticate(ROOT)==initial,"review changed")
print(json.dumps({"accepted_scope":"conditional initial deduplication and successful membership histories; no style invalidation", "audits":90,"independent_challenges":12,"native_cases":1755,"integrity_negatives":12,"fresh_replay":bool(args.replay)}))
