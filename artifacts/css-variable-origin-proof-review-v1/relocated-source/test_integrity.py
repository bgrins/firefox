#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert ROOT not in out.parents and out!=ROOT and not out.exists();out.mkdir(parents=True)
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
results=[]
for name in ['changed-source','missing-source','shadow-module','empty-directory','fifo','symlink-directory','duplicate-json','internal-output']:
    capsule=out/name;capsule.mkdir()
    for rel in [*manifest,'MANIFEST.json',*(['FREEZE.json'] if (ROOT/'FREEZE.json').exists() else [])]:
        dest=capsule/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
    external=out/(name+'-result')
    if name=='changed-source':(capsule/'lean/Origin.lean').write_text('import Std\n')
    elif name=='missing-source':(capsule/'native/oracle.py').unlink()
    elif name=='shadow-module':(capsule/'native/json.py').write_text('raise RuntimeError("shadow executed")\n')
    elif name=='empty-directory':(capsule/'unlisted').mkdir()
    elif name=='fifo':
        import os
        os.mkfifo(capsule/'pipe')
    elif name=='symlink-directory':(capsule/'external').symlink_to(out,target_is_directory=True)
    elif name=='duplicate-json':
        text=(capsule/'MANIFEST.json').read_text();key=next(iter(manifest));text=text.replace('{','{'+json.dumps(key)+':'+json.dumps(manifest[key])+',',1);(capsule/'MANIFEST.json').write_text(text)
    elif name=='internal-output':external=capsule/'generated'
    r=subprocess.run([sys.executable,'-I','-S',str(capsule/'check.py'),'--output',str(external)],capture_output=True,text=True,timeout=30)
    assert r.returncode!=0 and not external.exists(), (name,r.stdout,r.stderr)
    assert 'shadow executed' not in r.stdout+r.stderr
    results.append({'case':name,'exit':r.returncode,'rejected_before_output':True,'stderr':r.stderr})
    shutil.rmtree(capsule)
(out/'RESULT.json').write_text(json.dumps({'status':'PASS','controls':results},indent=2)+'\n')
print(json.dumps({'status':'PASS','controls':len(results)}))
