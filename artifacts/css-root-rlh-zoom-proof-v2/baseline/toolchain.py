import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
BASE=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def identify(lean):
    lean=Path(lean).resolve();prefix=lean.parent.parent
    pins={'bin/lean':sha(lean)}
    for p in sorted((prefix/'lib').rglob('*')):
        if p.is_file() and ('.olean' in p.name or p.suffix in ('.ir','.so','.dylib')):
            pins[str(p.relative_to(prefix))]=sha(p)
    tools={}
    for command in ['clang++','rustc']:
        path=Path(shutil.which(command)).resolve()
        args=['--version','--verbose'] if command=='rustc' else ['--version']
        proc=subprocess.run([command]+args,capture_output=True,text=True,check=True)
        tools[command]={'version':proc.stdout,'executable_sha256':sha(path)}
    version=subprocess.run([str(lean),'--version'],capture_output=True,text=True,check=True).stdout
    return {'leanVersion':version,'leanInputs':pins,'compilers':tools,'python':list(sys.version_info[:3]),'machine':os.uname().machine}
def verify(lean):
    expected=json.loads((BASE/'TOOLCHAIN.json').read_text())
    lean=Path(lean).resolve();prefix=lean.parent.parent
    for relative,digest in expected['leanInputs'].items():
        assert sha(prefix/relative)==digest,('Lean dependency changed',relative)
    for command,record in expected['compilers'].items():
        assert sha(Path(shutil.which(command)).resolve())==record['executable_sha256'],command
    assert list(sys.version_info[:3])==expected['python'] and os.uname().machine==expected['machine']
    for command,record in expected['compilers'].items():
        args=['--version','--verbose'] if command=='rustc' else ['--version']
        actual=subprocess.run([command]+args,capture_output=True,text=True,check=True).stdout
        assert actual==record['version'],command
    actual=subprocess.run([str(lean),'--version'],capture_output=True,text=True,check=True).stdout
    assert actual==expected['leanVersion'],'Lean version'
    return {'leanInputs':len(expected['leanInputs']),'leanVersion':actual,'compilers':expected['compilers'],'python':expected['python'],'machine':expected['machine']}
