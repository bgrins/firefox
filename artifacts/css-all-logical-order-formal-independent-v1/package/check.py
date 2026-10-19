import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,hashlib,json,subprocess,os,stat
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique_object(pairs):
 result={}
 for key,value in pairs:
  assert key not in result,('duplicate JSON key',key)
  result[key]=value
 return result
records=json.loads((R/'MANIFEST.json').read_text(),object_pairs_hook=unique_object);seen=set()
for row in records:
 name=row['path'];rel=PurePosixPath(name)
 assert not rel.is_absolute() and '..' not in rel.parts and str(rel)==name and name not in seen
 seen.add(name);path=R/name
 assert path.is_file() and not path.is_symlink()
 for parent in path.parents:
  if parent==R:break
  assert not parent.is_symlink()
 assert sha(path)==row['sha256'],name
expected_dirs=set()
for name in seen:
 for parent in PurePosixPath(name).parents:
  if str(parent)!='.':expected_dirs.add(str(parent))
actual=set();actual_dirs=set()
for root,dirs,files in os.walk(R,followlinks=False):
 for name in dirs+files:
  path=Path(root)/name;mode=path.lstat().st_mode;relative=str(path.relative_to(R))
  assert stat.S_ISREG(mode) or stat.S_ISDIR(mode),('nonregular entry',relative)
  if stat.S_ISDIR(mode):actual_dirs.add(relative)
  else:actual.add(relative)
assert actual-{'MANIFEST.json','FREEZE.json'}==seen
assert actual_dirs==expected_dirs
freeze=json.loads((R/'FREEZE.json').read_text(),object_pairs_hook=unique_object)
assert freeze['manifest_sha256']==sha(R/'MANIFEST.json')
D=R/'evidence/static'
assert sha(D/'MANIFEST.json')=='024b70615a12e04c8f2f12f23a1622bbcaf32ed474e0d3a294421bf573bc3694'
assert sha(D/'FREEZE.json')=='c4ee40b2c294e6765bfea27e5610adc0b3c05a9b3ef942e2dbde296d85a78931'
assert sha(D/'check.py')=='c196597f87d73dc76a46fbf34669d0b5df54e297c08e64031cb130fb82f70848'
subprocess.run([sys.executable,'-I','-S',str(D/'check.py')],check=True)
assert sha(R/'evidence/declaration_block.original.rs')=='7239be79e4864599f55b5d8898f682366290900ff484b63ce491b5b221bd3f6c'
assert sha(R/'evidence/declaration_block.candidate.rs')=='8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a'
for name in ['data.py','longhands.toml','shorthands.toml']:
 assert (R/'evidence/provider'/name).read_bytes()==(D/'evidence/source/servo/components/style/properties'/name).read_bytes()
if a.output:
 out=a.output.resolve();assert not out.is_relative_to(R) and not out.exists()
 subprocess.run([sys.executable,'-I','-S',str(R/'replay.py'),'--output',str(out)],check=True)
print(json.dumps({'authenticated_files':len(records),'nested_static_authenticated':True,'candidate_binding':True}))
