import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path, PurePosixPath
assert sys.flags.isolated and sys.flags.no_site, 'invoke python3 -I -S'
ROOT = Path(__file__).resolve().parent
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
 d = {}
 for k,v in pairs:
  assert k not in d, 'duplicate JSON key'
  d[k] = v
 return d
def read(p): return json.loads(p.read_text(), object_pairs_hook=unique)
def authenticate():
 assert not Path(__file__).is_symlink()
 seal=read(ROOT/'FREEZE.json');manifest=read(ROOT/'MANIFEST.json')
 assert digest(ROOT/'MANIFEST.json')==seal['manifest_sha256']
 assert digest(ROOT/'check.py')==seal['checker_sha256']
 expected=set(manifest)|{'MANIFEST.json','FREEZE.json'}
 dirs=set()
 for name in expected:
  p=PurePosixPath(name)
  assert not p.is_absolute() and all(x not in ('','.','..') for x in p.parts)
  assert str(p)==name
  dirs.update(str(q) for q in p.parents if str(q)!='.')
 actual=set();actual_dirs=set()
 for p in ROOT.rglob('*'):
  assert not p.is_symlink(), 'symlink input'
  n=str(p.relative_to(ROOT))
  if p.is_file():actual.add(n)
  elif p.is_dir():actual_dirs.add(n)
  else:raise AssertionError('nonregular input')
 assert actual==expected, ('file roster',actual^expected)
 assert actual_dirs==dirs, ('directory roster',actual_dirs^dirs)
 for name,sha in manifest.items():assert digest(ROOT/name)==sha, name
 return manifest
manifest=authenticate()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert out!=ROOT and not out.is_relative_to(ROOT)
assert not out.exists(), 'fresh external output required'
config=read(ROOT/'TOOLCHAIN.json')
for name in ['lean','rustc']:assert digest(Path(config[name]))==config[name+'_sha256']
lean_root=Path(config['lean']).parents[1]
for name,sha in read(ROOT/'TOOLCHAIN-LIBRARY.json').items():assert digest(lean_root/name)==sha,name
for item in read(ROOT/'SOURCE-BINDINGS.json'):
 s=(ROOT/item['file']).read_text();starts=[m.start() for m in re.finditer(re.escape(item['definition']),s)];start=s.rfind('\n',0,starts[item['occurrence']])+1;end=s.index('\n    }',start)+len('\n    }');text=s[start:end]
 assert text==item['text'] and hashlib.sha256(text.encode()).hexdigest()==item['sha256']
out.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_','RUSTFLAGS'))}
records=[]
def run(cmd):
 r=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True)
 records.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n')
 assert r.returncode==0,r.stdout+r.stderr
 return r.stdout
source=(ROOT/'lean/Boundary.lean').read_text();assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',source)
names=read(ROOT/'AUDITS.json');assert names==['Boundary.'+n for n in re.findall(r'^theorem (\w+)',source,re.M)]
audit=out/'Audit.lean';audit.write_text(source+'\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
log=run([config['lean'],str(audit)])
reports=re.findall(r"'(Boundary\.\w+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",log,re.S)
assert len(reports)==len(names),(len(reports),log)
assert [x[0] for x in reports]==names
for _,terms in reports:
 assert set(re.findall(r'\w+(?:\.\w+)*',terms))<={'propext','Quot.sound','Classical.choice'},terms
run([sys.executable,'-I','-S',str(ROOT/'native/build.py'),'--output',str(out/'native')])
authenticate()
result={'status':'PASS','inputs':len(manifest),'lean_modules':1,'theorem_audits':len(names),'source_bindings':len(read(ROOT/'SOURCE-BINDINGS.json')),'native':read(out/'native/RESULT.json'),'scope':'conditional event-to-boundary theorem; finite actual native parser bridge'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
