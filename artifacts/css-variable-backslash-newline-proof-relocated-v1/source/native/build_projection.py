import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
config=json.loads((ROOT/'TOOLCHAIN.json').read_text());rustc=Path(config['rustc'])
if hashlib.sha256(rustc.read_bytes()).hexdigest()!=config['rustc_sha256']:raise RuntimeError('rustc pin')
out.mkdir(parents=True,exist_ok=False)
commands=[]
def run(cmd,stdin=None):
    result=subprocess.run(cmd,cwd=out,text=True,capture_output=True,input=stdin)
    commands.append({'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if result.returncode:raise RuntimeError(result.stderr)
    return result.stdout
for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[]),('cssparser','2024',['dtoa_short','itoa','smallvec'])]:
    crate=name.replace('-','_');cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-L','dependency='+str(out),str(ROOT/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
    for dep in deps:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
    run(cmd)
run([str(rustc),'--edition','2024','-L','dependency='+str(out),'--extern','cssparser='+str(out/'libcssparser.rlib'),str(ROOT/'native/projection.rs'),'-o',str(out/'projection')])
cases=json.loads((ROOT/'native/CASES.json').read_text());raw=run([str(out/'projection')],''.join(c['css'].encode().hex()+'\n' for c in cases));(out/'PROJECTION.jsonl').write_text(raw)
print(json.dumps({'cases':len(cases),'complete':True}))
