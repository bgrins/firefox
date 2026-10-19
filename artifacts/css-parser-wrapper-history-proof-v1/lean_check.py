from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
assert sys.flags.isolated and sys.flags.no_site
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
tool=json.loads((R/'TOOLCHAIN.json').read_text());lean=Path(tool['lean']);assert hashlib.sha256(lean.read_bytes()).hexdigest()==tool['lean_sha256']
inv=json.loads((R/'LEAN-INVENTORY.json').read_text());src=out/'lean';shutil.copytree(R/'lean',src);env={**{k:v for k,v in os.environ.items()if not k.startswith(("PYTHON","LEAN_"))},'LEAN_PATH':str(src)};commands=[]
def run(path,log,expect=0):
 cmd=[str(lean),'-o',str(path.with_suffix('.olean')),str(path)]
 r=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True);text=r.stdout+r.stderr;(out/log).write_text(text);commands.append({'command':cmd,'exit':r.returncode,'log':log});assert (r.returncode==0) if expect==0 else (r.returncode!=0),(log,text[-3000:]);return text
for name in inv['modules']+['Audit']:
 s=(src/(name+'.lean')).read_text();assert not re.search(r'\b(sorry|admit|axiom|native_decide|implemented_by|bv_decide)\b',s),name
 run(src/(name+'.lean'),name+'.log')
text=(out/'Audit.log').read_text();observed=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$",text,re.M);names=json.loads((R/'AUDIT-NAMES.json').read_text());assert [n for n,_ in observed]==names
allowed={'propext','Classical.choice','Quot.sound'};assert all(set(filter(None,(s.strip()for s in ax.split(','))))<=allowed for _,ax in observed)
mutations=[]
for m in json.loads((R/'LEAN-MUTATIONS.json').read_text()):
 original=(src/(m['module']+'.lean')).read_text();assert original.count(m['old'])==1;changed=original.replace(m['old'],m['new']);q=out/('mutation-'+m['id']);q.mkdir()
 prefix=re.sub(r'(?ms)^theorem .*?(?=^(?:theorem |def |structure |end |namespace |#)|\Z)', '', changed)
 namespace=re.search(r'^namespace (\w+)',prefix,re.M).group(1)
 prefix=prefix.replace('namespace '+namespace,'namespace Mutation').replace('end '+namespace,'end Mutation')
 assert prefix.rstrip().endswith('end Mutation')
 prefix=prefix.rstrip()[:-len('end Mutation')]
 witness=q/'Witness.lean';witness.write_text(prefix+'\n'+m['witness']+'\nend Mutation\n');run(witness,'mutation-'+m['id']+'-witness.log')
 f=q/(m['module']+'.lean');f.write_text(changed);text=run(f,'mutation-'+m['id']+'-rejected.log',1)
 assert 'error:'in text and any(t in text for t in ['unsolved goals','decide','failed','Type mismatch','could not prove']),text
 assert not any(t in text for t in ['unexpected token','unknown identifier','unknown constant','unknown namespace']),text
 mutations.append({'id':m['id'],'definition_and_counterexample':'PASS','unchanged_theorems':'REJECTED'})
receipt={'status':'PASS','modules':len(inv['modules']),'new_modules':len(inv['new_modules']),'audits':len(names),'new_audits':inv['new_theorems'],'mutations':mutations,'commands':commands};(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='commands'}))
