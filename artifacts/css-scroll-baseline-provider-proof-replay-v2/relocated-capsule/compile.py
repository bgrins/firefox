import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, subprocess
ROOT=Path(__file__).resolve().parent
config=json.loads((ROOT/'TOOLCHAIN.json').read_text())
if hashlib.sha256(Path(config['lean']).read_bytes()).hexdigest()!=config['lean_sha256']:
    raise ValueError('Lean executable changed')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
out=args.output.resolve()
if not args.output.is_absolute() or out.exists() or out.is_relative_to(ROOT):
    raise ValueError('absent external output required')
out.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(out)
commands=[]
for name in json.loads((ROOT/'MODULES.json').read_text())+['Audit']:
    cmd=[config['lean'],'--root='+str(ROOT/'lean'),'-o',str(out/(name+'.olean')),str(ROOT/'lean'/(name+'.lean'))]
    result=subprocess.run(cmd,env=env,cwd=out,capture_output=True,text=True)
    commands.append({'module':name,'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if result.returncode or result.stderr: raise RuntimeError(result.stdout+result.stderr)
print(json.dumps({'modules':len(commands),'status':'PASS'}))
