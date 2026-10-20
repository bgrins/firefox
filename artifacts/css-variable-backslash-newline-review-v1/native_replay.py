import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("use python3 -I -S without optimization")
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
dep = Path('/Users/bgrins/code/firefox/artifacts/css-variable-origin-proof-v2')
if hashlib.sha256((dep/'MANIFEST.json').read_bytes()).hexdigest() != 'd4cf352f227c13e8deb57f32b3ba4222b629ad229a4e05cbf5a2b1840b98a246':
    raise RuntimeError('dependency manifest')
for name, digest in json.loads((dep/'MANIFEST.json').read_text()).items():
    if hashlib.sha256((dep/name).read_bytes()).hexdigest() != digest:
        raise RuntimeError('dependency input: '+name)
for name, digest in json.loads((Path(__file__).parent/'NATIVE-INPUTS.json').read_text()).items():
    if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
        raise RuntimeError('native source changed: '+name)
sys.path.insert(0, '/Users/bgrins/code/firefox/artifacts/css-variable-origin-proof-v2/native')
import rust_reader

ROOT = Path('/Users/bgrins/code/firefox/artifacts/css-variable-origin-proof-v2')
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

variants={'baseline': '/Users/bgrins/code/firefox/artifacts/css-variable-backslash-newline-root-v1/before.rs', 'tested': '/Users/bgrins/code/firefox/artifacts/css-variable-backslash-newline-root-v1/candidate.rs', 'head': '/Users/bgrins/code/firefox/artifacts/css-variable-backslash-newline-root-v1/package-head/candidate.rs', 'upstream': '/Users/bgrins/code/firefox/artifacts/css-variable-backslash-newline-root-v1/package-standalone/candidate.rs'}
for variant, source_path in variants.items():
    src=Path(source_path).read_text()
    records=[]
    def full(marker, after=0):
        i=src.index(marker,after)
        ts=rust_reader.tokens(src[i:])
        b=next(k for k,t in enumerate(ts) if t[0]=='{')
        end=rust_reader.pair(ts,b)
        s=src[i:i+ts[end][2]]
        records.append({'marker':marker,'start':i,'sha256':hashlib.sha256(s.encode()).hexdigest(),'complete':True})
        return s
    code=(ROOT/'native/facade.rs').read_text()
    code+='\n#[derive(Clone,Debug,PartialEq)]\n'+full('pub struct AttrTaintedRange {')+'\n'
    code+=full('impl AttrTaintedRange {')+'\n'
    tuple_decl='pub struct AttrTaint(SmallVec<[AttrTaintedRange; 1]>);'
    assert src.count(tuple_decl)==1
    code+='#[derive(Clone,Debug,Default)]\n'+tuple_decl+'\n'+full('impl AttrTaint {')+'\n'
    records.append({'marker':'AttrTaint tuple struct','sha256':hashlib.sha256(tuple_decl.encode()).hexdigest(),'complete':True})

    for marker,derive in [('pub struct VariableValue {','Debug'),('pub struct VariableFallback {','Debug'),('pub struct SubstitutionFunctionReference {','Debug'),('pub struct References {','Debug,Default'),('pub enum SubstitutionFunctionKind {','Copy,Clone,Debug,PartialEq,Eq'),("struct Substitution<'a> {",'Debug,Default')]:
        code+='\n#[derive('+derive+')]\n'+full(marker)+'\n'
    code+='\n#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]\npub struct ReferenceFlags(u8);\n'+full('bitflags! {')
    code+='\nimpl ReferenceFlags {\n'+full('    fn from_unit(value:')+'\n}\n'
    length=(ROOT/'source/length.rs').read_text()
    code+='\nstruct NoCalcLength;\nimpl NoCalcLength {\n'
    for name in ['EM','EX','CH','CAP','IC','LH','REM','REX','RCH','RCAP','RIC','RLH']:
        m=re.findall(r"    pub const "+name+r": &'static str = \"[^\"]+\";",length)
        assert len(m)==1
        code+=m[0]+'\n'
    code+='}\nimpl VariableValue {\n'
    for marker in ['    fn empty(url_data:', '    fn push(\n', '    pub fn parse(\n']:
        code+=full(marker)+'\n'
    code+='}\n'
    for marker in ['pub fn parse_name(', 'fn parse_declaration_value(', 'fn parse_declaration_value_block(', "fn do_substitute_chunk<'a>(", "fn substitute_internal<'a>("]:
        code+=full(marker)+'\n'
    start=src.index("impl<'a> Substitution<'a> {")
    code+="impl<'a> Substitution<'a> {\n"+full('    fn from_value(',start)+'\n'+full('    fn new(',start)+'\n}\n'
    one=full("fn substitute_one_reference<'a>(")
    records[-1]["complete"] = False
    records[-1]["source_body_hashed_complete"] = True
    records[-1]["compiled"] = "signature and fallback tail only; see provider record"
    head=one[:one.index('{')+1]
    tail=one[one.index('    let Some(ref fallback) = reference.fallback'):]
    code+=head+'''\n    if reference.name == "tainted" {
        return Ok(Substitution::new(Cow::Borrowed("é中𐐀"), TokenSerializationType::Ident, TokenSerializationType::Ident, true));
    }
    if substitution_functions.present && reference.name == "present" {
        return Ok(Substitution::new(Cow::Borrowed("known"), TokenSerializationType::Ident, TokenSerializationType::Ident, false));
    }
'''+tail+'\n'
    records.append({'marker':'substitute_one_reference','compiled':'signature and exact missing-provider fallback tail; provider facade deliberately bypasses var/env/attr lookup','full_sha256':hashlib.sha256(one.encode()).hexdigest()})
    code+=(ROOT/'native/driver.rs').read_text()
    path=out/(variant+'.rs');path.write_text(code)
    (out/(variant+'-bindings.json')).write_text(json.dumps(records,indent=2)+'\n')
    cmd=[str(rustc),'--edition','2024','--crate-name','witness','-C','opt-level=1','-L','dependency='+str(out)]
    for dep in ['cssparser','bitflags','smallvec']:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
    run(cmd+[str(path),'-o',str(out/variant)])
    cases=json.loads((Path(__file__).parent/'CASES.json').read_text())
    raw=run([str(out/variant)],''.join(c.get('mode','fresh')+'|'+str(c.get('start',0))+'|'+c['css'].encode().hex()+'\n' for c in cases))
    (out/(variant+'.jsonl')).write_text(raw)
print(json.dumps({'status':'EXECUTED','variants':4,'cases':len(cases)}))
