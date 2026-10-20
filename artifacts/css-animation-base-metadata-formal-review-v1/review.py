import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
import argparse,hashlib,json,os,shutil,stat,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(items):
 out={}
 for k,v in items:
  assert k not in out,k
  out[k]=v
 return out
def read(p):return json.loads(p.read_text(),object_pairs_hook=unique)
def authenticate(root,pins):
 for n,h in pins.items():assert sha(root/n)==h,n
 m=read(root/'MANIFEST.json');assert sha(root/'MANIFEST.json')==read(root/'FREEZE.json')['manifest_sha256']
 files=set(m)|{'FREEZE.json','MANIFEST.json'};dirs=set()
 for n in files:
  p=Path(n);assert not p.is_absolute() and '..' not in p.parts and str(p)==n
  dirs.update(str(q) for q in p.parents if str(q)!='.')
 af=set();ad=set()
 for p in root.rglob('*'):
  assert not p.is_symlink();mode=p.stat().st_mode
  if stat.S_ISDIR(mode):ad.add(str(p.relative_to(root)))
  else:assert stat.S_ISREG(mode);af.add(str(p.relative_to(root)))
 assert af==files and ad==dirs
 for n,h in m.items():assert sha(root/n)==h,n
 return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--producer',type=Path,required=True);a=ap.parse_args();p=a.producer.resolve()
 pins=read(R/'PRODUCER-PINS.json');m=authenticate(p,pins)
 env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
 with tempfile.TemporaryDirectory(prefix='base-formal-independent-',dir='/private/tmp') as temp:
  t=Path(temp);c=t/'capsule';c.mkdir()
  for n in list(m)+['FREEZE.json','MANIFEST.json']:
   q=c/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/n,q)
  authenticate(c,pins)
  q=subprocess.run([sys.executable,'-I','-S',str(c/'check.py'),'--output',str(t/'compiled')],cwd=t,env=env,capture_output=True,text=True)
  assert q.returncode==0,q.stdout+q.stderr
  result=read(t/'compiled/CHECK.json');assert result['axiom_reports']==23 and result['source_bindings']==14
  assert result['native_execution'] is False
  lean=Path(read(c/'TOOLCHAIN.json')['lean']);shutil.copyfile(R/'Review.lean',t/'compiled/Review.lean')
  q=subprocess.run([str(lean),'Review.lean'],cwd=t/'compiled',env=dict(env,LEAN_PATH=str(t/'compiled')),capture_output=True,text=True)
  assert q.returncode==0,q.stdout+q.stderr
  lines=q.stdout.strip().splitlines();assert len(lines)==7,q.stdout
  assert all(line.endswith('depends on axioms: [propext]') for line in lines[:6]),q.stdout
  assert lines[-1].endswith('does not depend on any axioms'),q.stdout
  independent=q.stdout;guards=[]
  def reject(name):
   q=subprocess.run([sys.executable,'-I','-S',str(c/'check.py'),'--output',str(t/('bad-'+name))],cwd=t,env=env,capture_output=True,text=True)
   assert q.returncode!=0,name
   assert not (t/('bad-'+name)).exists(),name
   guards.append({'name':name,'exit':q.returncode,'rejected_before_output':True})
  f=c/'lean/BaseModel.lean';b=f.read_bytes();f.write_bytes(b+b'\n');reject('changed-model');f.write_bytes(b)
  f=c/'lean/Std.lean';f.write_text('');reject('shadow-module');f.unlink()
  f=c/'empty-extra';f.mkdir();reject('extra-directory');f.rmdir()
  f=c/'link';f.symlink_to('REPORT.md');reject('symlink');f.unlink()
  f=c/'MANIFEST.json';b=f.read_bytes();s=b.decode();key=next(iter(m));f.write_text('{'+json.dumps(key)+':'+json.dumps(m[key])+','+s[1:]);reject('duplicate-manifest-key');f.write_bytes(b)
  f=c/'FIFO';os.mkfifo(f);reject('fifo');f.unlink()
  authenticate(c,pins)
  print(json.dumps({'producer_inputs':len(m),'producer_result':result,'independent_axioms':independent,'guards':guards,'status':'ACCEPT_SCOPED_MODEL'},indent=2))
if __name__=='__main__':main()
