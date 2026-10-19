import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, subprocess
from pathlib import Path, PurePosixPath
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path)
a = p.parse_args()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
records = json.loads((R / 'MANIFEST.json').read_text())
seen = set()
for rec in records:
    name = rec['path']
    rel = PurePosixPath(name)
    assert not rel.is_absolute() and '..' not in rel.parts and str(rel) == name
    assert name not in seen
    seen.add(name)
    path = R / name
    assert path.is_file() and not path.is_symlink()
    for parent in path.parents:
        if parent == R:
            break
        assert not parent.is_symlink()
    assert sha(path) == rec['sha256'], name
actual = {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}
assert actual - {'MANIFEST.json', 'FREEZE.json'} == seen
assert not any(p.is_symlink() for p in R.rglob('*'))
D=R/'evidence/discovery'
assert sha(D/'MANIFEST.json')=='84956dadd778c205bf42ed6c903d580420be6838e827aebc38afa53ae17b1201'
assert sha(D/'FREEZE.json')=='08d0f83d3ef69bf13631cd78795fc6284f7b85f68620e8164ec4274f09184a17'
assert sha(D/'check.py')=='c6c7c1d95b01054030c6290656359603b6353d91f5e620138dde5364cfc0ff52'
subprocess.run([sys.executable,'-I','-S',str(D/'check.py')],check=True)
if a.output:
    out=a.output.resolve()
    assert not out.is_relative_to(R) and not out.exists()
    subprocess.run([sys.executable,'-I','-S',str(R/'replay.py'),'--output',str(out)],check=True)
print(json.dumps({'authenticated_files':len(records),'discovery_pin':True}))
