import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S without optimization')
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
ROOT = Path(__file__).resolve().parent

def require(value, message):
    if not value:
        raise ValueError(message)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
    result = {}
    for k,v in pairs:
        require(k not in result, 'duplicate key')
        result[k]=v
    return result
def read(name):
    return json.loads((ROOT/name).read_text(), object_pairs_hook=unique)
if len(sys.argv)!=2:
    raise SystemExit('expected external FILES hash')
for seal in ['FILES.json','FREEZE.json']:
    require(stat.S_ISREG((ROOT/seal).lstat().st_mode),'nonregular seal')
require(sha(ROOT/'FILES.json')==sys.argv[1],'external manifest mismatch')
files=read('FILES.json');dirs=set()
for name,value in files.items():
    p=PurePosixPath(name)
    require(str(p)==name and not p.is_absolute() and '..' not in p.parts and name not in ['FILES.json','FREEZE.json'],'invalid path')
    require(isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value),'invalid hash')
    dirs.update(str(parent) for parent in p.parents if str(parent)!='.')
found=set()
def walk(directory):
    for e in os.scandir(directory):
        p=Path(e.path);rel=p.relative_to(ROOT).as_posix();mode=e.stat(follow_symlinks=False).st_mode
        if stat.S_ISDIR(mode):
            require(rel in dirs,'unexpected directory');walk(p)
        else:
            require(stat.S_ISREG(mode),'nonregular input')
            if rel in ['FILES.json','FREEZE.json']:
                continue
            require(rel in files and sha(p)==files[rel],'input mismatch: '+rel)
            found.add(rel)
walk(ROOT)
require(found==set(files),'missing input')
seal=read('FREEZE.json')
require(seal['FILES_sha256']==sys.argv[1] and seal['check_sha256']==sha(ROOT/'check.py'),'seal mismatch')
for row in read('SOURCE-PINS.json'):
    require(sha(ROOT/row['file'])==row['sha256'],'source pin')
spec=importlib.util.spec_from_file_location('binding',ROOT/'bind.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
require(m.bindings()==read('BINDINGS.json'),'body binding mismatch')
for row in read('VERSION-COMPARISONS.json'):
    _,_,a=m.selected((ROOT/row['reference']).read_text(),row['anchor'])
    _,_,b=m.selected((ROOT/row['current']).read_text(),row['anchor'])
    require(hashlib.sha256(a.encode()).hexdigest()==row['reference_sha256'] and hashlib.sha256(b.encode()).hexdigest()==row['current_sha256'] and (a==b)==row['exact'],'version comparison')
require(len(read('BINDINGS.json')) == 16, 'binding roster')
require(len(read('VERSION-COMPARISONS.json')) == 2, 'comparison roster')
print(json.dumps({'result':'PASS','inputs':len(files),'source_bindings':16,'exact_body_comparisons':2,'scope':'source-only descriptor access audit; publication-event completeness and callback lifetime remain open'}))
