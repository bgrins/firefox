import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, stat, subprocess
from pathlib import Path, PurePosixPath
R=Path(__file__).resolve().parent

def pairs(items):
    d={}
    for k,v in items:
        assert k not in d
        d[k]=v
    return d

def read(p):
    return json.loads(p.read_text(),object_pairs_hook=pairs)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def auth():
    m=read(R/'MANIFEST.json')
    assert read(R/'FREEZE.json')['manifest_sha256']==sha(R/'MANIFEST.json')
    allowed=set(m)|{'MANIFEST.json','FREEZE.json'}
    actual=set();dirs=set();needed=set()
    for p in R.rglob('*'):
        mode=p.lstat().st_mode
        assert not stat.S_ISLNK(mode)
        if stat.S_ISDIR(mode):dirs.add(p.relative_to(R).as_posix())
        else:
            assert stat.S_ISREG(mode)
            actual.add(p.relative_to(R).as_posix())
    assert actual==allowed
    for n in allowed:
        p=PurePosixPath(n)
        assert not p.is_absolute() and '..' not in p.parts and str(p)==n
        needed.update(str(x) for x in p.parents if str(x)!='.')
    assert dirs==needed
    for n,h in m.items():assert sha(R/n)==h,n
    assert sha(R/'dependency/CHECKPOINT.json')=='2667921b7a4804190b0af210bb88aaa9e5990de8a4ef7f828d88be1ab59ad2f3'
    assert sha(R/'dependency/replay.py')=='5e0662187e3efcac16483b4c1730833bfb678e5157221ea2f06d34c76807e9e6'
    for n,h in read(R/'dependency/CHECKPOINT.json')['sources'].items():assert sha(R/n)==h,n
    for rec in read(R/'SOURCE-BINDINGS.json'):
        source=(R/rec['source']).read_text();body=rec['body']
        assert source[rec['start']:rec['start']+len(body)]==body
        assert body.startswith('    '+rec['anchor'])
        assert hashlib.sha256(body.encode()).hexdigest()==rec['sha256']
    return len(m)

p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
count=auth()
if a.output:
    out=a.output.resolve()
    assert not out.exists() and not out.is_relative_to(R)
    subprocess.run([sys.executable,'-I','-S',str(R/'replay.py'),'--output',str(out)],check=True)
print(json.dumps({'authenticated_inputs':count,'source_bodies':len(read(R/'SOURCE-BINDINGS.json'))}))
