import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument('--output', required=True, type=Path); a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
config = json.loads((ROOT/'TOOLCHAIN.json').read_text()); rustc = Path(config['rustc'])
assert hashlib.sha256(rustc.read_bytes()).hexdigest() == config['rustc_sha256']
env = {k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_','RUSTFLAGS'))}
records = []
def run(cmd, allowed=(0,)):
 r = subprocess.run(cmd, cwd=out, env=env, capture_output=True, text=True)
 records.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 (out/'COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n')
 assert r.returncode in allowed, r.stderr
 return r
for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[])]:
 crate=name.replace('-','_');cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-L','dependency='+str(out),str(ROOT/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
 for dep in deps:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
 run(cmd)
shutil.copytree(ROOT/'vendor/cssparser/src',out/'src')
raw='''
/// Expose raw tokenizer classes for the boundary reference.
pub fn codex_flat_classes(css: &str) -> Vec<crate::TokenSerializationType> {
    let mut p = Parser::new(css);
    let mut result = Vec::new();
    while p.next_byte().is_some() {
        let token = p.next_unchecked();
        p.state.take_at_start_of();
        if !matches!(token, Token::Comment(_)) {
            result.push(token.serialization_type());
        }
    }
    result
}
'''
with (out/'src/parser.rs').open('a') as f:f.write(raw)
with (out/'src/lib.rs').open('a') as f:f.write('\npub use crate::parser::codex_flat_classes;\n')
cmd=[str(rustc),'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-L','dependency='+str(out),str(out/'src/lib.rs'),'-o',str(out/'libcssparser.rlib')]
for dep in ['dtoa_short','itoa','smallvec']:cmd+=['--extern',dep+'='+str(out/('lib'+dep+'.rlib'))]
run(cmd)
source=(ROOT/'source/value.candidate.rs').read_text()
start=source.index('        let mut input = CSSParser::new(&css);');end=source.index('        drop(input);',start)+len('        drop(input);')
loop=source[start:end];assert loop+'\n'==(ROOT/'native/loop.rs').read_text()
variants={'candidate':loop,'opener-last':loop.replace('=> TokenSerializationType::Other,','=> token.serialization_type(),'),'skip-whitespace':loop.replace('input.next_including_whitespace()','input.next()'),'include-comments':loop.replace('input.next_including_whitespace()','input.next_including_whitespace_and_comments()'),'first-as-last':loop.replace('            last = match token {','            if last == TokenSerializationType::Nothing { last = match token {').replace('            };','            }; }')}
assert len(set(variants.values()))==len(variants)
cases=json.loads((ROOT/'native/CASES.json').read_text())
fixture=',\n'.join('('+json.dumps(c['css'])+','+json.dumps(c['first'])+','+json.dumps(c['last'])+')' for c in cases)
for name,body in variants.items():
 code='use cssparser::{Parser as CSSParser, Token, TokenSerializationType};\nfn scan(css:&str)->(TokenSerializationType,TokenSerializationType) {\n'+body+'\n(first,last)\n}\n'
 code+='fn main(){ let cases = ['+fixture+']; for (i,(css,first,last)) in cases.iter().enumerate(){\n'
 code+='let raw=cssparser::codex_flat_classes(css); let flat=(raw.first().copied().unwrap_or_default(),raw.last().copied().unwrap_or_default()); let actual=scan(css); println!("{}|{:?}|{:?}|{:?}|{:?}",i,actual.0,actual.1,flat.0,flat.1); assert_eq!((format!("{:?}",flat.0),format!("{:?}",flat.1)),(first.to_string(),last.to_string()),"independent fixture"); assert_eq!(actual,flat,"boundary mismatch"); }}'
 path=out/(name+'.rs');path.write_text(code)
 run([str(rustc),'--edition','2024','-L','dependency='+str(out),'--extern','cssparser='+str(out/'libcssparser.rlib'),str(path),'-o',str(out/name)])
 r=run([str(out/name)],(0,) if name=='candidate' else (101,))
 if name!='candidate':assert 'boundary mismatch' in r.stderr
(out/'RESULT.json').write_text(json.dumps({'status':'PASS','cases':len(cases),'compiled_mutants':list(variants)[1:],'reference':'raw full tokenizer traversal, comments omitted; hand-written expected first/last classes','features':'ordinary byte dispatch only'},indent=2)+'\n')
print('PASS: 24 exact-loop/raw-tokenizer fixtures and four compiled semantic mutants')
