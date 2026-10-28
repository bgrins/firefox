import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def git(path, *args):
    return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=path,env=ENV)


def paths():
    return sorted(n.decode() for n in git(ROOT,'ls-files','--others','--exclude-standard','-z').split(b'\0') if n)


snapshot = read(HERE/'inventory.json')
assert git(ROOT,'rev-parse','HEAD').decode().strip() == snapshot['head']
assert paths() == snapshot['paths']
for record in snapshot['project_files']:
    path = ROOT/record['path']
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode)
    assert [info.st_dev,info.st_ino] == record['identity']
    assert info.st_size == record['bytes'] and stat.S_IMODE(info.st_mode) == record['mode']
    assert sha(path) == record['sha256']
recovery = ROOT/'artifacts/css-worktree-recovery-20261028-v1'
pins = read(recovery/'SOURCE-PINS.json')
assert sorted(pins) == sorted(snapshot['source_recovery_bodies_verified'])
for name,record in pins.items():
    assert sha(ROOT/name) == record['sha256']
    assert (ROOT/name).read_bytes() == (recovery/'working'/name).read_bytes()
assert git(ROOT/'artifacts/css-spec-lean','status','--porcelain=v1','-z').decode() == snapshot['nested_status']
assert paths() == snapshot['paths']
print(json.dumps({'root_untracked':len(snapshot['paths']),
                  'project_bodies_and_identities_verified':len(snapshot['project_files']),
                  'unrelated_contents_read':False,'recovery_bodies_verified':len(pins),
                  'stable_on_repeat':True,'writes_performed':False},indent=2))
