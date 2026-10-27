import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v4'
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def git(*args, env=ENV):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


assert not HERE.exists()
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert not git('diff', '--cached', '--name-only')
HERE.mkdir()
base = git('rev-parse', 'HEAD').decode().strip()
index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
before_index = sha(index)
old = json.loads((ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v3/SOURCE-PINS.json').read_text())
paths = sorted(old)
assert len(paths) == 131
pins = {name: sha(ROOT / name) for name in paths}
with tempfile.TemporaryDirectory(prefix='css-recovery-index-', dir='/private/tmp') as temp:
    env = dict(ENV, GIT_INDEX_FILE=str(Path(temp) / 'index'))
    git('read-tree', base, env=env)
    git('add', '-f', '--', *paths, env=env)
    assert sorted(git('diff', '--cached', '--name-only', base, env=env).decode().splitlines()) == paths
    tree = git('write-tree', env=env).decode().strip()
    patch = HERE / 'unfinished.patch'
    patch.write_bytes(git('diff', '--cached', '--binary', '--full-index', base, env=env))
    git('read-tree', base, env=env)
    git('apply', '--cached', '--check', str(patch), env=env)
    git('apply', '--cached', str(patch), env=env)
    assert git('write-tree', env=env).decode().strip() == tree
    for name, pin in pins.items():
        assert hashlib.sha256(git('show', ':' + name, env=env)).hexdigest() == pin
    git('apply', '--cached', '--reverse', str(patch), env=env)
    assert git('write-tree', env=env) == git('rev-parse', base + '^{tree}')
assert sha(index) == before_index
assert {name: sha(ROOT / name) for name in paths} == pins
save('BASE.json', dict(commit=base, tree=git('rev-parse', base + '^{tree}').decode().strip()))
save('SOURCE-PINS.json', pins)
save('CHECK.json', dict(files=131, exact_postimages=True, reverse_restores_base_tree=True, live_index_unchanged=True, changed_since_previous=[name for name in paths if pins[name] != old[name]]))
(HERE / 'README.md').write_text('# Unfinished work checkpoint\n\nThis recovery patch preserves all 131 previously inventoried unfinished project files, including the updated current-provider resolver and its two additional host tests. Apply `unfinished.patch` to the commit in `BASE.json`; exact application and reversal were checked in an isolated index. The live working files are retained.\n\nThis is a recovery snapshot, not an accepted production fix. The provider prototype passes 19 host tests but still needs normal cascade integration. The quote candidate awaits a fresh candidate/original/candidate browser comparison. The separately signed Lean library is excluded, as are unrelated directories and build outputs. The accepted bug count remains 133.\n')
save('FILES.json', {str(p.relative_to(HERE)): sha(p) for p in HERE.iterdir() if p.is_file()})
print('Verified recovery snapshot for 131 unfinished files.', flush=True)
