import hashlib,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
record=json.loads((BASE/'SOURCE-v1.json').read_text())
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else BASE
out.mkdir(parents=True,exist_ok=True)
for path,entry in record['files'].items():
 old=subprocess.check_output(['git','show',record['parent']+':'+path],cwd=ROOT)
 current=old
 if path.endswith('/mix.rs'):
  guard=b'if source.color_space.is_rgb_or_xyz_like() && self.color_space.is_rgb_or_xyz_like() {\n'
  line=b'            self.flags |= source.flags & (F::C0_IS_NONE | F::C1_IS_NONE | F::C2_IS_NONE);\n'
  if old.count(guard)!=1:raise RuntimeError('Parent branch cardinality')
  current=old.replace(guard,guard+line,1)
 for kind,data in [('old',old),('current',current)]:
  if hashlib.sha256(data).hexdigest()!=entry[kind+'_sha256']:raise RuntimeError('Source identity: '+kind+' '+path)
  target=out/entry[kind+'_snapshot']
  if target.exists() and target.read_bytes()!=data:raise RuntimeError('Existing snapshot drift')
  target.write_bytes(data)
print('Materialized four authenticated native snapshots from parent and reviewed delta.')
