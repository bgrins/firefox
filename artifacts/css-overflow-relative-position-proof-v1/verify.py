#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent
PINS={
 "sources/nsContainerFrame.cpp":"36f3b5faecd3ce0b26f9c7b6ae8e12c5365e08c1819d657eed73b8b622e1136d",
 "candidate-nsContainerFrame.cpp":"d80f991771f48292657a7c9e5914394adfa30c93e55fa5b3f5626567db5de197",
 "proposal.patch":"f7d213934f10ac0c33fbffe999630f45516f6e3836ca23abb1bfdcc658cd6b04",
 "relative-position-overflow-continuations.html":"f343069aefdd630657da02c84518f538d12773e4a938fc1c3b2c93770e7ce560",
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(root):
    files=json.loads((root/"FILES.json").read_text())
    assert sha(root/"FILES.json")==json.loads((root/"FREEZE.json").read_text())["files_sha256"],"freeze identity"
    actual=set()
    for path in root.rglob("*"):
        assert not path.is_symlink(),"symlink rejected"
        rel=path.relative_to(root)
        assert not {".lake","__pycache__","target"}.intersection(rel.parts),"cache rejected"
        assert path.suffix not in {".olean",".ilean",".o",".pyc",".exe",".dylib"},"compiler product rejected"
        if path.is_file():actual.add(str(rel))
    assert actual==set(files)|{"FILES.json","FREEZE.json"},"closed roster"
    for name,digest in files.items():
        rel=Path(name);assert not rel.is_absolute() and ".." not in rel.parts,"manifest path"
        assert sha(root/name)==digest,"payload hash: "+name
    for name,digest in PINS.items():assert sha(root/name)==digest,"source role identity: "+name
    return len(files)
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--replay",action="store_true");args=parser.parse_args()
    count=check(ROOT)
    if args.replay:
        with tempfile.TemporaryDirectory(prefix="css-relative-relocated-") as name:
            target=Path(name)/"capsule";target.mkdir()
            for rel in [*json.loads((ROOT/"FILES.json").read_text()),"FILES.json","FREEZE.json"]:
                path=target/rel;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,path)
            check(target)
            result=subprocess.run([sys.executable,str(target/"run_checks.py")],cwd=target,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            assert result.returncode==0,result.stdout
            check(target)
            print(json.dumps({"payload_files":count,"relocated_replay":json.loads(result.stdout)},indent=2))
    else:print(json.dumps({"payload_files":count,"closed_roster":True}))
if __name__=="__main__":main()
