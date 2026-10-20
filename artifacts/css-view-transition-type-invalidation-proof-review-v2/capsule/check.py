import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without -O/-OO')
sys.dont_write_bytecode = True
from pathlib import Path, PurePosixPath
import argparse, hashlib, importlib.util, json, os, re, stat, subprocess
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
config=read_json(ROOT/'TOOLCHAIN.json')
for name in ['lean','clang']:require(sha(Path(config[name]))==config[name+'_sha256'],'toolchain pin: '+name)
for row in read_json(ROOT/'EXTERNAL-IDENTITY.json'):
    require(sha(ROOT/row['retained_path'])==row['sha256'],'retained external input identity')
identity=read_json(ROOT/'DISCOVERY-IDENTITY.json')
for name,digest in identity.items():require(sha(ROOT/'evidence'/('discovery-'+name))==digest,'discovery receipt identity')
discovery={row['path']:row['sha256'] for row in read_json(ROOT/'evidence/discovery-FILES.json')}
for path in (ROOT/'source').glob('original-*'):
    require(sha(path)==discovery['source/'+path.name.removeprefix('original-')],'original source identity')
require(sha(ROOT/'evidence/types-proof-FILES.json')=='4291d462917594ca9b463e47f17c9c4ee74ec5b8dd4a0f7e823e91f6618213d5','preceding proof identity')
previous={row['path']:row['sha256'] for row in read_json(ROOT/'evidence/types-proof-FILES.json')}
require(sha(ROOT/'source/generated-ViewTransitionBinding.cpp')==previous['source/objdir-full.noindex__dom__bindings__ViewTransitionBinding.cpp'],'generated helper provenance')
final=read_json(ROOT/'evidence/root-FINAL-SOURCE-v2.json')['pins']
for path,digest in final.items():
    retained=ROOT/'source'/('candidate-'+path.replace('/','__')) if path.startswith('dom/') else ROOT/'evidence/root-wpt-v2.html'
    require(sha(retained)==digest,'final source / WPT identity')
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
module('case_schema','calibration.py').validate_cases(read_json(ROOT/'native/CASES.json'))
extract=module('extract','source_extract.py')
require(extract.bindings()==read_json(ROOT/'SOURCE-BINDINGS.json'),'complete source body binding')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
require(out!=ROOT and ROOT not in out.parents,'external output required');out.mkdir(parents=True,exist_ok=False)
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};commands=[]
def run(command,expected=0,extra_env=None):
    result=subprocess.run(command,cwd=out,env=extra_env or env,text=True,capture_output=True)
    commands.append(dict(command=command,exit=result.returncode,stdout=result.stdout,stderr=result.stderr));(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(result.returncode==expected,'command result: '+str(command));return result
run([sys.executable,'-I','-S',str(ROOT/'native/build.py'),'--output',str(out/'native')])
run([sys.executable,'-I','-S',str(ROOT/'compile.py'),'--output',str(out/'lean'),'Audit','CalibrationDriver'])
compiles=read_json(out/'lean/COMMANDS.json');audit=next(row['stdout'] for row in compiles if row['command'][-1].endswith('/Audit.lean'));(out/'AUDIT.txt').write_text(audit)
names=read_json(ROOT/'AUDIT-NAMES.json');found=re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",audit)
require([row[0] for row in found]==names,'theorem audit roster')
for _,_,axioms in found:require(set(axioms.split(', '))<={'','propext','Classical.choice','Quot.sound'},'unapproved axiom')
lean_env={**env,'LEAN_PATH':str(out/'lean')}
model=run([config['lean'],'--root='+str(ROOT/'lean'),'--run',str(ROOT/'lean/CalibrationDriver.lean'),str(out/'native/INPUT.txt')],extra_env=lean_env)
require(not model.stderr,'model diagnostics');(out/'CALIBRATION.txt').write_text(model.stdout)
calibration=module('calibration','calibration.py').validate(ROOT,out/'native',model.stdout)
(out/'CALIBRATION-RESULT.json').write_text(json.dumps(calibration,indent=2)+'\n')
mutants={}
for mutation in read_json(ROOT/'LEAN-MUTATIONS.json'):
    source=(ROOT/'lean'/(mutation['module']+'.lean')).read_text();require(source.count(mutation['old'])==1,'mutation uniqueness')
    target=out/'mutants'/mutation['name'];target.mkdir(parents=True);path=target/(mutation['module']+'.lean');path.write_text(source.replace(mutation['old'],mutation['new']))
    result=run([config['lean'],'--root='+str(target),str(path)],expected=1,extra_env=lean_env)
    require('error:' in result.stdout and any(marker in result.stdout for marker in ['unsolved goals','Tactic','Type mismatch','tactic failed']),'semantic proof failure')
    mutants[mutation['name']]=result.returncode
require(authenticate()==initial_manifest,'source capsule changed')
summary=dict(complete=True,audits=len(names),compiled_modules=len(compiles),source_bindings=len(read_json(ROOT/'SOURCE-BINDINGS.json')),calibration=calibration,lean_mutants=mutants,scope='type mutation notification and cached-observer coherence under explicit resolver/traversal/lifecycle providers')
(out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
