#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result

def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate():
    manifest = read_json(ROOT/'MANIFEST.json')
    assert isinstance(manifest,dict) and manifest
    expected_dirs = {''}
    for name, sha in manifest.items():
        path = PurePosixPath(name)
        assert name == path.as_posix() and not path.is_absolute()
        assert all(p not in ('','.','..') for p in path.parts)
        assert re.fullmatch('[0-9a-f]{64}',sha)
        for parent in path.parents:
            if str(parent) != '.':expected_dirs.add(str(parent))
    actual_files=set();actual_dirs={''}
    def visit(directory):
        for entry in os.scandir(directory):
            rel=Path(entry.path).relative_to(ROOT).as_posix()
            mode=entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                actual_dirs.add(rel);visit(entry.path)
            else:
                assert stat.S_ISREG(mode), 'nonregular entry: '+rel
                actual_files.add(rel)
    visit(ROOT)
    allowed=set(manifest)|{'MANIFEST.json'}
    if (ROOT/'FREEZE.json').exists():
        allowed.add('FREEZE.json')
        freeze=read_json(ROOT/'FREEZE.json')
        assert freeze['manifest_sha256']==digest(ROOT/'MANIFEST.json')
        assert freeze['checker_sha256']==digest(ROOT/'check.py')
    assert actual_files==allowed, ('file roster',actual_files^allowed)
    assert actual_dirs==expected_dirs, ('directory roster',actual_dirs^expected_dirs)
    for name,sha in manifest.items():assert digest(ROOT/name)==sha, name
    return manifest

p=argparse.ArgumentParser()
p.add_argument('--output',required=True,type=Path)
p.add_argument('--lean',type=Path)
a=p.parse_args()
initial=authenticate()
out=a.output.resolve()
assert out!=ROOT and ROOT not in out.parents, 'output must be external'
assert not out.exists(), 'output must be fresh'
config=read_json(ROOT/'TOOLCHAIN.json')
lean=a.lean.resolve() if a.lean else Path(config['lean'])
assert digest(lean)==config['lean_sha256']
assert digest(Path(config['rustc']))==config['rustc_sha256']
modules=read_json(ROOT/'AUDITS.json')
out.mkdir(parents=True)
commands=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LEAN_PATH=str(out))

def run(cmd):
    r=subprocess.run([str(x) for x in cmd],cwd=out,env=env,text=True,capture_output=True)
    commands.append({'command':[str(x) for x in cmd],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert r.returncode==0, r.stdout+r.stderr
    return r.stdout

all_names=[]
for module,names in modules.items():
    source=ROOT/'lean'/(module+'.lean')
    assert not re.search(r'\b(sorry|axiom|unsafe)\b',source.read_text())
    found=re.findall(r'(?:@\[[^\]]*\]\s*)?theorem\s+(\w+)',source.read_text())
    assert found==names, ('theorem roster',module)
    run([lean,'--root='+str(ROOT/'lean'),'-o',out/(module+'.olean'),source])
    all_names.extend('VariableOrigin.'+n for n in names)
audit=''.join('import '+m+'\n' for m in modules)+'\n'+''.join('#print axioms '+n+'\n' for n in all_names)
(out/'Audit.lean').write_text(audit)
raw=run([lean,out/'Audit.lean'])
assert 'sorryAx' not in raw
seen=re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms:)",raw)
assert seen==all_names, ('axiom audit roster',seen)
axioms=set()
for block in re.findall(r'depends on axioms:\s*\[([^]]*)\]',raw):
    axioms.update(s.strip() for s in block.split(',') if s.strip())
assert axioms <= {'propext','Quot.sound','Classical.choice'}, axioms
(out/'AXIOMS.txt').write_text(raw)
run([sys.executable,'-I','-S','-B',ROOT/'native/build.py','--output',out/'native'])
run([sys.executable,'-I','-S','-B',ROOT/'native/oracle.py',out/'native'])
source_binding=read_json(ROOT/'SOURCE-BINDING.json')
for variant in ['original','candidate']:
    records=read_json(out/'native'/(variant+'-bindings.json'))
    assert records==source_binding[variant], ('extraction integrity',variant)
assert authenticate()==initial
result={'status':'PASS','inputs':len(initial),'lean_modules':len(modules),'audits':len(all_names),
        'axioms':sorted(axioms),'native':read_json(out/'native/ORACLE.json'),
        'complete_source_bindings':{v:sum(x.get('complete') is True for x in source_binding[v]) for v in source_binding}}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='native'}))
