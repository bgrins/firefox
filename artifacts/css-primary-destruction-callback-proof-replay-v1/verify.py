import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S without optimization')
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent
if len(sys.argv) != 2:
    raise SystemExit('expected external FILES hash')
def require(value, message):
    if not value:
        raise ValueError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
require(sha(ROOT/'FILES.json') == sys.argv[1], 'external manifest')
files=json.loads((ROOT/'FILES.json').read_text())
expected_dirs={p.as_posix() for name in files for p in Path(name).parents if p.as_posix()!='.'}
found=set()
for p in ROOT.rglob('*'):
    rel=p.relative_to(ROOT).as_posix();mode=p.lstat().st_mode
    if stat.S_ISDIR(mode):
        require(rel in expected_dirs,'extra directory')
    else:
        require(stat.S_ISREG(mode),'nonregular input')
        if rel in ['FILES.json','FREEZE.json']:
            continue
        require(rel in files and sha(p)==files[rel],'input mismatch '+rel)
        found.add(rel)
require(found==set(files),'missing input')
source=ROOT/'relocated-source'
source_files=json.loads((source/'FILES.json').read_text())
source_roster={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
require(source_roster==set(source_files)|{'FILES.json','FREEZE.json'},'nested source closure')
for name,h in source_files.items():
    require(sha(source/name)==h,'nested source pin')
for case in ['canonical','relocated']:
    result=json.loads((ROOT/case/'RESULT.json').read_text())
    require(result['result']=='PASS' and result['audits']==51 and result['source_bindings']==23 and result['semantic_model_mutants']==4,'replay result')
    for mutation in ['MissingRoot','FollowRaw','MissingDetach','IgnoreRole']:
        stdout=(ROOT/case/(mutation+'.stdout')).read_text()
        require('Tactic `decide` proved that the proposition' in stdout and 'is false' in stdout,'mutation cause')
        require(not (ROOT/case/(mutation+'.stderr')).read_text(),'mutation infrastructure stderr')
guards=json.loads((ROOT/'GUARDS.json').read_text())
require(len(guards)==15 and all(row['passed'] and row['exit']!=0 and row['output_absent'] and row['shadow_absent'] for row in guards),'guards')
print(json.dumps({'result':'PASS','source_payloads':len(source_files),'audits_each':51,'negative_guards':15}))
