import argparse,hashlib,json,os,re,runpy,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--manifest-sha',required=True);args=ap.parse_args()
raw=(ROOT/'MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==args.manifest_sha
manifest=json.loads(raw)
for name,digest in manifest['files'].items():
 relative=Path(name);assert not relative.is_absolute()and '..'not in relative.parts
 path=ROOT/relative;assert not path.is_symlink()and path.resolve().is_relative_to(ROOT);assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
lean=Path(args.lean).resolve();tool=json.loads((ROOT/'TOOL.json').read_text());assert hashlib.sha256(lean.read_bytes()).hexdigest()==tool['sha256'];version=subprocess.check_output([lean,'--version'],text=True);assert tool['version_contains']in version
out=ROOT/'build';out.mkdir(exist_ok=True);env=dict(os.environ,LEAN_PATH=str(out));commands=[];reports=[]
def run(name,command):
 r=subprocess.run(list(map(str,command)),env=env,capture_output=True,text=True,timeout=300);(out/(name+'.log')).write_text(r.stdout+r.stderr);commands.append({'name':name,'exit':r.returncode});(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert r.returncode==0 and not r.stderr,(name,r.stdout,r.stderr);assert 'sorryAx'not in r.stdout and 'declaration uses' not in r.stdout
 return r.stdout
modules={p.stem:p for p in (ROOT/'lean').glob('*.lean')};done=[]
while len(done)<len(modules):
 progress=False
 for name,path in modules.items():
  if name in done:continue
  dependencies=re.findall(r'^import (\w+)',path.read_text(),re.M)
  if any(d in modules and d not in done for d in dependencies):continue
  assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',path.read_text()),name
  run(name,[lean,'-o',out/(name+'.olean'),path]);done.append(name);progress=True
 assert progress
for name,path in modules.items():
 ns=re.findall(r'^namespace (\w+)',path.read_text(),re.M);prefix=ns[0]+'.'if ns else'';names=re.findall(r'^theorem ([\w.]+)',path.read_text(),re.M)
 audit=out/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+prefix+n for n in names)+'\n');output=run(name+'Axioms',[lean,audit]);reports.extend(output.splitlines())
 for group in re.findall(r'depends on axioms: \[([^]]*)\]',output):assert set(map(str.strip,group.split(',')))<={'propext','Classical.choice','Quot.sound',''}
for name in ['PolicyMutation','ResolverMutation','ProjectionMutation','MutationWitness','PartitionCounterexamples','AstralWitness']:
 if re.search(r'^def main',modules[name].read_text(),re.M):run(name+'-run',[lean,'--run',modules[name]])
parse=runpy.run_path(str(ROOT/'observations.py'))['native_observations'];expected=parse((ROOT/'evidence/ownership-lean-native.txt').read_text())
output=run('stream-replay',[lean,'--run',modules['StreamDriver'],ROOT/'evidence/ownership-lean-fixtures.json']);actual=list(map(json.loads,output.splitlines()))
for case in actual:
 for step in case['steps']:
  for item in step['state']['items']:
   if item['owner']is None:item['offset']=0
assert actual==expected
result={'manifest_sha256':args.manifest_sha,'files':len(manifest['files']),'modules':len(done),'theorem_reports':len(reports),'cases':len(actual),'operations':sum(len(c['steps'])for c in actual),'events':sum(len(s['events'])for c in actual for s in c['steps']),'status':'Lean source-only replay and retained native-observation comparison passed; native providers not rebuilt by this component checker','commands':commands}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='commands'}))
