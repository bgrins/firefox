import argparse,hashlib,json,stat
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument("--files-sha256",required=True)
args=parser.parse_args()
here=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(here/"FILES.json")!=args.files_sha256:raise RuntimeError("Manifest")
manifest=json.loads((here/"FILES.json").read_text())
if {p.name for p in here.iterdir()}!=set(manifest)|{"FILES.json","FREEZE.json"}:raise RuntimeError("Roster")
for name,pin in manifest.items():
    path=here/name
    if Path(name).name!=name or not stat.S_ISREG(path.lstat().st_mode) or sha(path)!=pin:raise RuntimeError(name)
print(f"PASS {len(manifest)} sealed review payloads")
