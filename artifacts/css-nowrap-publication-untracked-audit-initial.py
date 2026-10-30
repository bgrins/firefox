import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT=Path(__file__).resolve().parent.parent
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args,cwd=ROOT):
    return subprocess.check_output(GIT+list(args),cwd=cwd,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
sha=lambda b:hashlib.sha256(b).hexdigest()
adopted='testing/web-platform/tests/css/css-text/white-space/nowrap-inline-break-policies.html'
pins=json.loads((ROOT/'artifacts/css-worktree-recovery-20261028-v1/SOURCE-PINS.json').read_bytes())
project={p:r for p,r in pins.items() if not r['tracked'] and p!=adopted}
assert len(project)==67
unrelated=json.loads((ROOT/'artifacts/css-untracked-audit-shadow-pair-20261029-v1/UNRELATED-METADATA.json').read_bytes())
assert len(unrelated)==495
expected=set(project)|{r['path'] for r in unrelated}
actual=set(git('ls-files','--others','--exclude-standard','-z').decode().rstrip('\0').split('\0'))
assert actual==expected and len(actual)==562
for path,record in project.items():
    body=(ROOT/path).read_bytes()
    assert sha(body)==record['sha256']
    archive=git('show','0197d1c8e8fd678680d78b212f6a2c0ae9d82d51:artifacts/css-worktree-recovery-20261028-v1/working/'+path)
    assert body==archive
for record in unrelated:
    path=ROOT/record['path'];s=path.lstat()
    kind='symlink' if stat.S_ISLNK(s.st_mode) else 'file' if stat.S_ISREG(s.st_mode) else 'unexpected'
    assert kind==record['kind']
    assert s.st_size==record['bytes'] and stat.S_IMODE(s.st_mode)==record['mode']
    assert [s.st_dev,s.st_ino]==record['identity']
assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
assert git('ls-files','--',adopted).decode().strip()==adopted
nested=git('status','--short','--untracked-files=all',cwd=ROOT/'artifacts/css-spec-lean').decode().splitlines()
assert nested==['?? .DS_Store']
result={'head':git('rev-parse','HEAD').decode().strip(),'untracked_count':562,'project_files_matching_committed_recovery':67,'untracked_project_wpt_count':52,'unrelated_metadata_matches':495,'unrelated_contents_read':False,'exact_inventory':True,'adopted_wpt_tracked':adopted,'tracked_modified':[],'staged':[],'nested_status':nested,'script_sha256':sha(Path(__file__).read_bytes())}
out=ROOT/'artifacts/css-nowrap-publication-untracked-audit-v1.json'
with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
