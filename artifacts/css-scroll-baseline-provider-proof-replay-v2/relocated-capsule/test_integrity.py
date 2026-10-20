import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
out=args.output.resolve()
if not args.output.is_absolute() or out.exists() or out.is_relative_to(ROOT): raise ValueError('absent external output')
out.mkdir(parents=True)
rows=json.loads((ROOT/'FILES.json').read_text())
records=[]
def copy(name):
    target=out/name;target.mkdir()
    for row in rows+[{'path':'FILES.json'},{'path':'FREEZE.json'}]:
        dest=target/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],dest)
    return target
def reseal(target):
    manifest=json.loads((target/'FILES.json').read_text())
    for row in manifest:
        file=target/row['path'];row['bytes']=file.stat().st_size;row['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
    (target/'FILES.json').write_text(json.dumps(manifest,indent=2)+'\n')
    freeze=json.loads((target/'FREEZE.json').read_text());freeze['FILES_sha256']=hashlib.sha256((target/'FILES.json').read_bytes()).hexdigest()
    (target/'FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
def challenge(name,change=None,flags=None,entry='check.py',needle=None,output_inside=False):
    target=copy(name);destination=target/'bad-output' if output_inside else out/(name+'-output')
    if change: change(target)
    cmd=[sys.executable,*(flags if flags is not None else ['-I','-S']),str(target/entry),'--output',str(destination)]
    result=subprocess.run(cmd,capture_output=True,text=True,cwd=target)
    if result.returncode==0 or destination.exists() or (out/'shadow-marker').exists():
        raise RuntimeError('guard did not reject before execution/output: '+name)
    if needle and needle not in result.stdout+result.stderr: raise RuntimeError('wrong rejection: '+name+result.stderr)
    records.append({'name':name,'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'no_output':True})
    shutil.rmtree(target)
for mode,flags in [('optimized',['-I','-S','-O']),('double-optimized',['-I','-S','-OO']),('not-isolated',['-S']),('site-enabled',['-I'])]:
    challenge(mode,flags=flags,needle='Require python3')
for index,entry in enumerate(['check.py','compile.py','model_mutants.py','source_bindings.py','native/build.py','native/cases.py','test_integrity.py']):
    def shadow(target,entry=entry):
        file=target/Path(entry).parent/'json.py'
        file.write_text('from pathlib import Path\nPath('+repr(str(out/'shadow-marker'))+').write_text("unsafe")\n')
    challenge('shadow-'+str(index),shadow,flags=['-S'],entry=entry,needle='Require python3' if entry=='check.py' else 'isolated')
challenge('extra-file',lambda t:(t/'extra').write_text('x'),needle='file roster')
challenge('extra-directory',lambda t:(t/'extra').mkdir(),needle='unexpected directory')
challenge('nested-seal',lambda t:(t/'lean/FILES.json').write_text('{}'),needle='file roster')
challenge('symlink',lambda t:(t/'extra').symlink_to(t/'REPORT.md'),needle='nonregular entry')
challenge('source-tamper',lambda t:(t/'source/candidate.cpp').write_text('tampered'),needle='input mismatch')
challenge('output-inside',output_inside=True,needle='absent external output')
def duplicate(t):
    file=t/'FILES.json';m=json.loads(file.read_text());m.append(m[0]);file.write_text(json.dumps(m))
challenge('duplicate-manifest',duplicate,needle='duplicate / reserved')
def case_change(t,kind):
    file=t/'CASES.json';r=json.loads(file.read_text())
    if kind=='bool':r[0]['first']=0
    elif kind=='omitted':r.pop()
    elif kind=='reordered':r[0],r[1]=r[1],r[0]
    file.write_text(json.dumps(r));reseal(t)
for kind in ['bool','omitted','reordered']:
    challenge('resealed-case-'+kind,lambda t,kind=kind:case_change(t,kind),needle='case roster / schema')
cmd=[sys.executable,'-I','-S',str(ROOT/'check.py'),'--help']
positive=subprocess.run(cmd,capture_output=True,text=True)
if positive.returncode: raise RuntimeError('intact positive rejected '+positive.stderr)
records.append({'name':'intact-help','command':cmd,'exit':positive.returncode,'stdout':positive.stdout,'stderr':positive.stderr})
(out/'RESULTS.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({'negative':len(records)-1,'positive':1,'status':'PASS'}))
