#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def auth():
 f=json.loads((R/'FREEZE.json').read_text())
 assert digest(R/'MANIFEST.json')==f['manifest_sha256'],'manifest authentication'
 m=json.loads((R/'MANIFEST.json').read_text())
 for name,pin in m.items():
  q=R/name
  assert q.is_file() and digest(q)==pin,'authentication: '+name
 return m

def main():
 a=argparse.ArgumentParser();a.add_argument('--run',action='store_true');a.add_argument('--output',type=Path);args=a.parse_args()
 m=auth();print('AUTHENTICATED',len(m),'entries')
 if not args.run:return
 assert args.output is not None and not args.output.exists(),'new output directory required'
 out=args.output.resolve();out.mkdir(parents=True)
 tool=json.loads((R/'TOOLCHAIN.json').read_text());lean=Path(os.environ.get('LEAN',tool['lean']));rust=Path(os.environ.get('RUSTC',tool['rustc']))
 assert digest(lean)==tool['lean_sha256'],'Lean executable'
 assert subprocess.check_output([str(rust),'--version','--verbose'],text=True)==tool['rustc_version'],'Rust toolchain'
 results=[]
 def run(cmd,log,env=None,expected=0,cwd=out):
  p=subprocess.run(list(map(str,cmd)),cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (out/log).write_text(p.stdout);results.append(dict(command=list(map(str,cmd)),log=log,exit=p.returncode))
  assert (p.returncode==0) if expected==0 else (p.returncode!=0),(log,p.stdout[-2000:])
  return p.stdout
 src=out/'lean';src.mkdir()
 modules=tool['modules']+['Audit']
 for name in modules:
  data=(R/'lean'/f'{name}.lean').read_text()
  assert not re.search(r'\b(sorry|admit|axiom|native_decide|implemented_by)\b',data),name
  (src/f'{name}.lean').write_text(data)
 env=dict(os.environ,LEAN_PATH=str(src))
 for name in modules:run([lean,'-o',src/f'{name}.olean',src/f'{name}.lean'],name+'.log',env)
 audit=(out/'Audit.log').read_text();names=json.loads((R/'AUDIT-NAMES.json').read_text())
 observed=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$",audit,re.M)
 assert [n for n,_ in observed]==names,'audit completeness'
 allowed={'propext','Classical.choice','Quot.sound'}
 assert all(set(filter(None,(s.strip() for s in ax.split(','))))<=allowed for _,ax in observed),'axiom whitelist'
 generated=out/'generated';generated.mkdir();shutil.copy2(R/'generate.py',generated/'generate.py');shutil.copytree(R/'source',generated/'source')
 run([sys.executable,generated/'generate.py'],'generate.log')
 for name in ['observer-witness.rs','CASES.json','EXTRACTIONS.json']:assert digest(generated/name)==digest(R/name),'regeneration '+name
 for mode,flags in [('debug',[]),('release',['-O'])]:
  binary=out/('observer-'+mode)
  run([rust,'--edition=2021',*flags,generated/'observer-witness.rs','-o',binary],'compile-'+mode+'.log')
  text=run([binary],'run-'+mode+'.log');assert text.strip()=='PASS histories=395 comment_calls=405 raw_slices_positions_locations_and_both_URLs'
 mutants=json.loads((R/'MUTATIONS.json').read_text());mutation_results=[]
 for mutant in mutants:
  name=mutant['name'];module=mutant['module'];original=(R/'lean'/f'{module}.lean').read_text();before=mutant['before'];after=mutant['after']
  assert original.count(before)==1
  mutated=original.replace(before,after)
  definition=re.search(r'^def '+mutant['definition']+r'\b[\s\S]*?(?=\n\n|\Z)',mutated,re.M).group()
  defs='import '+module+'\nnamespace Mutation\nopen '+module+' CommentScan\n'+definition+'\n'+mutant['witness']+'\nend Mutation\n'
  q=out/('mutation-'+name);q.mkdir();(q/'Definitions.lean').write_text(defs);(q/(module+'.lean')).write_text(mutated)
  run([lean,q/'Definitions.lean'],'mutation-'+name+'-definitions.log',env)
  text=run([lean,q/(module+'.lean')],'mutation-'+name+'-rejection.log',env,expected=1)
  assert 'error:' in text and any(x in text for x in ['unsolved goals','decide','failed']),'not semantic rejection'
  assert not any(x in text for x in ['unexpected token','unknown identifier','unknown constant','unknown namespace']),'syntax/name failure'
  mutation_results.append(dict(name=name,definition_and_counterexample_compiled=True,unchanged_theorems_rejected=True))
 (out/'REPLAY.json').write_text(json.dumps(dict(status='PASS',authenticated_entries=len(m),modules=len(modules)-1,new_modules=7,axiom_audits=len(names),new_axiom_audits=62,native_histories=395,native_calls=405,mutants=mutation_results,commands=results),indent=2)+'\n')
 print('PASS 11 modules, 100 audits (62 new), 405 native calls/debug+release, 4 compiled semantic mutants')
if __name__=='__main__':main()
