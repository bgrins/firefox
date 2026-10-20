import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib
import json
import stat
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def require(v,msg):
    if not v:raise SystemExit(msg)
def unique(items):
    result={}
    for k,v in items:
        require(k not in result,'Duplicate JSON key');result[k]=v
    return result
def load(p):return json.loads(p.read_bytes(),object_pairs_hook=unique)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def path(root,name):
    p=Path(name)
    require(not p.is_absolute() and p.as_posix()==name and bool(p.parts) and all(x not in ['.','..'] for x in p.parts),'Invalid relative path')
    q=root
    for part in p.parts:
        q=q/part;require(not q.is_symlink(),'Symlink')
    require(stat.S_ISREG(q.lstat().st_mode),'Nonregular file')
    return q
def capsule(root,pin):
    require(digest(root/'FILES.json')==pin,'External manifest pin')
    rows=load(root/'FILES.json')['files'];seen=set()
    for r in rows:
        require(r['path'] not in seen,'Duplicate manifest path');seen.add(r['path'])
        p=path(root,r['path']);require(p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],'Payload mismatch')
    dirs={'.'}
    for n in seen|{'FILES.json','FREEZE.json'}:
        dirs.update(str(x) for x in Path(n).parents)
    actual=set()
    for p in root.rglob('*'):
        rel=p.relative_to(root).as_posix();mode=p.lstat().st_mode
        require(not p.is_symlink(),'Symlink entry')
        if stat.S_ISDIR(mode):require(rel in dirs,'Extra directory')
        else:require(stat.S_ISREG(mode),'Special entry');actual.add(rel)
    require(actual==seen|{'FILES.json','FREEZE.json'},'Closed payload roster')
    return len(rows)
def main():
    require(len(sys.argv)==3 and sys.argv[1]=='--files-sha256','Expected externally pinned review manifest')
    count=capsule(ROOT,sys.argv[2])
    seals=load(ROOT/'RUNTIME-SEALS.json');counts={}
    for name,pin in seals.items():counts[name]=capsule(ROOT.parent/name,pin)
    for fname in ['INPUT-PINS.json','STANDALONE-INPUT-PINS.json']:
        for name,pin in load(ROOT/fname).items():require(digest(path(ROOT.parent,name))==pin,'Review input changed')
    source=load(ROOT/'OBSERVER-SOURCE.json')
    source_name=source['source'].removeprefix('artifacts/')
    require(digest(path(ROOT.parent,source_name))==source['sha256'],'Observer source changed')
    text=path(ROOT.parent,source_name).read_text();start=text.index('void ResizeObserverEntry::SetContentRectAndSize');end=text.index('\n}',start)+2
    require((ROOT/'ResizeObserver-SetContentRectAndSize.txt').read_text()==text[start:end]+'\n','Complete observer body extraction')
    for name in ['analyze.py','analyze_standalone.py']:
        result=subprocess.run([sys.executable,'-I','-S',str(ROOT/name),'--check'],capture_output=True,text=True)
        require(result.returncode==0,result.stdout+result.stderr)
    require(capsule(ROOT,sys.argv[2])==count,'Review changed during check')
    print(json.dumps({'status':'PASS','review_payloads':count,'runtime_payloads':counts,'raw_reconstructions':2}))
if __name__=='__main__':main()
