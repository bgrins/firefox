import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import hashlib
import json
import stat
import subprocess
import tempfile
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--runtime',type=Path,required=True)
p.add_argument('--prior',type=Path,required=True)
a=p.parse_args()
here=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def need(ok,why):
    if not ok:
        raise RuntimeError(why)
need(sha(a.runtime/'FILES.json')=='d61460eb681158d98c6299d3b6605fd066cd6ae9a388039659674180c2daf019','Wrong final runtime manifest')
need(sha(a.runtime/'FREEZE.json')=='9f7141ff97435395a0e4644f596006d61c6ce7641c4c0677ead0f6f36b35be55','Wrong final runtime freeze')
manifest=read(a.runtime/'FILES.json')
actual=set()
for path in a.runtime.rglob('*'):
    mode=path.lstat().st_mode
    if stat.S_ISDIR(mode):
        continue
    need(stat.S_ISREG(mode),'Nonregular runtime payload')
    actual.add(path.relative_to(a.runtime).as_posix())
need(len(manifest)==474 and actual==set(manifest)|{'FILES.json','FREEZE.json'},'Wrong closed runtime roster')
for name,pin in manifest.items():
    need(not Path(name).is_absolute() and '..' not in Path(name).parts and sha(a.runtime/name)==pin,'Runtime payload mismatch '+name)
state=read(a.runtime/'STATE.json')
need(state['status']=='terminal' and state['restored'] and state['restore_build_exit']==0 and not state['recovery_errors'] and 'failure' not in state,'Incomplete restored terminal state')
need(read(a.runtime/'BEFORE.json')==read(a.runtime/'FINAL.json')==read(a.runtime/'INPUTS.json')['before'],'Historical state not restored')
need(set(state['phases'])=={'baseline','principal-only','oof-only','both','original-key','original-key-principal'},'Missing correctness phase')
need(set(state['traces'])=={'trace-baseline','trace-oof-only'},'Missing trace phase')
for phase in list(state['phases'].values())+list(state['traces'].values()):
    need(phase['build_exit']==0 and phase['wpt']['complete'],'Phase incomplete')
need(not read(a.runtime/'both-timing-parent.json')['measurement_complete'],'Combined timing incorrectly accepted')
with tempfile.TemporaryDirectory(prefix='hidden-compact-review-') as scratch:
    output=Path(scratch)/'all.json'
    subprocess.run([sys.executable,'-I','-S',str(here/'analyze.py'),'--runtime',str(a.runtime),'--prior',str(a.prior),'--phases','baseline','principal-only','oof-only','both','original-key','original-key-principal','trace-baseline','trace-oof-only','--output',str(output)],check=True)
    need(output.read_bytes()==(here/'ALL-PHASE-CHECK.json').read_bytes(),'Reconstructed outcome/cost mismatch')
    trace=Path(scratch)/'trace.json'
    subprocess.run([sys.executable,'-I','-S',str(here/'analyze-trace.py'),'--runtime',str(a.runtime),'--output',str(trace)],check=True)
    need(trace.read_bytes()==(here/'TRACE-CHECK.json').read_bytes(),'Reconstructed trace mismatch')
print('PASS: 474 sealed payloads; six correctness phases; two traces; three measured costs; retained combined timeout; historical source/index/HEAD restoration')
