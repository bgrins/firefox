import argparse
import hashlib
import json
from pathlib import Path
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
def run(cmd, expect=0):
    r = subprocess.run(cmd, cwd=out, capture_output=True, text=True)
    commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert (r.returncode == 0) == (expect == 0), r.stderr
    return r.stdout
for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[])]:
    crate=name.replace('-','_')
    cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-C','opt-level=1','-L','dependency='+str(out),str(ROOT/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
    for d in deps:
        d=d.replace('-','_');cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
    run(cmd)
original=(ROOT/'original/third_party/rust/cssparser/src/parser.rs').read_text()
candidate=(ROOT/'candidate/third_party/rust/cssparser/src/parser.rs').read_text()
call='        parser.consume_until_end_of_block(block_type);\n'
assert candidate.count(call)==1 and candidate.replace(call,'')==original
variants={'original':original,'candidate':candidate,'mutant-omit':candidate.replace(call,''),'mutant-kind':candidate.replace(call,'        parser.consume_until_end_of_block(BlockType::Parenthesis);\n')}
for variant,parser in variants.items():
    dest=out/variant;dest.mkdir()
    shutil.copytree(ROOT/'vendor/cssparser/src',dest/'src')
    (dest/'src/parser.rs').write_text(parser)
    cmd=[str(rustc),'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-C','opt-level=1','-L','dependency='+str(out),str(dest/'src/lib.rs'),'-o',str(dest/'libcssparser.rlib')]
    for d in ['dtoa_short','itoa','smallvec']:
        cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
    run(cmd)
    run([str(rustc),'--edition','2024','-C','opt-level=1','-L','dependency='+str(out),'--extern','cssparser='+str(dest/'libcssparser.rlib'),str(ROOT/'native/witness.rs'),'-o',str(dest/'witness')])
    raw=run([str(dest/'witness'),'original' if variant=='original' else 'repaired'],expect=1 if variant.startswith('mutant-') else 0)
    (dest/'OBSERVATIONS.jsonl').write_text(raw)
print('PASS: original and candidate observations; both compiled semantic mutants rejected')
