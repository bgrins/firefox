import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
def git(*args, env=ENV):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def index_state():
    return {'head': git('rev-parse', 'HEAD').decode().strip(),
            'entries': sha(git('ls-files', '--stage', '-z')),
            'flags': sha(git('ls-files', '-v', '-z')),
            'cached': sha(git('diff', '--cached', '--binary'))}
def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert git('symbolic-ref', 'HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
assert not git('diff', '--cached', '--name-only')
item = json.loads(Path(sys.argv[1]).read_text())
state = index_state()
parent = state['head']
if len(sys.argv) == 3:
    prior = json.loads(Path(sys.argv[2]).read_text())
    assert prior['branch_before'] == state
    parent = prior['commit']
assert all(n.startswith('artifacts/') and '..' not in Path(n).parts for n in item['files'])
assert set(item['files']) == set(item['source_pins'])
for name, digest in item['source_pins'].items():
    assert sha((ROOT / name).read_bytes()) == digest, name
with tempfile.TemporaryDirectory(prefix='css-presign-index-', dir='/private/tmp') as tmp:
    env = dict(ENV, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
    git('read-tree', parent, env=env)
    names = Path(tmp) / 'paths'
    names.write_bytes(b''.join(n.encode() + b'\0' for n in item['files']))
    git('add', '-f', '--pathspec-from-file=' + str(names), '--pathspec-file-nul', env=env)
    assert sorted(git('diff', '--cached', '--name-only', parent, env=env).decode().splitlines()) == sorted(item['files'])
    for name, digest in item['source_pins'].items():
        assert sha(git('show', ':' + name, env=env)) == digest, name
    tree = git('write-tree', env=env).decode().strip()
    message = HERE / (item['id'] + '-message.txt')
    message.write_text(item['message'].rstrip() + '\n')
    signed = subprocess.run(GIT + ['commit-tree', '-S', tree, '-p', parent, '-F', str(message)],
                            cwd=ROOT, env=env, capture_output=True, text=True)
    (HERE / (item['id'] + '-signing.log')).write_text(signed.stderr)
    assert signed.returncode == 0, 'Signing failed; branch and index untouched'
    commit = signed.stdout.strip()
assert git('rev-parse', commit + '^').decode().strip() == parent
assert git('rev-parse', commit + '^{tree}').decode().strip() == tree
with (HERE / (item['id'] + '-signature.log')).open('w') as stream:
    subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
assert index_state() == state
for name, digest in item['source_pins'].items():
    assert sha((ROOT / name).read_bytes()) == digest, name
save(HERE / (item['id'] + '-presigned.json'), {'commit': commit, 'parent': parent, 'tree': tree,
     'branch_before': state, 'files': item['files'], 'source_pins': item['source_pins'],
     'signature_verified': True, 'published': False, 'branch_and_index_unchanged': True})
print('Signed and verified; branch publication pending:', item['id'], commit, flush=True)
