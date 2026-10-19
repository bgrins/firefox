from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--release',action='store_true');p.add_argument('--mutation');p.add_argument('--fast',action='store_true');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
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
shutil.copytree(ROOT/'vendor/cssparser/src',out/'src');p=out/'src/tokenizer.rs';source=p.read_text()
if a.mutation:
 mutations=json.loads((ROOT/'MUTATIONS.json').read_text());mutation=next(m for m in mutations if m['id']==a.mutation)
 start=source.index('fn consume_unquoted_url');end=source.index('\n// (value, number of digits',start)
 if mutation['scope']=='bad-url':start=source.index('    fn consume_bad_url',start)
 part=source[start:end];assert part.count(mutation['old'])==1
 source=source[:start]+part.replace(mutation['old'],mutation['new'])+source[end:]
 (out/'MUTATION.json').write_text(json.dumps(mutation,indent=2)+'\n')
p.write_text(source+'\n'+(ROOT/'native/wrapper.rs').read_text())
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
