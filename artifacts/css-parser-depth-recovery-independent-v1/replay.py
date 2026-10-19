import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,json,hashlib,subprocess,shutil
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
S=R/'evidence/scout';cfg=json.loads((S/'TOOLCHAIN.json').read_text());rustc=Path(cfg['rustc']);assert hashlib.sha256(rustc.read_bytes()).hexdigest()==cfg['rustc_sha256']
commands=[]
def run(cmd):
 p=subprocess.run(cmd,cwd=out,text=True,capture_output=True);commands.append({'command':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n');assert p.returncode==0,p.stderr;return p.stdout
for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[])]:
 crate=name.replace('-','_');cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-C','opt-level=1','-L','dependency='+str(out),str(S/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
 for dep in deps:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
 run(cmd)
old=(S/'vendor/cssparser/src/parser.rs').read_text();needle='    if parser.current_block_depth >= parser.nested_block_limit && parser.nested_block_limit != 0 {\n';assert old.count(needle)==1
candidate=old.replace(needle,needle+'        parser.consume_until_end_of_block(block_type);\n');assert candidate==(R/'evidence/candidate-parser.rs').read_text()
results={}
for mode in ['original','candidate']:
 src=out/mode;shutil.copytree(S/'vendor/cssparser',src);(src/'src/parser.rs').write_text(old if mode=='original' else candidate)
 lib=src/'libcssparser.rlib';cmd=[str(rustc),'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-C','opt-level=1','-L','dependency='+str(out),str(src/'src/lib.rs'),'-o',str(lib)]
 for dep in ['dtoa_short','itoa','smallvec']:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
 run(cmd);exe=src/'witness';run([str(rustc),'--edition','2024','-L','dependency='+str(out),'--extern','cssparser='+str(lib),str(R/'witness.rs'),'-o',str(exe)])
 raw=run([str(exe),mode]);(out/(mode+'.jsonl')).write_text(raw);results[mode]=len(raw.splitlines())
(out/'RESULT.json').write_text(json.dumps(results,indent=2)+'\n');print(results)
