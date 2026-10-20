import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S, without optimization')
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess
root = Path(__file__).resolve().parent
config=json.loads((root/'TOOLCHAIN.json').read_text())
lean=Path(config['lean'])
if hashlib.sha256(lean.read_bytes()).hexdigest()!=config['lean_sha256']:raise RuntimeError('toolchain mismatch')
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('targets',nargs='+');args=parser.parse_args()
src=root/'lean';out=args.output.resolve()
if out==root or root in out.parents:raise RuntimeError('external output required')
out.mkdir(parents=True,exist_ok=False)
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(out)
commands=[];done=set()
def run(command):
    r=subprocess.run(command,cwd=src,env=env,text=True,capture_output=True)
    commands.append(dict(command=command,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    return r.stdout
def build(module):
    if module in done:return
    if module == 'Std' or module.startswith('Std.') or module == 'Lean' or module.startswith('Lean.'):
        return
    p=src/(module+'.lean')
    for d in re.findall(r'^import ([\w.]+)',p.read_text(),re.M):build(d)
    run([str(lean),'--root='+str(src),'-o',str(out/(module+'.olean')),str(p)])
    done.add(module)
for module in args.targets:build(module)
print(json.dumps({'modules':len(done),'targets':args.targets}))
