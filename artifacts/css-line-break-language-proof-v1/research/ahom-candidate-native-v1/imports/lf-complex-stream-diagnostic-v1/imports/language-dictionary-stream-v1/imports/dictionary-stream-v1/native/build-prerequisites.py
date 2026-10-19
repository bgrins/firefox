import json
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build'
RUST=OUT/'rust'
RUST.mkdir(parents=True,exist_ok=True)
commands=[]
def run(name,args,cwd=None,env=None):
    args=list(map(str,args))
    result=subprocess.run(args,cwd=cwd,env=env,stdout=(OUT/(name+'.log')).open('w'),stderr=subprocess.STDOUT,timeout=180)
    commands.append({'name':name,'args':args,'cwd':str(cwd)if cwd else None,'exit':result.returncode})
    (OUT/'prerequisite-receipt.json').write_text(json.dumps(commands,indent=2)+'\n')
    print(name,result.returncode,flush=True)
    if result.returncode:raise SystemExit(result.returncode)
tools=json.loads((ROOT/'TOOLS.json').read_text());rustc=tools['rustc']
for name,edition,extra in [
    ('arrayref','2015',[]),('log','2021',[]),('libc','2021',['--cfg','feature="std"']),
    ('memmap2','2021',['--extern',f'libc={RUST}/liblibc.rlib']),
    ('mapped_hyph','2018',['--extern',f'arrayref={RUST}/libarrayref.rlib','--extern',f'log={RUST}/liblog.rlib','--extern',f'memmap2={RUST}/libmemmap2.rlib']),
]:
    final=name=='mapped_hyph'
    run('prerequisite-'+name,[rustc,'--edition',edition,'--crate-name',name,'--crate-type','staticlib'if final else'rlib','-L',f'dependency={RUST}',ROOT/'source/vendor'/name/'src/lib.rs','-o',RUST/('lib'+name+('.a'if final else'.rlib')),*extra])
env=dict(os.environ);env['CARGO_HOME']=str(OUT/'cargo-home');env['RUSTC']=rustc
run('prerequisite-icu',[tools['cargo'],'build','--locked','--offline','--target-dir',OUT/'icu'],cwd=ROOT/'provider-bridge-v1/icu',env=env)
