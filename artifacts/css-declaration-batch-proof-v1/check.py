import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,hashlib,json,os,stat,subprocess
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
if a.output:
 out=a.output.resolve();assert not out.is_relative_to(R) and not out.exists(),'output outside capsule and fresh'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
 d={}
 for k,v in pairs:
  assert k not in d,('duplicate JSON key',k)
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=unique)
manifest=read(R/'MANIFEST.json');assert isinstance(manifest,dict)
files=set();directories=set()
for root,dirs,names in os.walk(R,followlinks=False):
 for name in dirs+names:
  path=Path(root)/name;mode=path.lstat().st_mode
  assert stat.S_ISREG(mode) or stat.S_ISDIR(mode),('nonregular',str(path))
  (directories if stat.S_ISDIR(mode) else files).add(str(path.relative_to(R)))
assert files==set(manifest)|{'MANIFEST.json','FREEZE.json'},'closed files'
expected_dirs={str(parent) for name in files for parent in PurePosixPath(name).parents if str(parent)!='.'}
assert directories==expected_dirs,'closed directories'
for name,pin in manifest.items():
 rel=PurePosixPath(name)
 assert not rel.is_absolute() and '..' not in rel.parts and str(rel)==name,'path'
 assert sha(R/name)==pin,('hash',name)
assert read(R/'FREEZE.json')['manifest_sha256']==sha(R/'MANIFEST.json')
nested={
 'all-order':('e89fb0788f7fde9c69fa36c5329e72f1190b697a87168157b5500ca785bc4f04','492aefc7aa5ae7a0a62b138737d34648adf5122325a40ee47520fdb59ad30ff5','213f9c06e4e487a6a1ae75625161b7e8e0422c43e31dcddc3104cec275ceea80'),
 'source-admission':('95af19e5addabfeac43288e7b33f7ce68c528eeac3c536ccac2a59912d29b915','617606db4158bc86ff4618f767a01904dd5d75a613ffa3686b8be18abdd61c19','ce7d7a3808652b2d74e92e9d2b6fdff33c209c6fcb4464d325c684e1c89a2d85'),
 'nan-audit':('9a2fa15836abdd2be87f1bd9cb1f5ac3b1cfc4ba6d53ba14c77b91794dce5a9e','ff4c11f8da8e0bd71038c9a10bff252c671772bb4158403b1d49c33b4f9332a5',None)}
for name,pins in nested.items():
 for filename,pin in zip(['FREEZE.json','MANIFEST.json','check.py'],pins,strict=True):
  if pin:assert sha(R/'evidence'/name/filename)==pin
for name in ['all-order','source-admission','nan-audit']:
 subprocess.run([sys.executable,'-I','-S',str(R/'evidence'/name/'check.py')],check=True,capture_output=True,text=True)
assert (R/'lean/AllOrder.lean').read_bytes()==(R/'evidence/all-order/lean/AllOrder.lean').read_bytes()
assert (R/'lean/Publication.lean').read_bytes()==(R/'evidence/source-admission/Publication.lean').read_bytes()
if a.output:
 out=a.output.resolve();assert not out.is_relative_to(R) and not out.exists(),'output outside capsule and fresh'
 subprocess.run([sys.executable,'-I','-S',str(R/'replay.py'),'--output',str(out)],check=True)
print(json.dumps({'authenticated_files':len(manifest),'nested_capsules':list(nested),'replayed':bool(a.output)}))
