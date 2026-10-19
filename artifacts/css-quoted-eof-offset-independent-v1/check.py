import sys
assert sys.flags.isolated and sys.flags.no_site, 'Run with python3 -I -S -B'
import argparse, collections, hashlib, json, os, re, shutil, subprocess, tempfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--replay-output',type=Path);a=p.parse_args()
def pairs(xs):
 d={}
 for k,v in xs:
  assert k not in d, ('duplicate',k)
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
raw=(ROOT/'MANIFEST.json').read_bytes();assert H(raw)==a.manifest
manifest=json.loads(raw,object_pairs_hook=pairs)
seen=set()
for name,digest in manifest.items():
 q=PurePosixPath(name);assert not q.is_absolute() and str(q)==name and '..' not in q.parts
 assert name.casefold() not in seen;seen.add(name.casefold())
 path=ROOT/name
 for ancestor in [path,*path.parents]:assert not ancestor.is_symlink(),str(ancestor)
 assert path.is_file() and H(path.read_bytes())==digest,name
for label,mp,fp in [('design','f894fa724dde514ba02d4ac0af5eb847c4001af1e919a069e249c995e1aae643','b9f1f614651f5ca061bddb223f3da89c6a1e37e2a37e23f4a66df24cbb64f0ef'),('formatted','fd0ca7ff03181b3a9438446631246da138170a5996a6bf2039c1b985e071fa9d','8b34c97523fc36b617ca0bc6078705aced6654b21789d583368bd431234e45b4')]:
 cap=ROOT/'evidence'/label
 assert H((cap/'MANIFEST.json').read_bytes())==mp and H((cap/'FREEZE.json').read_bytes())==fp
 for n,d in read(cap/'MANIFEST.json').items():assert H((cap/n).read_bytes())==d
b=ROOT/'evidence/browser';d=ROOT/'evidence/design';f=ROOT/'evidence/formatted'
assert (d/'source/custom_properties.rs').read_bytes()==(f/'original.rs').read_bytes()==(b/'custom_properties.original.rs').read_bytes()
assert (d/'candidate/custom_properties.rs').read_bytes()==(f/'proposed.rs').read_bytes()==(b/'custom_properties.candidate.rs').read_bytes()
assert (f/'formatted.rs').read_bytes()==(b/'custom_properties.formatted.rs').read_bytes()
patch=(ROOT/'evidence/root/fix.patch').read_bytes();assert H(patch)=='3ddc72ba87dfe762bb42e88b781ae844ee48cb4750a6d1c20bf4513527b16076'
# Apply exact context hunks without Git or touching the checkout.
def apply_patch(text,body):
 src=text.splitlines(True);dst=[];pos=0;lines=body.splitlines(True);i=0
 while i<len(lines):
  line=lines[i]
  if not line.startswith('@@ '):i+=1;continue
  m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',line);assert m,line
  start=int(m[1]);oldcount=int(m[2] or 1);newcount=int(m[4] or 1);at=start-1 if oldcount else start
  assert at>=pos;dst+=src[pos:at];pos=at;i+=1;oc=nc=0
  while i<len(lines) and not lines[i].startswith('@@ '):
   l=lines[i]
   if l.startswith(('--- ','+++ ','diff ','index ','new file ')):break
   if l.startswith(' '):assert src[pos]==l[1:];dst.append(l[1:]);pos+=1;oc+=1;nc+=1
   elif l.startswith('-'):assert src[pos]==l[1:];pos+=1;oc+=1
   elif l.startswith('+'):dst.append(l[1:]);nc+=1
   else:raise AssertionError(l)
   i+=1
  assert (oc,nc)==(oldcount,newcount)
 dst+=src[pos:];return ''.join(dst)
sections=patch.decode().split('diff --git ')[1:];assert len(sections)==2
assert apply_patch((f/'original.rs').read_text(),sections[0])==(f/'formatted.rs').read_text()
assert apply_patch('',sections[1])==(b/'quoted-eof-fallback-endpoints.html').read_text()
key=lambda r:(r['action'],r['test'],r.get('subtest'))
rows={}
for name in ['baseline','candidate']:
 before=read(b/(name+'-before.json'));after=read(b/(name+'-after.json'));assert before==after
 rr=[r for r in [json.loads(x) for x in (b/(name+'-raw.jsonl')).read_text().splitlines()] if r.get('action') in ['test_status','test_end']]
 rows[name]={key(r):r for r in rr};assert len(rows[name])==len(rr)
 summary=read(b/(name+'-result.json'))
 assert summary['raw_sha256']==H((b/(name+'-raw.jsonl')).read_bytes())
 assert summary['console_sha256']==H((b/(name+'-console.log')).read_bytes())
 assert {key(r):r['status'] for r in rr}=={key(r):r['status'] for r in summary['rows']}
new='/css/css-variables/quoted-eof-fallback-endpoints.html'
oldnew=[r for k,r in rows['baseline'].items() if k[1]==new];assert len(oldnew)==1 and oldnew[0]['status']=='CRASH'
newnew=[r for k,r in rows['candidate'].items() if k[1]==new];assert collections.Counter(r['status'] for r in newnew)=={'PASS':38,'OK':1}
oldother={k:(r['status'],r.get('expected')) for k,r in rows['baseline'].items() if k[1]!=new}
newother={k:(r['status'],r.get('expected')) for k,r in rows['candidate'].items() if k[1]!=new}
assert oldother==newother and len(oldother)==34
bp=read(b/'baseline-before.json');cp=read(b/'candidate-before.json')
source='servo/components/style/custom_properties.rs';wpt='testing/web-platform/tests'+new
assert bp['fixed'][source]==H((f/'original.rs').read_bytes())
assert cp['fixed'][source]==H((f/'formatted.rs').read_bytes())
assert bp['fixed'][wpt]==cp['fixed'][wpt]==H((b/'quoted-eof-fallback-endpoints.html').read_bytes())
assert {k:v for k,v in bp['fixed'].items() if k!=source}=={k:v for k,v in cp['fixed'].items() if k!=source}
commands=read(ROOT/'receipts/producer-COMMANDS.json')
lean=[x for x in commands if x['command'][-1].endswith('/Endpoints.lean')][0]
assert lean['exit']==0 and 'sorryAx' not in lean['stdout'] and 'warning:' not in lean['stdout']
allowed={'propext','Quot.sound','Classical.choice'}
for line in lean['stdout'].splitlines():
 if 'depends on axioms:' in line:assert set(re.search(r'\[(.*)\]',line)[1].split(', '))<=allowed
assert read(ROOT/'receipts/producer-RESULT.json')['cases']==40
assert read(ROOT/'challenge-result/RESULT.json')['cases']==360
for variant in ['original','candidate','missing-correction-mutant']:
 rs=[json.loads(x) for x in (ROOT/'challenge-result'/(variant+'.jsonl')).read_text().splitlines()];assert len(rs)==360
if a.replay_output:
 out=a.replay_output.resolve();assert not out.exists();out.mkdir(parents=True)
 env=os.environ.copy()
 for n in ['PYTHONPATH','PYTHONHOME','LEAN_PATH']:env.pop(n,None)
 env.update(PYTHONSAFEPATH='1',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
 cap=out/'capsule';cap.mkdir()
 for name in [*read(d/'MANIFEST.json'),'MANIFEST.json','FREEZE.json']:
  dest=cap/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(d/name,dest)
 env['PYTHONPATH']=str(cap/'native')
 calls=[[sys.executable,'-I','-S','-B',str(cap/'check.py'),'--output',str(out/'producer')], [sys.executable,'-I','-S','-B',str(ROOT/'challenge.py'),str(out/'producer/native'),str(out/'challenge')], [sys.executable,'-I','-S','-B',str(f/'check.py')]]
 for i,cmd in enumerate(calls):
  r=subprocess.run(cmd,cwd=out,env=env,text=True,capture_output=True)
  (out/f'command-{i}.json').write_text(json.dumps({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
  assert r.returncode==0,r.stdout+r.stderr
print(json.dumps({'status':'PASS','authenticated_files':len(manifest),'producer_cases':40,'independent_cases':360,'browser_new':38,'unchanged_other_outcomes':34,'scope':'H1 conditional endpoint arithmetic and bounded native/browser evidence'}))
