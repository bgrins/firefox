import hashlib,json,os,re,subprocess,sys
from pathlib import Path
from controls import MUTATIONS
import source_check

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
LEAN=ROOT/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
NAMES=['rgb_transfer','native_rgb_refinement','converted_flags_preserved','no_spurious_rgb_mask','old_branch_counterexample','operand_refinement','missing_left_copies','transferred_channel_copies','both_missing_preserved','rgb_counterexample','residual_counterexample','partial_residual_not_carried']
AXIOMS={
 'rgb_transfer':'[propext, Quot.sound]', 'native_rgb_refinement':'[propext, Quot.sound]',
 'converted_flags_preserved':'[propext]', 'no_spurious_rgb_mask':'[propext]',
 'old_branch_counterexample':'[propext]', 'transferred_channel_copies':'[propext]',
 'rgb_counterexample':'[propext, Quot.sound]', 'residual_counterexample':'[propext, Quot.sound]',
 'partial_residual_not_carried':'[propext, Quot.sound]',
}
EXPECTED=''.join("'MissingComponents."+n+"' "+('depends on axioms: '+AXIOMS[n] if n in AXIOMS else 'does not depend on any axioms')+'\n' for n in NAMES)
APP='unsolved goals'
FALSE='Tactic `decide` proved that the proposition'
RFL='Tactic `rfl` failed: The left-hand side'
CONTROL_ERRORS={
 'OldEarlyReturn':[('native_rgb_refinement',APP),('old_branch_counterexample',FALSE),('transferred_channel_copies',APP)],
 'OverwriteConverted':[('native_rgb_refinement',APP),('converted_flags_preserved',APP)],
 'RedOnly':[('native_rgb_refinement',APP),('transferred_channel_copies',APP)],
 'WrongCopyDirection':[('operand_refinement',RFL),('missing_left_copies',RFL),('transferred_channel_copies',APP)],
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
 if len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--snapshots-only'):raise RuntimeError('Usage: check.py OUTPUT [--snapshots-only]')
 live=len(sys.argv)==2
 out=Path(sys.argv[1]).resolve();out.mkdir()
 model=(BASE/'Missing.lean').read_text()
 if re.search(r'\b(sorry|admit|axiom|unsafe)\b',model.replace('#print axioms','')):raise RuntimeError('Unchecked construct')
 pins=[BASE/'Missing.lean',BASE/'README.md',Path(__file__).resolve(),BASE/'controls.py',BASE/'source_check.py',BASE/'materialize.py',LEAN]+source_check.inputs(live)
 before={str(p):sha(p) for p in pins}
 binding,source_controls=source_check.run(live)
 (out/'source-binding.json').write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
 calls=[]
 def compile_case(name,text,good=False):
  d=out/name;d.mkdir();p=d/'Missing.lean';p.write_text(text)
  env=os.environ.copy();env['LEAN_PATH']=str(d);env.pop('LEAN_SRC_PATH',None)
  command=[str(LEAN),'-DwarningAsError=true','-Dlinter.unusedVariables=false','-Dlinter.unusedSimpArgs=false']
  if good:command+=['-o',str(d/'Missing.olean')]
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
 text,p,r,expected=samples['OldEarlyReturn']
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
 report={'status':'pass','live_native_verified':live,'audits':NAMES,'controls':controls,'corruptions':rejected,'source_controls':source_controls,'inputs':before,
  'outputs':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()},
  'scope':'RGB/XYZ missing-component carry branch for all eight source masks and arbitrary converted channel masks, independent category relation, generic optional-operand copy refinement. Manual source bridge; conversion numerics, same-space pipeline, alpha, residual-set implementation, parser and full Rust refinement excluded.'}
 (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'audits':len(NAMES),'controls':len(controls),'corruptions':len(rejected),'source_controls':len(source_controls)}))

if __name__=='__main__':main()
