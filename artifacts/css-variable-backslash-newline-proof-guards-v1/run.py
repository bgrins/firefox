import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use -I -S without optimization")
from pathlib import Path
import hashlib, json, os, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'css-variable-backslash-newline-proof-v1'
records=[]
def run(cmd):
    p=subprocess.run(cmd,text=True,capture_output=True)
    return dict(command=cmd,exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
with tempfile.TemporaryDirectory(prefix='fix86-guards-',dir='/private/tmp') as tmp:
    tmp=Path(tmp)
    for entry in ['check.py','compile.py','native/build_projection.py']:
        home=tmp/entry.replace('/','-');home.mkdir()
        script=home/'entry.py';shutil.copy2(SOURCE/entry,script)
        marker=home/'IMPORTED'
        (home/'json.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("executed")\n')
        for mode,flags in [('unisolated',[]),('site-enabled',['-I']),('site-disabled-unisolated',['-S']),('optimized',['-I','-S','-O']),('double-optimized',['-I','-S','-OO'])]:
            out=home/('forbidden-'+mode)
            row=run([sys.executable,*flags,str(script),'--output',str(out)])
            row.update(kind='mode-shadow',entrypoint=entry,mode=mode,entry_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),marker_created=marker.exists(),output_created=out.exists())
            records.append(row)
            if row['exit']!=1 or 'RuntimeError' not in row['stderr'] or marker.exists() or out.exists():raise RuntimeError(row)
    for kind in ['nested-seal','empty-directory','fifo','directory-link','intact']:
        home=tmp/kind;shutil.copytree(SOURCE,home)
        if kind=='nested-seal':(home/'lean/FILES.json').write_text('{}')
        if kind=='empty-directory':(home/'extra').mkdir()
        if kind=='fifo':os.mkfifo(home/'extra')
        if kind=='directory-link':(home/'extra').symlink_to(home/'lean',target_is_directory=True)
        row=run([sys.executable,'-I','-S',str(home/'check.py'),'--help']);row['kind']=kind;records.append(row)
        expected=0 if kind=='intact' else 1
        if row['exit']!=expected or (expected and 'RuntimeError' not in row['stderr']):raise RuntimeError(row)
(ROOT/'GUARDS.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(dict(complete=True,negative=19,positive=1)))
