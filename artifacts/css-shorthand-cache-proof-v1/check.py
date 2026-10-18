import hashlib,json,os,re,subprocess,sys
from pathlib import Path
from discover_controls import MUTATIONS
import source_check

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
LEAN=ROOT/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
NAMES=['populate_sound','lookup_sound','populated_lookup','hit_provenance','scan_refinement','fresh_scan_refinement','partial_rollback_counterexample','omitted_entry_counterexample']
EXPECTED=''.join("'ShorthandProvenance."+n+"' "+('does not depend on any axioms' if n.endswith('counterexample') else 'depends on axioms: [propext]')+'\n' for n in NAMES)
APP='Application type mismatch: The argument'
FALSE='Tactic `decide` proved that the proposition'
CONTROL_ERRORS={
 'UnguardedFirst':[('hit_provenance',APP),('hit_provenance',APP),('partial_rollback_counterexample',FALSE),('omitted_entry_counterexample',FALSE)],
 'UnguardedSecond':[('hit_provenance',APP),('omitted_entry_counterexample',FALSE)],
 'WrongStoredIdentity':[('populate_sound','Type mismatch'),('populated_lookup','unsolved goals'),('partial_rollback_counterexample',FALSE)],
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def positive(code,stdout,stderr):
 if code!=0 or stdout!=EXPECTED or stderr:raise RuntimeError('Positive mismatch')

def negative(source,path,code,stdout,stderr,expected):
 if code!=1 or stderr:raise RuntimeError('Negative exit/stderr mismatch')
 lines=source.splitlines()
 declarations=[(i,s) for i,s in enumerate(lines,1) if re.match(r'^(theorem |def |#print|end )',s)]
 spans={}
 for j,(start,s) in enumerate(declarations[:-1]):
  if s.startswith('theorem '):
   end=declarations[j+1][0]
   body=[i for i in range(start,end) if ':= by' in lines[i-1]]
   if not body:raise RuntimeError('Missing theorem body')
   spans[s.split()[1]]=(body[0],end)
 headers=re.findall(r'^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$',stdout,re.M)
 if len(re.findall(r'\berror(?:\([^\n)]*\))?:',stdout))!=len(headers):raise RuntimeError('Unlocated error')
 found=[]
 for filename,line,message in headers:
  if filename!=str(path):raise RuntimeError('Foreign diagnostic')
  owners=[n for n,(a,b) in spans.items() if a<=int(line)<b]
  if len(owners)!=1:raise RuntimeError('Outside theorem body')
  found.append((owners[0],message))
 if found!=expected:raise RuntimeError('Unexpected proof inventory: '+repr(found))
 return found

def main():
 if sys.flags.optimize:raise RuntimeError('Normal Python required')
 out=Path(sys.argv[1]).resolve();out.mkdir()
 model=(BASE/'Provenance.lean').read_text()
 if re.search(r'\b(sorry|admit|axiom|unsafe)\b',model.replace('#print axioms','')):raise RuntimeError('Unchecked construct')
 pins=[BASE/'Provenance.lean',BASE/'README.md',Path(__file__).resolve(),BASE/'discover_controls.py',BASE/'source_check.py',LEAN]+source_check.inputs()
 before={str(p):sha(p) for p in pins}
 binding,source_controls=source_check.run()
 (out/'source-binding.json').write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
 calls=[]
 def compile_case(name,text,good=False):
  d=out/name;d.mkdir();p=d/'Provenance.lean';p.write_text(text)
  env=os.environ.copy();env['LEAN_PATH']=str(d);env.pop('LEAN_SRC_PATH',None)
  command=[str(LEAN),'-DwarningAsError=true']
  if good:command+=['-o',str(d/'Provenance.olean')]
  command+=[str(p)]
  result=subprocess.run(command,cwd=d,env=env,capture_output=True,text=True)
  (d/'stdout').write_text(result.stdout);(d/'stderr').write_text(result.stderr)
  calls.append({'command':command,'cwd':str(d),'LEAN_PATH':str(d),'LEAN_SRC_PATH':None,'exit':result.returncode})
  return p,result
 _,good=compile_case('positive',model,True)
 positive(good.returncode,good.stdout,good.stderr)
 controls={};samples={}
 for name,errors in CONTROL_ERRORS.items():
  old,new=MUTATIONS[name]
  if model.count(old)!=1:raise RuntimeError('Mutation cardinality')
  text=model.replace(old,new);p,r=compile_case(name,text)
  controls[name]=negative(text,p,r.returncode,r.stdout,r.stderr,errors)
  samples[name]=(text,p,r,errors)
 text,p,r,expected=samples['UnguardedFirst']
 header=re.search(r'^(.+):(\d+):\d+: error: (.*)$',r.stdout,re.M).group(0)
 bad={
  'exit-zero':(0,r.stdout,''),'exit-two':(2,r.stdout,''),'stderr':(1,r.stdout,'noise'),
  'empty':(1,'',''),'foreign-file':(1,r.stdout.replace(str(p),str(p)+'-other',1),''),
  'outside-body':(1,re.sub(r':\d+:\d+: error:',':1:1: error:',r.stdout,count=1),''),
  'extra-error':(1,r.stdout+'\n'+header+'\n',''),'unlocated':(1,r.stdout+'\nerror: tool failure\n',''),
  'tagged-extra-error':(1,r.stdout+'\n'+str(p)+':1:1: error(lean.synthInstanceFailed): bad type\n',''),
  'unknown-name':(1,r.stdout.replace('error: '+APP,'error: Unknown identifier bogus',1),''),
  'parse-error':(1,r.stdout.replace('error: '+APP,'error: unexpected token',1),''),
 }
 rejected=[]
 for name,args in bad.items():
  try:negative(text,p,*args,expected)
  except RuntimeError:rejected.append(name)
  else:raise RuntimeError('Accepted negative corruption '+name)
 for name,args in {'positive-exit':(1,good.stdout,''),'positive-stderr':(0,good.stdout,'noise'),'positive-axiom':(0,good.stdout.replace('[propext]','[sorryAx]',1),'')}.items():
  try:positive(*args)
  except RuntimeError:rejected.append(name)
  else:raise RuntimeError('Accepted positive corruption '+name)
 if before!={str(p):sha(p) for p in pins}:raise RuntimeError('Inputs changed')
 (out/'commands.json').write_text(json.dumps(calls,indent=2)+'\n')
 report={'status':'pass','audits':NAMES,'controls':controls,'corruptions':rejected,'source_controls':source_controls,'inputs':before,
  'outputs':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()},
  'scope':'Tagged cache refinement for arbitrary finite eligible four-side scans, under source identity stability and fixed expansion environment. Manual source bridge, no Rust/parser/cascade eligibility refinement.'}
 (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'audits':len(NAMES),'controls':len(controls),'corruptions':len(rejected),'source_controls':len(source_controls)}))

if __name__=='__main__':main()
