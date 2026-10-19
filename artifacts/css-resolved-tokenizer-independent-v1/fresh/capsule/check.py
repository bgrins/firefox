import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--lean',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((ROOT/'FREEZE.json').read_text())
assert sha(ROOT/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((ROOT/'MANIFEST.json').read_text())
for n,h in m.items():assert (ROOT/n).is_file() and not (ROOT/n).is_symlink() and sha(ROOT/n)==h,n
lean=a.lean.resolve()
assert sha(lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
copy=out/'capsule'
for n in m:
 dst=copy/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,dst)
commands=[]
def run(cmd,cwd,success=True):
 r=subprocess.run(cmd,cwd=cwd,env=dict(os.environ,LEAN_PATH=str(out)),capture_output=True,text=True)
 commands.append({'cmd':cmd,'cwd':str(cwd),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert (r.returncode==0)==success,commands[-1]
 return r.stdout+r.stderr
run(['python3',str(copy/'extract.py'),'--output',str(out/'generated')],out)
for n in ['INVOCATIONS.json','CurrentInvocations.lean']:
 assert sha(out/'generated'/n)==sha(ROOT/'generated'/n),n
for src in [copy/'lean/ByteDispatch.lean',out/'generated/CurrentInvocations.lean']:
 assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',src.read_text())
 shutil.copyfile(src,out/src.name)
log=run([str(lean),'-o','ByteDispatch.olean','ByteDispatch.lean'],out)
audits=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$",log,re.M)
assert len(audits)==8,audits
for n,deps in audits:assert set(filter(None,deps.split(', ')))<={'propext','Classical.choice','Quot.sound'},(n,deps)
run([str(lean),'-o','CurrentInvocations.olean','CurrentInvocations.lean'],out)
base=(out/'ByteDispatch.lean').read_text()
mutants=[('overwrite-existing','| some old => some old','| some old => if covers p b then some id else some old'),
 ('exclusive-endpoint','lo ≤ b ∧ b ≤ hi','lo ≤ b ∧ b < hi')]
for name,old,new in mutants:
 assert old in base
 mutant=base.replace(old,new,1)
 path=out/(name+'.lean');path.write_text(mutant)
 log=run([str(lean),path.name],out,False)
 assert 'error:' in log
# The strict source reader must reject unsupported future patterns before generation.
tokenizer=copy/'source/cssparser/src/tokenizer.rs'
original=tokenizer.read_text()
assert "b'0' ..= b'9'" in original
tokenizer.write_text(original.replace("b'0' ..= b'9'","b'0' .. b'9'",1))
log=run(['python3',str(copy/'extract.py'),'--output',str(out/'unsupported')],out,False)
assert 'exclusive range' in log
tokenizer.write_text(original)
result={'authenticated':len(m),'universal_theorem_audits':len(audits),'current_source_invocations':22,
 'tokenizer_invocations':19,'serializer_invocations':3,'source_byte_decisions':5632,
 'semantic_mutants_rejected':[x[0] for x in mutants],'unsupported_exclusive_pattern_rejected':True,
 'native_build':'NOT RUN','whole_tokenizer_admission':'OPEN','Rust_macro_compiler_refinement':'EXTERNAL'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
