from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile
P=Path(__file__).resolve().parent
LEAN=P.parents[1]/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert hashlib.sha256(LEAN.read_bytes()).hexdigest()=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=P/'check';out.mkdir(exist_ok=False)
records=[]
with tempfile.TemporaryDirectory(prefix='provider-owner-witness-') as tmp:
 scratch=Path(tmp);env=dict(os.environ,LEAN_PATH=str(scratch))
 for source in P.glob('*.lean'):shutil.copyfile(source,scratch/source.name)
 for name in ['Ownership','Audit','FalseForeignResume','FalseForeignRelease']:
  args=[str(LEAN),'-j1']
  if name=='Ownership':args+=['-o','Ownership.olean']
  args+=[name+'.lean']
  result=subprocess.run(args,cwd=scratch,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
  (out/(name+'.log')).write_text(result.stdout)
  if name.startswith('False'):
   assert result.returncode!=0 and 'proved that the proposition' in result.stdout and 'false' in result.stdout,result.stdout
  else:assert result.returncode==0 and 'sorryAx' not in result.stdout and 'Lean.ofReduceBool' not in result.stdout,result.stdout
  records.append({'name':name,'exit':result.returncode})
(out/'RESULT.json').write_text(json.dumps({'theorems':6,'false_controls':2,'records':records,'scratch_removed':not scratch.exists()},indent=2)+'\n')
print(json.dumps({'theorems':6,'false_controls':2,'scratch_removed':not scratch.exists()}))
