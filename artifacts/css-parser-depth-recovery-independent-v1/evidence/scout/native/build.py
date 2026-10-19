import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
config = json.loads((ROOT/'TOOLCHAIN.json').read_text())
rustc = Path(config['rustc'])
assert hashlib.sha256(rustc.read_bytes()).hexdigest() == config['rustc_sha256']
commands = []

def run(cmd, stdin=None):
    r = subprocess.run(cmd, cwd=out, input=stdin, capture_output=True, text=True)
    commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert r.returncode == 0, r.stderr
    return r.stdout

for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[]),('bitflags','2021',[]),('cssparser','2024',['dtoa-short','itoa','smallvec'])]:
    crate=name.replace('-','_')
    cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-C','opt-level=1','-L','dependency='+str(out),str(ROOT/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
    for d in deps:
        d=d.replace('-','_');cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
    run(cmd)


run([str(rustc),'--edition','2024','-C','opt-level=1','-L','dependency='+str(out),'--extern','cssparser='+str(out/'libcssparser.rlib'),str(ROOT/'native/witness.rs'),'-o',str(out/'witness')])
raw=run([str(out/'witness')]);(out/'OBSERVATIONS.jsonl').write_text(raw);print(raw)
