import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, subprocess
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--olean',type=Path,required=True);args=p.parse_args()
out=args.output.resolve()
if not args.output.is_absolute() or out.exists() or out.is_relative_to(ROOT): raise ValueError('external absent output')
out.mkdir(parents=True)
config=json.loads((ROOT/'TOOLCHAIN.json').read_text())
if hashlib.sha256(Path(config['lean']).read_bytes()).hexdigest()!=config['lean_sha256']: raise ValueError('tool pin')
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(args.olean.resolve())
results=[]
for name,left,right in json.loads((ROOT/'MODEL-MUTANTS.json').read_text()):
    source='import Witnesses\nopen FlexRelativeWitnesses\nexample : '+left+' = '+right+' := by decide +kernel\n'
    file=out/(name+'.lean');file.write_text(source)
    cmd=[config['lean'],str(file)];result=subprocess.run(cmd,env=env,cwd=out,capture_output=True,text=True)
    if not result.returncode or 'decide' not in result.stdout or 'false' not in result.stdout or result.stderr:
        raise ValueError('not the intended semantic rejection: '+result.stdout+result.stderr)
    results.append({'name':name,'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
      'compiled_witness':'Witnesses.lean contains the independently kernel-checked inequality for this exact pair'})
(out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({'rejected':len(results)}))
