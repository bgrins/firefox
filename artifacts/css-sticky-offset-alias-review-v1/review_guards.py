import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:raise SystemExit('use Python -I -S')
sys.dont_write_bytecode=True
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seal(root):
    files={p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root).as_posix() not in ['FILES.json','FREEZE.json']}
    (root/'FILES.json').write_text(json.dumps({'files':files},indent=2)+'\n')
    (root/'FREEZE.json').write_text(json.dumps({'manifest_sha256':sha(root/'FILES.json')})+'\n')
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
source=Path(args.source).resolve();out=Path(args.out).resolve()
if out.exists() or source==out or source in out.parents:raise ValueError('new external output')
out.mkdir(parents=True);records=[]
for name in ['nested-cache-outer-resealed','nested-source-outer-resealed','nested-seals-outer-resealed','outer-duplicate-json','optimized','nonisolated']:
    clone=out/'temporary-source';shutil.copytree(source,clone);flags=['-I','-S']
    if name.startswith('nested-cache') or name.startswith('nested-seals'):
        q=clone/'capsule/native/__pycache__';q.mkdir();(q/'source.pyc').write_bytes(b'not accepted as extra imported cache')
        if name.startswith('nested-seals'):seal(clone/'capsule')
        seal(clone)
        expected='nested pin' if name.startswith('nested-seals') else 'closed file roster'
    elif name.startswith('nested-source'):
        with (clone/'capsule/core.py').open('a') as f:f.write('\nraise RuntimeError("tampered")\n')
        seal(clone);expected='source hash: core.py'
    elif name=='outer-duplicate-json':
        f=clone/'FILES.json';f.write_text(f.read_text().replace('"files":','"files": {}, "files":',1));(clone/'FREEZE.json').write_text(json.dumps({'manifest_sha256':sha(f)}));expected='duplicate JSON key'
    elif name=='optimized':flags+=['-O'];expected='require Python'
    else:flags=['-S'];expected='require Python'
    r=subprocess.run([sys.executable,*flags,str(clone/'check.py'),'--authenticate-only'],capture_output=True,text=True)
    text=r.stdout+r.stderr;(out/(name+'.log')).write_text(text)
    if r.returncode==0 or expected not in text:raise ValueError(name+' '+text)
    records.append({'name':name,'exit':r.returncode,'expected':expected});shutil.rmtree(clone)
(out/'RESULT.json').write_text(json.dumps({'status':'pass','guards':records},indent=2)+'\n');print(json.dumps({'status':'pass','guards':len(records)}))
