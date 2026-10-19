import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,hashlib,json,os,re,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--record',action='store_true');a=p.parse_args()
subprocess.run([sys.executable,'-I','-S',str(R/'check.py')],check=True,capture_output=True,text=True)
out=a.output.resolve();assert not out.is_relative_to(R) and not out.exists();out.mkdir(parents=True)
cfg=json.loads((R/'TOOLCHAIN.json').read_text());assert hashlib.sha256(Path(cfg['lean']).read_bytes()).hexdigest()==cfg['lean_sha256']
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};env['LEAN_PATH']=str(out)
commands=[]
def run(cmd):
 start=time.monotonic();r=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True)
 commands.append({'command':cmd,'exit':r.returncode,'seconds':time.monotonic()-start,'stdout':r.stdout,'stderr':r.stderr})
 (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert r.returncode==0,commands[-1];return r
modules=['AllOrder','PublicStorage','ParseWinners','ParseFlags','WinnerWitnesses'];names=[];counts={}
for module in modules:
 source=(R/'lean'/f'{module}.lean').read_text();assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b',source)
 roster=[module+'.'+n for n in re.findall(r'^theorem\s+(\w+)',source,re.M)];names+=roster;counts[module]=len(roster)
 (out/f'{module}.lean').write_text(source)
 run([cfg['lean'],'-o',str(out/f'{module}.olean'),str(out/f'{module}.lean')])
assert names==json.loads((R/'THEOREMS.json').read_text())
(out/'Audit.lean').write_text(''.join('import '+m+'\n' for m in modules)+''.join('#print axioms '+n+'\n' for n in names))
ax=run([cfg['lean'],str(out/'Audit.lean')]).stdout
rows=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$",ax,re.M)
assert [n for n,_ in rows]==names
for _,group in rows:assert set(re.findall(r'[A-Za-z_][\w.]*',group))<={'propext','Quot.sound','Classical.choice'}
(out/'AXIOMS.txt').write_text(ax)
result={'theorem_counts':counts,'total_theorems':len(names),'new_universal_theorems':counts['ParseWinners']+counts['ParseFlags'],'new_concrete_kernel_examples':counts['WinnerWitnesses'],'native_executions':0,'source_only':True,'arbitrary_payloads':True,'duplicate_incoming_ids':True,'independent_whole_history_winner_reference':True}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
if not a.record:
 assert result==json.loads((R/'receipts/RESULT.json').read_text())
 assert ax==(R/'receipts/AXIOMS.txt').read_text()
 run([sys.executable,'-I','-S',str(R/'guard_capsule.py'),'--output',str(out/'capsule-guards')])
 assert (out/'capsule-guards/RESULT.json').read_bytes()==(R/'receipts/CAPSULE-GUARDS.json').read_bytes()
print(json.dumps(result))
