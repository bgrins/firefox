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
config=read_json(ROOT/'TOOLCHAIN.json')
for tool in ['lean','rustc']:
    require(sha(Path(config[tool]))==config[tool+'_sha256'], 'toolchain mismatch: '+tool)
for row in read_json(ROOT/'IMPORTS.json'):
    require(sha(ROOT/'lean'/(row['module']+'.lean'))==row['sha256'], 'import mismatch')
for row in read_json(ROOT/'SOURCE-PINS.json'):
    require(sha(ROOT/row['retained'])==row['sha256'], 'source mismatch')
for row in read_json(ROOT/'PREDECESSOR-TRANSFER.json')['source_vendor']:
    require(sha(ROOT/row['path'])==row['sha256'], 'predecessor transfer mismatch')
for path,digest in read_json(ROOT/'ROOT-OWNED-PINS.json').items():
    require(sha(ROOT/path)==digest, 'root-owned source changed')
for path in (ROOT/'lean').glob('*.lean'):
    require(not re.search(r'\b(sorry|admit|axiom)\b', '\n'.join(line for line in path.read_text().splitlines() if not line.lstrip().startswith('--'))), 'unsupported proof declaration')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
require(out!=ROOT and ROOT not in out.parents, 'output must be external')
out.mkdir(parents=True,exist_ok=False)
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))}
commands=[]
def run(command):
    r=subprocess.run(command,cwd=out,env=env,text=True,capture_output=True)
    commands.append(dict(command=command,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(r.returncode==0, 'command failed: '+r.stdout+r.stderr)
    return r
run([sys.executable,'-I','-S',str(ROOT/'compile.py'),'--output',str(out/'proof'),'AllAudit'])
compiled=read_json(out/'proof/COMMANDS.json')
audit=''.join(r['stdout'] for r in compiled if Path(r['command'][-1]).name in {'AfterAudit.lean','AllAudit.lean'})
(out/'AUDIT.txt').write_text(audit)
audit_rows=re.findall(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",audit)
require([row[0] for row in audit_rows]==read_json(ROOT/'ALL-AUDIT-NAMES.json'), 'audit roster mismatch')
for _,_,axioms in audit_rows:
    require(set(axioms.split(', '))<={'','propext','Classical.choice','Quot.sound'}, 'unapproved axiom')
require(all(not row['stderr'] for row in compiled), 'Lean diagnostics')
run([sys.executable,'-I','-S',str(ROOT/'native/check.py'),'--output',str(out/'calibration')])
calibration=read_json(out/'calibration/RESULT.json')
require(calibration['cases']==27 and calibration['snapshots']==138 and calibration['source_bindings']==10, 'calibration roster')
require(calibration['native_mutants']=={'outer-ownership':25,'missing-advance':41,'omitted-curly-cleanup':22,'ignored-stop-guard':7,'cache-overwrite':11,'erased-curly-writes':5}, 'semantic mutation roster')
require(authenticate()==initial_manifest, 'capsule changed during replay')
result=dict(status='PASS',general_audits=22,kernel_challenges=11,audit_count=len(audit_rows),proof_modules=len(compiled),calibration=calibration,scope='Conditional until-after model refinement and finite complete-source native calibration; not universal tokenizer/callback/native refinement')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
