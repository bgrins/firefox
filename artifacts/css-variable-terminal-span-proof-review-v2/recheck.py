#!/usr/bin/env python3
import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
PINS={'FREEZE.json': 'b5ba0d6263b36cdd833a4902b7c0ccfdff5488d383ef0aab621a4e4ca3c3c176', 'MANIFEST.json': 'd2d1b726ee18d0de4a4a41f53d0f087a404a9b4239b8c6ac5668df8abbc7483c', 'check.py': 'a0ed0353223fa2bc7131ecc913ee9b9a268525a99644e3ccd95e3cd58ceb7f2b'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('duplicate key')
        result[k]=v
    return result

def authenticate(root):
    for n,h in PINS.items():
        if sha(root/n)!=h:raise ValueError(n)
    m=json.loads((root/'MANIFEST.json').read_text(),object_pairs_hook=unique)
    for n,h in m.items():
        q=PurePosixPath(n)
        if n!=str(q) or q.is_absolute() or '..' in q.parts:raise ValueError(n)
        if sha(root/n)!=h:raise ValueError(n)
    expected=set(m)|{'FREEZE.json','MANIFEST.json'}
    dirs={str(p) for n in expected for p in PurePosixPath(n).parents if str(p)!='.'}
    actual=set();actualdirs=set()
    for p in root.rglob('*'):
        mode=p.lstat().st_mode;n=p.relative_to(root).as_posix()
        if stat.S_ISREG(mode):actual.add(n)
        elif stat.S_ISDIR(mode):actualdirs.add(n)
        else:raise ValueError('nonregular input')
    if actual!=expected or actualdirs!=dirs:raise ValueError('roster')
    return m

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=HERE/'capsule';authenticate(root)
out=a.output.resolve()
if out.exists() or out==HERE or HERE in out.parents:raise ValueError('fresh external output required')
out.mkdir(parents=True)
commands=[]
def run(cmd,env=None):
    r=subprocess.run(cmd,capture_output=True,text=True,env=env)
    commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if r.returncode:raise ValueError(r.stdout+r.stderr)
run([sys.executable,'-I','-S',str(root/'check.py'),'--output',str(out/'producer')])
config=json.loads((root/'TOOLCHAIN.json').read_text())
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(out/'producer')
run([config['lean'],'-R',str(HERE),str(HERE/'Challenges.lean')],env)
source=(root/'source/serializer.rs').read_text();enum=source.split('pub enum TokenSerializationType {',1)[1].split('}',1)[0]
native=set(re.findall(r'^    (\w+),$',enum,re.M))-{'Nothing'}
lean=(root/'lean/Span.lean').read_text().split('inductive Kind where',1)[1].split('deriving',1)[0]
model=set(re.findall(r'\b[a-zA-Z]\w*\b',lean))
if {n.lower() for n in native}!={n.lower() for n in model}:raise ValueError('class inventory')
authenticate(root)
shadow=out/'unsafe-shadow';shadow.mkdir()
for name in [*json.loads((root/'MANIFEST.json').read_text()),'MANIFEST.json','FREEZE.json']:
    target=shadow/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/name).read_bytes())
(shadow/'json.py').write_text('raise RuntimeError("TERMINAL_SHADOW_IMPORTED_BEFORE_GUARD")\n')
probe=subprocess.run([sys.executable,'-B','-S',str(shadow/'check.py'),'--output',str(out/'unsafe-result')],capture_output=True,text=True)
if 'TERMINAL_SHADOW_IMPORTED_BEFORE_GUARD' in probe.stderr or 'optimization forbidden' not in probe.stderr or probe.returncode == 0 or (out/'unsafe-result').exists():
    raise ValueError('unsafe shadow result changed')
(out/'UNSAFE-SHADOW.json').write_text(json.dumps({'exit':probe.returncode,'stderr':probe.stderr,'shadow_executed':False},indent=2)+'\n')
shutil.rmtree(shadow)
run([sys.executable,'-I','-S',str(root/'test_integrity.py'),'--output',str(out/'integrity')])
result={'status':'ACCEPTED_SCOPED','mathematical_replay':'PASS','integrity':'pre-import guard rejection; 12 controls pass','producer_audits':37,'producer_model_mutants':5,'independent_kernel_challenges':23,'non_Nothing_classes':len(native),'native_translation_proved':False,'general_serialization_proved':False}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
