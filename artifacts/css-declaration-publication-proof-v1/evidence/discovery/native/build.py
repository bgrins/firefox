import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import types
rust_reader = types.ModuleType('rust_reader')
rust_reader.__file__ = str(Path(__file__).resolve().parent/'rust_reader.py')
exec(compile((Path(__file__).resolve().parent/'rust_reader.py').read_text(), 'authenticated-rust-reader', 'exec'), rust_reader.__dict__)

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

for variant in ['original','clear-candidate']:
    src=(ROOT/'evidence/source/servo/components/style/custom_properties.rs').read_text()
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
    for marker,derive in [('pub struct VariableValue {','Debug'),('pub struct VariableFallback {','Debug'),('pub struct SubstitutionFunctionReference {','Debug'),('pub struct References {','Debug,Default'),('pub enum SubstitutionFunctionKind {','Copy,Clone,Debug,PartialEq,Eq')]:
        code+='\n#[derive('+derive+')]\n'+full(marker)+'\n'
    code+='\n#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]\npub struct ReferenceFlags(u8);\n'+full('bitflags! {')
    code+='\nimpl ReferenceFlags {\n'+full('    fn from_unit(value:')+'\n}\n'
    length=(ROOT/'evidence/length.rs').read_text()
    code+='\nstruct NoCalcLength;\nimpl NoCalcLength {\n'
    for name in ['EM','EX','CH','CAP','IC','LH','REM','REX','RCH','RCAP','RIC','RLH']:
        m=re.findall(r"    pub const "+name+r": &'static str = \"[^\"]+\";",length)
        assert len(m)==1
        code+=m[0]+'\n'
    code+='}\nimpl VariableValue {\n'
    for marker in ['    fn empty(url_data:', '    pub fn parse(\n']:
        code+=full(marker)+'\n'
    code+='}\n'
    for marker in ['pub fn parse_name(', 'fn parse_declaration_value(', 'fn parse_declaration_value_block(']:
        code+=full(marker)+'\n'
    src=(ROOT/'evidence/source/servo/components/style/values/specified/mod.rs').read_text()
    code+='\n#[derive(Debug)]\n'+full('pub enum ParsedNamespace {')+'\n'
    for marker in ['impl ParsedNamespace {','impl Default for ParsedNamespace {','pub fn parse_namespace(']:
        code+=full(marker)+'\n'
    src=(ROOT/'evidence/source/servo/components/style/values/specified/param.rs').read_text()
    code+='\n'+full('impl Parse for LinkParameters {')+'\n'
    src=(ROOT/'evidence/source/servo/components/style/properties/mod.rs').read_text()
    helper=full('fn parse_non_custom_property_declaration_value_into(')
    if variant=='clear-candidate':
        needle='            ParseError::custom(style_traits::StyleParseErrorKind::UnspecifiedError)'
        assert helper.count(needle)==1
        helper=helper.replace(needle,'            declarations.clear();\n'+needle)
    code+='\n'+helper+'\n'
    code+=(ROOT/'native/driver.rs').read_text()
    path=out/(variant+'.rs');path.write_text(code)
    (out/(variant+'-bindings.json')).write_text(json.dumps(records,indent=2)+'\n')
    cmd=[str(rustc),'--edition','2024','--crate-name','witness','-C','opt-level=1','-L','dependency='+str(out)]
    for dep in ['cssparser','bitflags','smallvec']:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
    run(cmd+[str(path),'-o',str(out/variant)])
    raw=run([str(out/variant)])
    (out/(variant+'.jsonl')).write_text(raw)
original=[json.loads(x) for x in (out/'original.jsonl').read_text().splitlines()]
candidate=[json.loads(x) for x in (out/'clear-candidate.jsonl').read_text().splitlines()]
assert len(original)==len(candidate)==13
for i,(old,new) in enumerate(zip(original,candidate)):
    ordinary=i in {0,1,2,3,4,12}
    seen=i not in {3,4,8,10}
    accepted=i not in {5,6,7,8}
    assert old['ordinary_ok']==new['ordinary_ok']==ordinary
    assert old['seen']==new['seen']==seen
    assert old['helper_ok']==new['helper_ok']==accepted
    expected=[] if not accepted else ['wide'] if i==10 else ['ordinary'] if i in {3,4} else ['with-variables']
    assert new['scratch']==expected
    assert old['scratch']==(['ordinary']+expected if ordinary and seen else expected)
print(json.dumps({'status':'PASS','variants':2,'rows_per_variant':13,'duplicate_scratch_before':4,'duplicate_scratch_after':0,'unchanged_controls':9}))
