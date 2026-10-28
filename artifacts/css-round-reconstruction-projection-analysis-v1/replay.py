import argparse,hashlib,json,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output.resolve()
assert not out.exists() and H not in out.parents and out!=H
out.mkdir()
solver=Path('/opt/homebrew/bin/z3');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'solver_path':str(solver),'solver_sha256':sha(solver),'solver_version':subprocess.check_output([str(solver),'-version'],text=True).strip(),'threads':1,'timeout_ms':45000,'queries':{}}
for name in ['distance-positive','distance-negative','bad-tie-adapter','small-step-projection','small-step-exact-enclosure','bad-omitted-small-premise','small-step-nonvacuity']:
 start=time.monotonic()
 with (out/(name+'.log')).open('wb') as log:
  try:
   run=subprocess.run([str(solver),str(H/(name+'.smt2'))],stdout=log,stderr=subprocess.STDOUT,timeout=55)
   code=run.returncode
  except subprocess.TimeoutExpired:code='outer_timeout'
 text=(out/(name+'.log')).read_text();status=text.splitlines()[0] if text else 'empty'
 result['queries'][name]={'input_sha256':sha(H/(name+'.smt2')),'log_sha256':sha(out/(name+'.log')),'exit':code,'status':status,'seconds':time.monotonic()-start}
 print(name,status,flush=True)
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')

expected={'distance-positive':'unsat','distance-negative':'unsat','bad-tie-adapter':'sat','small-step-projection':'unsat','small-step-exact-enclosure':'unsat','bad-omitted-small-premise':'sat','small-step-nonvacuity':'sat'}
if not all(v['exit']==0 and v['status']==expected[n] for n,v in result['queries'].items()):
 raise SystemExit(1)
