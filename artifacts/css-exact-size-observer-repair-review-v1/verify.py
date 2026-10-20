import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require -I -S without optimization')
sys.dont_write_bytecode=True
import argparse
import hashlib
import json
from pathlib import Path
import stat

ROOT=Path(__file__).resolve().parent

def pairs(items):
    d={}
    for k,v in items:
        if k in d: raise SystemExit('Duplicate key')
        d[k]=v
    return d

def load(p):
    return json.loads(p.read_text(),object_pairs_hook=pairs)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def require(v,message):
    if not v: raise SystemExit(message)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--files-sha256',required=True)
    a=ap.parse_args()
    require(sha(ROOT/'FILES.json')==a.files_sha256,'Review manifest')
    files=load(ROOT/'FILES.json');dirs=set()
    for n in files:
        p=Path(n)
        require(not p.is_absolute() and '..' not in p.parts and str(p)==n,'Path')
        dirs.update(str(x) for x in p.parents if str(x)!='.')
    actual=set();actual_dirs=set()
    for p in ROOT.rglob('*'):
        mode=p.lstat().st_mode;name=p.relative_to(ROOT).as_posix()
        if stat.S_ISDIR(mode):actual_dirs.add(name)
        elif stat.S_ISREG(mode):actual.add(name)
        else:raise SystemExit('Nonregular')
    require(actual==set(files)|{'FILES.json'} and actual_dirs==dirs,'Review roster')
    for n,h in files.items():require(sha(ROOT/n)==h,'Review input '+n)
    auth=load(ROOT/'AUTHENTICATION.json');producer=ROOT.parent/Path(auth['producer']).name
    require(sha(producer/'FILES.json')==auth['FILES_sha256'],'Producer manifest')
    manifest=load(producer/'FILES.json')['files']
    names=[x['path'] for x in manifest];require(len(names)==len(set(names))==auth['payloads'],'Producer roster')
    for r in manifest:
        p=Path(r['path']);require(not p.is_absolute() and '..' not in p.parts,'Producer path')
        f=producer/p;require(f.is_file() and not f.is_symlink() and sha(f)==r['sha256'] and f.stat().st_size==r['bytes'],'Producer input')
    for row in load(ROOT/'SOURCE-INVENTORY.json'):
        source=producer/row['path'];require(sha(source)==row['file_sha256'],'Source role')
        require(row['body'] in source.read_text() and hashlib.sha256(row['body'].encode()).hexdigest()==row['body_sha256'],'Source body')
    for row in load(ROOT/'SPLIT-ROUNDTRIP.json'):require(row['exact_apply_reverse'],'Roundtrip')
    counts=[row['test_count'] for row in load(ROOT/'WPT-REGISTRATIONS.json')]
    require(counts==[28,4,4],'Registration inventory')
    print(json.dumps({'status':'PASS','review_payloads':len(files),'producer_payloads':len(manifest),'selected_bodies':len(load(ROOT/'SOURCE-INVENTORY.json')),'wpt_counts':counts}))

if __name__=='__main__':main()
