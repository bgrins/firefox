import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--release',action='store_true');p.add_argument('--mutation');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
BASE=ROOT
config=json.loads((BASE/'TOOLCHAIN.json').read_text());rustc=Path(config['rustc']);assert hashlib.sha256(rustc.read_bytes()).hexdigest()==config['rustc_sha256']
commands=[]
mode_flags=['-C','opt-level=2','-C','debug-assertions=off'] if a.release else []
def run(cmd,stdin=None,cwd=None,env=None):
 if cmd[0]==str(rustc):cmd=cmd+mode_flags
 r=subprocess.run(cmd,cwd=cwd or out,env=env or {k:v for k,v in os.environ.items() if not k.startswith(("PYTHON","LEAN_"))},input=stdin,capture_output=True,text=True);commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n');assert r.returncode==0,r.stderr;return r.stdout
for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[])]:
 crate=name.replace('-','_');cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-L','dependency='+str(out),str(BASE/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
 for d in deps:cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
 run(cmd)
shutil.copytree(BASE/'vendor/cssparser/src',out/'src')
source=(ROOT/'source/third_party__rust__cssparser__src__tokenizer.rs').read_text()
parser=(ROOT/'source/third_party__rust__cssparser__src__parser.rs').read_text()
parser += "\n"+(BASE/'source/accepted-wrapper.rs').read_text()+"\n"+(ROOT/'native/wrapper.rs').read_text()
if a.mutation:
 mutation=next(m for m in json.loads((ROOT/'MUTATIONS.json').read_text()) if m['id']==a.mutation)
 target=parser if mutation['source']=='parser' else source
 assert target.count(mutation['old'])==1
 target=target.replace(mutation['old'],mutation['new'])
 if mutation['source']=='parser':parser=target
 else:source=target
 (out/'MUTATION.json').write_text(json.dumps(mutation,indent=2)+'\n')
(out/'src/parser.rs').write_text(parser)
(out/'src/tokenizer.rs').write_text(source)
fast_flags=[]
probe_flags=[]
cmd=[str(rustc),'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-L','dependency='+str(out),str(out/'src/lib.rs'),'-o',str(out/'libcssparser.rlib')]
for d in ['dtoa_short','itoa','smallvec']:cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
run(cmd+fast_flags)
run([str(rustc),'--edition','2024','-L','dependency='+str(out),'--extern','cssparser='+str(out/'libcssparser.rlib'),str(ROOT/'native/probe.rs'),'-o',str(out/'probe')]+probe_flags)
cases=json.loads((ROOT/'native/CASES.json').read_text());raw=run([str(out/'probe')],''.join(case['input'].encode().hex()+'|'+';'.join(case['ops'])+'\n'for case in cases));(out/'raw.txt').write_text(raw)
print(f'Executed {len(cases)} exact-source public history cases')
