import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize: raise SystemExit('use -I -S')
from pathlib import Path
import subprocess,tempfile,json,hashlib
ROOT=Path(__file__).resolve().parent
results=[]
with tempfile.TemporaryDirectory(prefix='css-v4-independent-') as tmp:
 for role in ['v3','candidate']:
  raw=(ROOT/'replay'/(role+'.cpp')).read_text()
  start=raw.index('int main(')
  source=ROOT/(role+'-extra.cpp')
  source.write_text(raw[:start]+(ROOT/'extra-main.cpp').read_text())
  for opt in ['-O0','-O2']:
   exe=Path(tmp)/'extra'
   args=['/usr/bin/clang++','-std=c++20',opt,'-fsanitize=undefined','-fno-sanitize-recover=all','-I',str(ROOT/'source/include'),str(source),'-o',str(exe)]
   build=subprocess.run(args,capture_output=True,text=True)
   (ROOT/(role+opt+'-extra-compile.log')).write_text(build.stdout+build.stderr)
   assert build.returncode==0,build.stderr
   run=subprocess.run([str(exe)],capture_output=True,text=True)
   (ROOT/(role+opt+'-extra-run.log')).write_text(run.stdout+run.stderr)
   results.append(dict(role=role,optimization=opt,compile_exit=build.returncode,run_exit=run.returncode,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
   assert run.returncode==0,run.stdout+run.stderr
   assert 'NULL_BOUNDARIES_PASS' in run.stdout and 'INDEPENDENT_PASS dispatch=48 masks=16 geometry=4 arithmetic=81' in run.stdout
for opt in ['-O0','-O2']:
 assert (ROOT/('v3'+opt+'-extra-run.log')).read_bytes()==(ROOT/('candidate'+opt+'-extra-run.log')).read_bytes()
(ROOT/'EXTRA-RESULT.json').write_text(json.dumps(dict(runs=results,compiler_outputs_cleaned=True),indent=2)+'\n')
print(json.dumps(dict(runs=len(results),all_pass=True,compiler_outputs_cleaned=True)))
