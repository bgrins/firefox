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
scanner = ROOT / 'inputs/scanner/scanner'
config = json.loads((scanner / 'TOOLCHAIN.json').read_text())
rustc = Path(config['rustc'])
assert hashlib.sha256(rustc.read_bytes()).hexdigest() == config['rustc_sha256']
shutil.copytree(scanner / 'vendor', out / 'vendor')
shutil.copyfile(ROOT / 'inputs/static/source/third_party/rust/cssparser/src/tokenizer.rs', out / 'vendor/cssparser/src/tokenizer.rs')
commands = []
def run(command, stdin=None):
    r = subprocess.run(command, cwd=out, input=stdin, capture_output=True, text=True)
    commands.append({'command': command, 'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands, indent=2)+'\n')
    assert r.returncode == 0, r.stderr
    return r.stdout
for name, edition, deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[]),('bitflags','2021',[]),('cssparser','2024',['dtoa-short','itoa','smallvec'])]:
    crate=name.replace('-','_')
    cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-C','opt-level=1','-L','dependency='+str(out),str(out/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
    for d in deps:
        d=d.replace('-','_');cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
    run(cmd)
source=(ROOT/'inputs/static/source/servo/components/style/custom_properties.rs').read_text()
records=[]
def extract(start,end):
    i=source.index(start);j=source.index(end,i)+len(end);s=source[i:j]
    records.append({'start':start,'sha256':hashlib.sha256(s.encode()).hexdigest()})
    return s
flags=extract('bitflags! {\n    impl ReferenceFlags','\n}')
units=extract('    fn from_unit(value:','\n    }')
helper=extract('fn resolved_token_dependencies(','\n}')
enum=extract('pub enum SubstitutionFunctionKind {','\n}')
length=(scanner/'source/servo/components/style/values/specified/length.rs').read_text()
constants=[]
for name in ['EM','EX','CH','CAP','IC','LH','REM','REX','RCH','RCAP','RIC','RLH']:
    matches=re.findall(r"    pub const "+name+r": &'static str = \"[^\"]+\";",length)
    assert len(matches)==1;constants+=matches
code='use cssparser::{CowRcStr,Parser,Token};\nuse bitflags::bitflags;\nuse std::io::{self,BufRead};\n'
code+='#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]\npub struct ReferenceFlags(u8);\n'+flags
code+='\nstruct NoCalcLength;\nimpl NoCalcLength {\n'+'\n'.join(constants)+'\n}\nimpl ReferenceFlags {\n'+units+'\n}\n'+enum
code+='''
impl SubstitutionFunctionKind {
 fn from_ident(s:&str)->Result<Self,()> { cssparser::match_ignore_ascii_case! {s,"var"=>Ok(Self::Var),"env"=>Ok(Self::Env),"attr"=>Ok(Self::Attr),_=>Err(())} }
}
'''+helper+'\n'+(ROOT/'native/driver.rs').read_text()
(out/'harness.rs').write_text(code)
(out/'SOURCE-BINDINGS.json').write_text(json.dumps(records,indent=2)+'\n')
run([str(rustc),'--edition','2024','-C','opt-level=1','-L','dependency='+str(out),'--extern','cssparser='+str(out/'libcssparser.rlib'),'--extern','bitflags='+str(out/'libbitflags.rlib'),str(out/'harness.rs'),'-o',str(out/'numeric')])
cases=json.loads((ROOT/'native/CASES.json').read_text())
raw=run([str(out/'numeric')],''.join(c['css'].encode().hex()+'\n' for c in cases))
(out/'OBSERVATIONS.tsv').write_text(raw)
rows=raw.splitlines();assert len(rows)==len(cases)
for c,row in zip(cases,rows):
    fields=row.split('\t')
    if 'payload_bits' in c: assert fields[6]==c['payload_bits'],(c,row)
    if 'scanner_flags' in c: assert fields[7]==str(c['scanner_flags']),(c,row)
print(json.dumps({'status':'PASS','cases':len(cases),'source':'original numeric / corrected identifier guard','payload':'selected controls only; intermediate-loss witnesses retained'}))
