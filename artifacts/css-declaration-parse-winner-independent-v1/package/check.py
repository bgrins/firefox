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
deps=read(R/'DEPENDENCIES.json')
for name,pin in deps['public_storage'].items():
 path=R/'evidence/public-storage'/name;assert sha(path)==pin['sha256']
 if name.startswith('lean/'):assert (R/name).read_bytes()==path.read_bytes()
assert sha(R/'lean/AllOrder.lean')=='b527603856f4c58547c5ae5eef804940554b3d7fc465ed6eaf47243c9775a0a7'
assert sha(R/'lean/PublicStorage.lean')=='bfb925b31038f5615f352d0debbd4bb538a1a35576759b8ba6be047d5c12399f'
for name in ['MANIFEST.json','FREEZE.json']:
 assert sha(R/'evidence/public-operations'/name)==deps['public_operations_'+name.split('.')[0].lower()+'_sha256']
subprocess.run([sys.executable,'-I','-S',str(R/'evidence/public-operations/check.py')],check=True,capture_output=True,text=True)
binding=read(R/'SOURCE-BINDING.json');source=(R/'evidence/public-operations/source/servo/components/style/properties/declaration_block.rs').read_text()
assert hashlib.sha256(source.encode()).hexdigest()==binding['source_sha256']
assert [item['function'] for item in binding['complete_functions']]==['extend','push']
for item in binding['complete_functions']:
 start=source.index('    pub fn '+item['function']+'(');opening=source.index('{',start);depth=0
 for end in range(opening,len(source)):
  if source[end]=='{':depth+=1
  elif source[end]=='}':
   depth-=1
   if depth==0:break
 body=source[start:end+1]
 assert body==item['body'] and start==item['start'] and hashlib.sha256(body.encode()).hexdigest()==item['sha256']
assert 'changed |= self.push(decl, importance);' in source
assert 'changed | self.push(decl, importance)' in source
assert 'if important && !importance.important()' in binding['complete_functions'][1]['body']
if a.output:subprocess.run([sys.executable,'-I','-S',str(R/'replay.py'),'--output',str(out)],check=True)
print(json.dumps({'authenticated_files':len(manifest),'source_functions':2,'replayed':bool(a.output)}))
