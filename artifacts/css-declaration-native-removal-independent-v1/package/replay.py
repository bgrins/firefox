import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
subprocess.run([sys.executable,'-I','-S',str(R/'check.py')],check=True,capture_output=True,text=True)
out=a.output.resolve();assert not out.exists() and not out.is_relative_to(R);out.mkdir(parents=True)
t=json.loads((R/'TOOLCHAIN.json').read_text());lean=Path(t['lean']);assert hashlib.sha256(lean.read_bytes()).hexdigest()==t['lean_sha256']
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};env['LEAN_PATH']=str(out)
modules=['AllOrder','PublicStorage','PublicRemoval','PublicAPI','NativeRemoval','NativeRemovalAPI','RemovalWitnesses']
commands=[]
def run(args,cwd):
    p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True)
    commands.append({'command':args,'cwd':str(cwd),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    return p
for name in modules:
    src=R/'lean'/(name+'.lean');text=src.read_text()
    assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b',text)
    shutil.copyfile(src,out/src.name)
    p=run([str(lean),'-o',name+'.olean',name+'.lean'],out)
    assert p.returncode==0,(name,p.stdout,p.stderr)
names=json.loads((R/'THEOREMS.json').read_text())
actual=[]
for name in modules[1:]:actual += [name+'.'+x for x in re.findall(r'^theorem ([A-Za-z0-9_]+)',(out/(name+'.lean')).read_text(),re.M)]
assert actual==names and len(names)==len(set(names))==65
(out/'Audit.lean').write_text('\n'.join('import '+n for n in modules)+'\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
p=run([str(lean),'Audit.lean'],out);assert p.returncode==0
(out/'AXIOMS.txt').write_text(p.stdout)
audits=re.findall(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",p.stdout)
assert [n for n,_ in audits]==names
for _,items in audits:assert {x.strip() for x in items.split(',') if x.strip()} <= {'propext','Quot.sound','Classical.choice'}
mut=out/'mutant';mut.mkdir()
text=(R/'lean/NativeRemoval.lean').read_text();old='loop selected (rawDelete raw old.1 index) index (len-1)';new='loop selected (rawDelete raw old.1 index) (index+1) (len-1)';assert text.count(old)==1
(mut/'NativeRemoval.lean').write_text(text.replace(old,new))
p=run([str(lean),'NativeRemoval.lean'],mut)
assert p.returncode!=0 and ('unsolved goals' in p.stdout or 'Type mismatch' in p.stdout or 'rewrite' in p.stdout)
assert not re.search(r'unknown (identifier|constant)|unexpected token|unknown module',p.stdout)
result={'modules':len(modules),'audited_theorems':len(names),'inherited_checkpoint_audits':44,'new_audits':21,'source_bodies':len(json.loads((R/'SOURCE-BINDINGS.json').read_text())),'advance_delete_mutated_module_rejected':True,'successful_kernel_witnesses':['adjacent_removal_control','advance_after_delete_counterexample','retained_length_counterexample','no_match_control','exhausted_index_control'],'native_compilation':'NOT_RUN','scope':'source-shaped Lean loop with manual source correspondence, explicit container/compiler/usize/caller admissions'}
g=run([sys.executable,'-I','-S',str(R/'guard.py'),'--output',str(out/'guards')],out);assert g.returncode==0
result['authentication_controls']=json.loads((out/'guards/RESULT.json').read_text())
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
if (R/'receipts/RESULT.json').exists():assert result==json.loads((R/'receipts/RESULT.json').read_text())
print(json.dumps(result))
