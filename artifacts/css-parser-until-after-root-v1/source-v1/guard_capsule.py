import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S without optimization")
from pathlib import Path
import argparse, json, os, shutil, subprocess
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();out=a.output.resolve()
if out==ROOT or ROOT in out.parents:raise RuntimeError('external output required')
out.mkdir(parents=True,exist_ok=False)
records=[]
labels=['optimized','double-optimized','nonisolated','site-enabled','shadow-json','missing-input','altered-input','extra-file','nested-seal','empty-directory','symlink-file','symlink-directory','fifo','duplicate-row','path-escape','seal-symlink','checker-change','output-inside','intact-help']
for label in labels:
    stage=out/'stage';shutil.copytree(ROOT,stage)
    output=out/('forbidden-'+label)
    flags=['-I','-S'];args=['--output',str(output)]
    if label=='optimized':flags+=['-O']
    elif label=='double-optimized':flags+=['-OO']
    elif label=='nonisolated':flags=['-S']
    elif label=='site-enabled':flags=['-I']
    elif label=='shadow-json':
        flags=['-S'];(stage/'json.py').write_text('print("UNSAFE_IMPORT_EXECUTED")\n')
    elif label=='missing-input':(stage/'lean/UntilAfter.lean').unlink()
    elif label=='altered-input':
        q=stage/'lean/UntilAfter.lean';q.write_text(q.read_text()+'\n')
    elif label=='extra-file':(stage/'unexpected.txt').write_text('extra')
    elif label=='nested-seal':(stage/'lean/FILES.json').write_text('{}')
    elif label=='empty-directory':(stage/'unexpected-directory').mkdir()
    elif label=='symlink-file':
        q=stage/'lean/UntilAfter.lean';q.unlink();q.symlink_to(ROOT/'lean/UntilAfter.lean')
    elif label=='symlink-directory':(stage/'linked-directory').symlink_to(ROOT/'lean',target_is_directory=True)
    elif label=='fifo':os.mkfifo(stage/'fifo')
    elif label in ['duplicate-row','path-escape']:
        q=stage/'FILES.json';rows=json.loads(q.read_text())
        if label=='duplicate-row':rows.append(rows[0])
        else:rows[0]['path']='../escape'
        q.write_text(json.dumps(rows))
    elif label=='seal-symlink':
        q=stage/'FREEZE.json';q.unlink();q.symlink_to(ROOT/'FREEZE.json')
    elif label=='checker-change':
        q=stage/'check.py';q.write_text(q.read_text()+'\n')
    elif label=='output-inside':output=stage/'output';args=['--output',str(output)]
    elif label=='intact-help':args=['--help']
    command=[sys.executable,*flags,str(stage/'check.py'),*args]
    r=subprocess.run(command,capture_output=True,text=True)
    ok=(r.returncode==0 if label=='intact-help' else r.returncode!=0) and not output.exists() and 'UNSAFE_IMPORT_EXECUTED' not in r.stdout+r.stderr
    records.append(dict(label=label,command=command,exit=r.returncode,stdout=r.stdout,stderr=r.stderr,output_absent=not output.exists(),pass_gate=ok))
    (out/'GUARDS.json').write_text(json.dumps(records,indent=2)+'\n')
    shutil.rmtree(stage)
    if not ok:raise RuntimeError('guard failed: '+label)
print(json.dumps(dict(negative=18,positive=1,status='PASS')))
