import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
executable = shutil.which('git')
assert executable
allowed_env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
allowed_env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
                   GIT_AUTHOR_NAME='Disposable Probe', GIT_AUTHOR_EMAIL='probe@invalid',
                   GIT_COMMITTER_NAME='Disposable Probe', GIT_COMMITTER_EMAIL='probe@invalid',
                   GIT_AUTHOR_DATE='1700000000 +0000', GIT_COMMITTER_DATE='1700000000 +0000')
records = []
with tempfile.TemporaryDirectory(prefix='fix121-ref-probe-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    def git(*args, data=None, ok=True):
        r = subprocess.run([executable, '-c', 'commit.gpgsign=false', '-c', 'gc.auto=0',
                            '-c', 'core.hooksPath=/dev/null', *args], cwd=scratch,
                           env=allowed_env, input=data, capture_output=True)
        if ok:
            assert r.returncode == 0, r.stderr.decode()
        return r
    version = git('--version').stdout.decode().strip()
    git('init', '-b', 'expected')
    tree = git('mktree', data=b'').stdout.decode().strip()
    old = git('commit-tree', tree, data=b'old\n').stdout.decode().strip()
    new = git('commit-tree', tree, '-p', old, data=b'new\n').stdout.decode().strip()
    branch = 'refs/heads/expected'
    backup = 'refs/heads/backup'
    git('update-ref', branch, old)
    git('update-ref', backup, old)
    cases = {
        'v2-symref-verify': ['option no-deref', 'symref-verify HEAD ' + branch,
            'verify ' + backup + ' ' + old, 'update ' + branch + ' ' + new + ' ' + old],
        'no-deref-branch-update': ['option no-deref', 'symref-verify HEAD ' + branch,
            'verify ' + backup + ' ' + old, 'option no-deref', 'update ' + branch + ' ' + new + ' ' + old],
        'symref-self-update': ['option no-deref', 'symref-update HEAD ' + branch + ' ref ' + branch,
            'verify ' + backup + ' ' + old, 'update ' + branch + ' ' + new + ' ' + old],
        'backup-and-branch-cas': ['verify ' + backup + ' ' + old, 'update ' + branch + ' ' + new + ' ' + old],
    }
    for name, commands in cases.items():
        git('update-ref', branch, old)
        transaction = '\n'.join(['start', *commands, 'prepare', 'commit']) + '\n'
        result = git('update-ref', '--stdin', data=transaction.encode(), ok=False)
        records.append(dict(name=name, transaction=transaction, exit=result.returncode,
                            stdout=result.stdout.decode(), stderr=result.stderr.decode(),
                            head=git('rev-parse', 'HEAD').stdout.decode().strip(),
                            branch=git('symbolic-ref', 'HEAD').stdout.decode().strip(),
                            backup=git('rev-parse', backup).stdout.decode().strip()))
    assert records[0]['exit'] == 128 and records[0]['head'] == old
    assert records[-1]['exit'] == 0 and records[-1]['head'] == new
assert not scratch.exists()
check = dict(status='DISPOSABLE_GIT_TRANSACTION_OBSERVED', executable=executable,
             executable_sha256=hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
             version=version, old=old, new=new, records=records,
             owned_scratch_removed=True, live_repository_accessed=False,
             signatures_created=False, files_index_used=False)
(HERE / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
print(json.dumps(check, indent=2))
