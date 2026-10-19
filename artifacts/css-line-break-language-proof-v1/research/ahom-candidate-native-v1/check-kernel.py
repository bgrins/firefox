import hashlib,json,os,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'build/kernel';O.mkdir(parents=True,exist_ok=True)
tools=json.loads((R/'imports/complex-encoding-diagnostic-v1/TOOLS.json').read_text());lean=tools['lean']['path'];assert hashlib.sha256(Path(lean).read_bytes()).hexdigest()==tools['lean']['sha256']
modules={p.stem:p for p in (R/'lean/kernel').glob('*.lean')};done=[];reports=0;env=dict(os.environ,LEAN_PATH=str(O));commands=[]
def run(name,args):
 r=subprocess.run(list(map(str,args)),env=env,text=True,capture_output=True);(O/(name+'.stdout')).write_text(r.stdout);(O/(name+'.stderr')).write_text(r.stderr);commands.append({'name':name,'exit':r.returncode});assert r.returncode==0,(name,r.stdout,r.stderr);return r.stdout
while len(done)<len(modules):
 progress=False
 for name,path in modules.items():
  if name in done:continue
  s=path.read_text();deps=re.findall(r'^import (\w+)',s,re.M)
  assert all(d in modules or d in ['Std','Lean']for d in deps)
  if any(d in modules and d not in done for d in deps):continue
  assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',s)
  run(name,[lean,'-o',O/(name+'.olean'),path]);done.append(name);progress=True
  ns=[];theorems=[]
  for line in s.splitlines():
   a=re.match(r'^namespace ([\w.]+)',line);b=re.match(r'^end(?: ([\w.]+))?$',line);t=re.match(r'^(?:@\[[^]]*\]\s*)?theorem ([\w.]+)',line)
   if a:ns.append(a.group(1))
   elif b and ns:ns.pop()
   if t:theorems.append('.'.join(ns+[t.group(1)]))
  audit=O/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+n for n in theorems)+'\n');ax=run(name+'-axioms',[lean,audit]);assert 'sorryAx'not in ax
  for g in re.findall(r'depends on axioms: \[([^]]*)\]',ax):assert set(map(str.strip,g.split(',')))<={'propext','Classical.choice','Quot.sound',''}
  reports+=len(theorems)
 assert progress
raw=run('driver',[lean,'--run',modules['LFComplexStreamDriver']]);rows=[json.loads(l)for l in raw.splitlines()]
q=subprocess.run([R/'build/candidate-gecko-provider'],input=(R/'inputs/kernel-provider.txt').read_text(),text=True,capture_output=True);assert q.returncode==0 and not q.stderr;(O/'native-query.txt').write_text(q.stdout)
for row,line in zip(rows[:3],q.stdout.splitlines(),strict=True):assert ''.join(map(str,row['values']))==line
native=json.loads((R/'build/RESULT.json').read_text())['candidate']['variants']
for variant,cases in native.items():
 for key,part in [('whole','whole'),('before','before-lf'),('after','after-lf')]:assert ''.join(map(str,rows[-1][key]))==cases['ahom-'+part]['glyphs']
(O/'RESULT.json').write_text(json.dumps({'modules':len(done),'standard_axiom_reports':reports,'driver':rows,'native_query_match':True},indent=2)+'\n');print('kernel candidate witness passed',len(done),reports)
