import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require -I -S without optimization')
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--files-sha256',required=True)
parser.add_argument('--output',required=True)
a=parser.parse_args()
check=subprocess.run([sys.executable,'-I','-S','-B',str(ROOT/'verify.py'),'--files-sha256',a.files_sha256],capture_output=True,text=True)
if check.returncode:raise SystemExit(check.stdout+check.stderr)
out=Path(a.output)
if not out.is_absolute() or out.exists() or out.is_symlink():raise SystemExit('new absolute output required')
out=out.resolve()
if out==ROOT or ROOT in out.parents:raise SystemExit('output must be outside review')
out.mkdir(parents=True)
(out/'authentication.log').write_text(check.stdout+check.stderr)
try:
 command=[sys.executable,'-I','-S','-B',str(ROOT/'source/check.py'),'--files-sha256','c9d46c3317fb6756068607237405939930da2f23d2096acec6b5091a30aaace9','--output',str(out/'producer')]
 r=subprocess.run(command,capture_output=True,text=True)
 (out/'producer.log').write_text(r.stdout+r.stderr)
 assert r.returncode==0,r.stdout+r.stderr
 tool=json.loads((ROOT/'source/TOOLCHAIN.json').read_text())
 lean=Path(tool['lean'])
 assert hashlib.sha256(lean.read_bytes()).hexdigest()==tool['sha256']
 env=os.environ.copy();env['LEAN_PATH']=str(out/'producer/proof');env.pop('LEAN_OPTS',None)
 r=subprocess.run([str(lean),str(ROOT/'Challenges.lean')],cwd=ROOT,env=env,capture_output=True,text=True)
 (out/'Challenges.stdout').write_text(r.stdout);(out/'Challenges.stderr').write_text(r.stderr)
 assert r.returncode==0 and not r.stderr and r.stdout==(ROOT/'CHALLENGES.log').read_text()
 (out/'RESULT.json').write_text(json.dumps({'producer_audits':74,'independent_checks':7,'result':'PASS'})+'\n')
finally:
 removed=[]
 for file in (out/'producer/proof').glob('*.olean'):
  removed.append({'path':str(file.relative_to(out)),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()});file.unlink()
 (out/'CLEANUP.json').write_text(json.dumps(removed,indent=2)+'\n')
print('PASS: fresh producer and independent checks; olean products removed')
