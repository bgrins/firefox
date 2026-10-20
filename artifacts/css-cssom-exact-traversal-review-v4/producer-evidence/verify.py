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
require(seal['FILES_sha256']==sys.argv[1] and seal['check_sha256']==sha(ROOT/'verify.py'),'seal mismatch')
spec=importlib.util.spec_from_file_location('nested_replay',ROOT/'capsule/replay.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pin='e5171412e9d35ae3280fe194e803b3a2a6674242d262e70abdc4ddee62b1f720'
m.authenticate(pin)
import difflib
paths={'nsIFrame.cpp':'layout/generic/nsIFrame.cpp','nsIFrame.h':'layout/generic/nsIFrame.h','nsLayoutUtils.cpp':'layout/base/nsLayoutUtils.cpp','nsLayoutUtils.h':'layout/base/nsLayoutUtils.h','DOMRect.cpp':'dom/base/DOMRect.cpp'}
for role,name in [('original','proposal.patch'),('v3','v3-to-v4.patch')]:
    patch=''
    for file,path in paths.items():
        a=(ROOT/'capsule'/role/file).read_text();b=(ROOT/'capsule/candidate'/file).read_text()
        patch+=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
    require(patch==(ROOT/name).read_text(),'patch source mismatch')
transfer=read('SOURCE-TRANSFER.json')
require(transfer['changes']==['CANDIDATE-PINS.json','candidate/nsIFrame.cpp','replay.py'],'unexpected predecessor input change')
require(all(row['exact_v3_candidate'] for row in transfer['v3_role_copies']),'v3 source transfer')
for row in transfer['copied_v3_inputs']:
    require(sha(ROOT/'capsule'/row['path'])==row['v4_sha256'],'transfer current pin')
controls=read('GUARD-CONTROLS.json')
require(len(controls)==10 and all(x['exit']!=0 and not x['output_created'] and not x['shadow_executed'] for x in controls),'guard records')
result=read('REPLAY-COMPARISON.json')
require(result['result_equal'] and len(result['final_result']['runs'])==26,'replay result roster')
require(all(x['path_normalized_equal'] for x in result['files']),'relocation observations')
require(all(x['apply_reverse_exact'] for x in read('PATCH-ROUNDTRIP.json')['roundtrips']),'patch receipts')
print(json.dumps({'result':'PASS','inputs':len(files),'closed_capsule_pin':pin,'replay_runs':26,'guards':10,'scope':'source proposal and retained extracted calibration; no native/performance acceptance'}))
