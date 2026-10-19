import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,hashlib,json,os,stat,subprocess
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
if a.output:
 out=a.output.resolve();assert not out.is_relative_to(R) and not out.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
 d={}
 for k,v in pairs:
  assert k not in d,('duplicate JSON key',k)
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=unique)
manifest=read(R/'MANIFEST.json');files=set();directories=set()
for root,ds,fs in os.walk(R,followlinks=False):
 for name in ds+fs:
  path=Path(root)/name;mode=path.lstat().st_mode
  assert stat.S_ISREG(mode) or stat.S_ISDIR(mode),('nonregular',str(path))
  (directories if stat.S_ISDIR(mode) else files).add(str(path.relative_to(R)))
assert files==set(manifest)|{'MANIFEST.json','FREEZE.json'}
assert directories=={str(p) for n in files for p in PurePosixPath(n).parents if str(p)!='.'}
for name,pin in manifest.items():
 rel=PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts and str(rel)==name
 assert sha(R/name)==pin,name
assert read(R/'FREEZE.json')['manifest_sha256']==sha(R/'MANIFEST.json')
assert sha(R/'evidence/static/FREEZE.json')=='e497393de4571658ef3afc7f606a0e1027b4452baf436bbef3a3d4deee044534'
assert sha(R/'evidence/static/MANIFEST.json')=='b5f8a66a6c632f6bd21733c7d1aca7173ecf168b6e65bfbc9870f0be66829cd5'
subprocess.run([sys.executable,'-I','-S',str(R/'evidence/static/check.py')],check=True,capture_output=True,text=True)
records=read(R/'SOURCE-BINDING.json');assert len(records)==15
assert len({(x['source'],x['context'],x['anchor']) for x in records})==15
for item in records:
 source=(R/'evidence/static/source'/item['source']).read_text()
 start=source.index(item['anchor'],source.index(item['context']) if item['context'] else 0)
 opening=source.index('{',start);depth=0
 for end in range(opening,len(source)):
  if source[end]=='{':depth+=1
  elif source[end]=='}':
   depth-=1
   if depth==0:break
 body=source[start:end+1]
 assert body==item['body'] and start==item['start'] and hashlib.sha256(body.encode()).hexdigest()==item['sha256']
assert 'enum CompositeOperation { "replace", "add", "accumulate" };' in (R/'evidence/BaseKeyframeTypes.webidl').read_text()
if a.output:subprocess.run([sys.executable,'-I','-S',str(R/'replay.py'),'--output',str(out)],check=True)
print(json.dumps({'authenticated_files':len(manifest),'complete_native_bindings':len(records),'replayed':bool(a.output)}))
