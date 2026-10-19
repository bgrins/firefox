from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,os,sys
assert sys.flags.isolated and sys.flags.no_site
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--release',action='store_true');p.add_argument('--mutation');p.add_argument('--fast',action='store_true');p.add_argument('--plain',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
config=json.loads((ROOT/'TOOLCHAIN.json').read_text());rustc=Path(config['rustc']);assert hashlib.sha256(rustc.read_bytes()).hexdigest()==config['rustc_sha256']
commands=[]
mode_flags=['-C','opt-level=2','-C','debug-assertions=off'] if a.release else []
def run(cmd,stdin=None,cwd=None,env=None):
 if cmd[0]==str(rustc):cmd=cmd+mode_flags
 r=subprocess.run(cmd,cwd=cwd or out,env=env,input=stdin,capture_output=True,text=True);commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n');assert r.returncode==0,r.stderr;return r.stdout
for name,edition,deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[])]:
 crate=name.replace('-','_');cmd=[str(rustc),'--crate-name',crate,'--crate-type','rlib','--edition',edition,'-L','dependency='+str(out),str(ROOT/'vendor'/name/'src/lib.rs'),'-o',str(out/('lib'+crate+'.rlib'))]
 for d in deps:cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
 run(cmd)
shutil.copytree(ROOT/'vendor/cssparser/src',out/'src')
source=(ROOT/'source/tokenizer.rs').read_text()
parser=(ROOT/'source/parser.rs').read_text()
parser += "\nimpl ParserState { pub(crate) fn codex_packed(&self) -> u32 { self.line_number_and_block_type } }\n"
(out/'src/parser.rs').write_text(parser)
assert source.count('if let Ok(url) = consume_unquoted_url(parser) {')==1
source=source.replace('if let Ok(url) = consume_unquoted_url(parser) {','if let Ok(url) = codex_url_call(parser) {')
start=source.index("fn consume_unquoted_url<'a>")
part=source[start:]
replacements={}
for name in ['advance','consume_known_byte','consume_4byte_intro','consume_continuation_byte','consume_newline','consume_char','slice_from']:
 old='parser.'+name+'(';new='parser.codex_'+name+'('
 replacements[old]=part.count(old);assert replacements[old]>0
 part=part.replace(old,new)
old='    if newlines > 0 {\n        parser.state.advance_line_number(newlines);'
new='    parser.codex_bulk(start_position, newlines, last_newline);\n'+old
assert part.count(old)==1
part=part.replace(old,new)
source=source[:start]+part
restored=source.replace('if let Ok(url) = codex_url_call(parser) {','if let Ok(url) = consume_unquoted_url(parser) {')
for old in replacements:
 restored=restored.replace(old.replace('parser.','parser.codex_'),old)
restored=restored.replace('    parser.codex_bulk(start_position, newlines, last_newline);\n','')
assert restored==(ROOT/'source/tokenizer.rs').read_text(),'instrumentation inverse must recover every original byte'
(out/'INSTRUMENTATION.json').write_text(json.dumps({'applied':not a.plain,'inverse_recovers_complete_source':True,'method_call_replacements':replacements,'caller_seam':1,'bulk_before_assignment':1,'parser_field_reader':1},indent=2)+'\n')
if a.plain:
 assert not a.mutation
 source=(ROOT/'source/tokenizer.rs').read_text()
if a.mutation:
 mutations=json.loads((ROOT/'MUTATIONS.json').read_text());mutation=next(m for m in mutations if m['id']==a.mutation)
 old,new=mutation['old'],mutation['new'];assert source.count(old)==mutation.get('count',1)
 source=source.replace(old,new)
 (out/'MUTATION.json').write_text(json.dumps(mutation,indent=2)+'\n')
(out/'src/tokenizer.rs').write_text(source+'\n'+(ROOT/'native/wrapper.rs').read_text())
fast_flags=[]
probe_flags=[]
if a.fast:
 cargo=Path(config['cargo']);assert hashlib.sha256(cargo.read_bytes()).hexdigest()==config['cargo_sha256']
 project=out/'macro-build';(project/'.cargo').mkdir(parents=True);(project/'src').mkdir()
 (project/'Cargo.toml').write_text('[package]\nname="bad-url-macro-build"\nversion="0.1.0"\nedition="2024"\n[workspace]\n[dependencies]\ncssparser-macros={path='+json.dumps(str(ROOT/'macro-vendor/cssparser-macros'))+'}\n')
 (project/'.cargo/config.toml').write_text('[source.crates-io]\nreplace-with="vendored-sources"\n[source.vendored-sources]\ndirectory='+json.dumps(str(ROOT/'macro-vendor'))+'\n')
 (project/'src/main.rs').write_text('fn main() {}\n');shutil.copyfile(ROOT/'inherited/bad-url/macro-Cargo.lock',project/'Cargo.lock')
 env={**{k:v for k,v in os.environ.items()if not k.startswith(("PYTHON","LEAN_"))},'RUSTC':str(rustc),'CARGO_HOME':str(out/'cargo-home'),'RUSTFLAGS':'-D warnings'}
 run([str(cargo),'build','--offline','--locked','--target-dir',str(project/'target')],cwd=project,env=env)
 deps=project/'target/debug/deps';macros=list(deps.glob('libcssparser_macros-*.dylib'));assert len(macros)==1
 probe_flags=['-L','dependency='+str(deps)]
 fast_flags=['--cfg','feature="fast_match_byte"','--extern','cssparser_macros='+str(macros[0]),'-L','dependency='+str(deps)]
cmd=[str(rustc),'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-L','dependency='+str(out),str(out/'src/lib.rs'),'-o',str(out/'libcssparser.rlib')]
for d in ['dtoa_short','itoa','smallvec']:cmd+=['--extern',d+'='+str(out/('lib'+d+'.rlib'))]
run(cmd+fast_flags)
run([str(rustc),'--edition','2024','-L','dependency='+str(out),'--extern','cssparser='+str(out/'libcssparser.rlib'),str(ROOT/'native/probe.rs'),'-o',str(out/'probe')]+probe_flags)
cases=json.loads((ROOT/'CASES.json').read_text());raw=run([str(out/'probe')],''.join(case['input'].encode().hex()+'\n'for case in cases));(out/'raw.txt').write_text(raw)
print(f'Executed {len(cases)} exact-source lexical provider cases')
