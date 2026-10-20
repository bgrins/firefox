import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without -O/-OO')
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, re, stat, subprocess
ROOT=Path(__file__).resolve().parent
def require(value, message):
    if not value: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        require(key not in result, 'duplicate JSON key: '+key)
        result[key]=value
    return result
def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)
def authenticate():
    for name in ['FILES.json','FREEZE.json']:
        require(stat.S_ISREG((ROOT/name).lstat().st_mode), 'nonregular root seal: '+name)
    manifest=read_json(ROOT/'FILES.json')
    require(isinstance(manifest,list) and manifest, 'invalid manifest')
    expected_files={'FILES.json','FREEZE.json'};expected_dirs={''}
    for row in manifest:
        require(isinstance(row,dict) and set(row)=={'path','bytes','sha256'}, 'invalid manifest row')
        name=row['path'];require(isinstance(name,str), 'invalid manifest path')
        path=PurePosixPath(name)
        require(name==path.as_posix() and bool(path.parts) and not path.is_absolute()
            and all(part not in ('','.','..') for part in path.parts), 'invalid manifest path')
        require(name not in expected_files, 'duplicate / reserved manifest path')
        require(type(row['bytes']) is int and row['bytes']>=0, 'invalid input size')
        require(isinstance(row['sha256'],str) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'invalid digest')
        expected_files.add(name)
        for parent in path.parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    actual_files=set();actual_dirs={''}
    def visit(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                rel=Path(entry.path).relative_to(ROOT).as_posix()
                mode=entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    require(rel in expected_dirs, 'unexpected directory: '+rel)
                    actual_dirs.add(rel);visit(entry.path)
                else:
                    require(stat.S_ISREG(mode), 'nonregular entry: '+rel)
                    actual_files.add(rel)
    visit(ROOT)
    require(actual_files==expected_files, 'file roster mismatch')
    require(actual_dirs==expected_dirs, 'directory roster mismatch')
    for row in manifest:
        path=ROOT/row['path']
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'], 'input mismatch: '+row['path'])
    freeze=read_json(ROOT/'FREEZE.json')
    require(freeze['FILES_sha256']==sha(ROOT/'FILES.json'), 'manifest seal mismatch')
    require(freeze['check_sha256']==sha(ROOT/'check.py'), 'checker seal mismatch')
    return manifest
initial_manifest=authenticate()
config=json.loads((ROOT/'TOOLCHAIN.json').read_text())
for name in ['lean','rustc']:
    require(sha(Path(config[name]))==config[name+'_sha256'], 'toolchain mismatch: '+name)
for row in json.loads((ROOT/'IMPORTS.json').read_text()):
    require(sha(ROOT/'lean'/(row['module']+'.lean'))==row['sha256'], 'import mismatch')
for row in json.loads((ROOT/'SOURCE-PINS.json').read_text()):
    require(sha(ROOT/row['retained'])==row['sha256'], 'source mismatch')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
require(out!=ROOT and ROOT not in out.parents, 'output must be outside capsule')
out.mkdir(parents=True,exist_ok=False)
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))}
commands=[]
def run(command,expected=0,extra_env=None):
    result=subprocess.run(command,cwd=out,env=extra_env or env,text=True,capture_output=True)
    commands.append({'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(result.returncode==expected if expected is not None else result.returncode!=0, 'unexpected command result: '+str(command))
    return result
run([sys.executable,'-I','-S',str(ROOT/'compile.py'),'--output',str(out/'lean'),'NestedAudit','NestedDriver'])
compile_commands=json.loads((out/'lean/COMMANDS.json').read_text())
audit=next(row['stdout'] for row in compile_commands if row['command'][-1].endswith('/NestedAudit.lean'))
(out/'AUDIT.txt').write_text(audit)
names=json.loads((ROOT/'AUDIT-NAMES.json').read_text())
audit_rows=re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",audit)
require([row[0] for row in audit_rows]==names, 'audit roster mismatch')
for _,_,axioms in audit_rows:
    require(set(axioms.split(', ')) <= {'','propext','Classical.choice','Quot.sound'}, 'unapproved axiom')
lean_env={**env,'LEAN_PATH':str(out/'lean')}
model_run=run([config['lean'],'--root='+str(ROOT/'lean'),'--run',str(ROOT/'lean/NestedDriver.lean')],extra_env=lean_env)
require(not model_run.stderr, 'model diagnostic / unsupported provider')
model=model_run.stdout
(out/'model.txt').write_text(model)
for label,flags in [('debug',[]),('release',['--release'])]:
    run([sys.executable,'-I','-S',str(ROOT/'native/build.py'),'--output',str(out/('native-'+label))]+flags)
    require((out/('native-'+label)/'raw.txt').read_text()==model,'native/model mismatch: '+label)
mutants={}
for mutation in json.loads((ROOT/'MUTATIONS.json').read_text()):
    target=out/('native-'+mutation['id'])
    run([sys.executable,'-I','-S',str(ROOT/'native/build.py'),'--output',str(target),'--mutation',mutation['id']])
    rows=(target/'raw.txt').read_text().splitlines(); expected=model.splitlines()
    require(len(rows)==len(expected),'mutant row count')
    changed=sum(a!=b for a,b in zip(rows,expected));require(changed>0,'undetected native mutant')
    mutants[mutation['id']]=changed
lean_mutants={}
for mutation in json.loads((ROOT/'LEAN-MUTATIONS.json').read_text()):
    source=(ROOT/'lean'/(mutation['module']+'.lean')).read_text()
    require(source.count(mutation['old'])==1,'ambiguous Lean mutation')
    target=out/'lean-mutants'/mutation['id'];target.mkdir(parents=True)
    path=target/(mutation['module']+'.lean');path.write_text(source.replace(mutation['old'],mutation['new']))
    result=run([config['lean'],'--root='+str(target),str(path)],expected=None,extra_env=lean_env)
    require('error:' in result.stdout,'Lean mutant lacks proof failure')
    lean_mutants[mutation['id']]=result.returncode
require(authenticate()==initial_manifest, 'capsule changed during replay')
summary={'complete':True,'audits':len(names),'compiled_modules':len(compile_commands),'cases':len(json.loads((ROOT/'native/CASES.json').read_text())),'snapshots':len(model.splitlines()),'model_sha256':hashlib.sha256(model.encode()).hexdigest(),'native_mutants':mutants,'lean_mutants':lean_mutants}
(out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
