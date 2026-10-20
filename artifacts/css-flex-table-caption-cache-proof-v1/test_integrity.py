import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require isolated nonoptimized Python without site")
sys.dont_write_bytecode=True
from pathlib import Path
import json, shutil, subprocess

ROOT=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve()
if not Path(sys.argv[1]).is_absolute() or out.exists() or out.is_relative_to(ROOT):
    raise SystemExit('fresh external output required')
out.mkdir(parents=True)
records=[]
def challenge(name,flags,edit=None,script='check.py'):
    copy=out/(name+'-source');shutil.copytree(ROOT,copy)
    if edit: edit(copy)
    target=out/(name+'-output')
    command=[sys.executable]+flags+[str(copy/script),'--output',str(target)]
    p=subprocess.run(command,capture_output=True,text=True)
    record=dict(name=name,command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,
                output_created=target.exists(),shadow_executed=(copy/'SHADOW').exists())
    records.append(record);(out/'RESULT.json').write_text(json.dumps(records,indent=2)+'\n')
    if p.returncode==0 or target.exists() or record['shadow_executed'] or 'SHADOW_RAN' in p.stdout+p.stderr:
        raise RuntimeError(record)
    shutil.rmtree(copy)

for name,flags in [('optimized',['-I','-S','-O']),('double-optimized',['-I','-S','-OO']),
                   ('not-isolated',['-S']),('site-enabled',['-I'])]:
    challenge(name,flags)
def shadow(copy):
    (copy/'json.py').write_text("raise RuntimeError('SHADOW_RAN')\n")
challenge('pre-import-shadow',['-S'],shadow)
challenge('extra-file',['-I','-S'],lambda p:(p/'unlisted.txt').write_text('x'))
challenge('extra-directory',['-I','-S'],lambda p:(p/'empty').mkdir())
challenge('nested-seal',['-I','-S'],lambda p:(p/'lean/FILES.json').write_text('{}'))
challenge('changed-source',['-I','-S'],lambda p:(p/'lean/CaptionKey.lean').write_text('import Std\n'))
challenge('missing-source',['-I','-S'],lambda p:(p/'lean/CaptionKey.lean').unlink())
def symlink(copy):
    value=copy/'lean/CaptionKey.lean';value.unlink();value.symlink_to(ROOT/'lean/CaptionKey.lean')
challenge('source-symlink',['-I','-S'],symlink)
for name,script in [('compile-shadow','compile.py'),('native-shadow','native/check.py')]:
    def add_shadow(copy,script=script):
        (copy/script).parent.joinpath('json.py').write_text("raise RuntimeError('SHADOW_RAN')\n")
    challenge(name,['-S'],add_shadow,script)
command=[sys.executable,'-I','-S',str(ROOT/'check.py'),'--help']
p=subprocess.run(command,capture_output=True,text=True)
records.append(dict(name='intact-help-positive',command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
if p.returncode or p.stderr: raise RuntimeError('positive source authentication failed')
(out/'RESULT.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(dict(negative=len(records)-1,positive=1,status='PASS')))
