import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('Use python3 -I -S without optimization')
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ['git', '-c', 'core.fsmonitor=false']
ITEMS = {
    '83': ('css-attr-leading-whitespace-root-v1', 'stylo-css-attr-leading-whitespace-fix'),
    '84': ('css-variable-trailing-token-root-v1', 'stylo-css-variable-trailing-token-fix'),
    '85': ('css-variable-escaped-whitespace-root-v1', 'stylo-css-variable-escaped-whitespace-fix'),
}

def require(value, message):
    if not value:
        raise RuntimeError(message)

def git(*args, env=None, data=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env, input=data)

def read_commit(head, name):
    return json.loads(git('show', head + ':' + name))

require(len(sys.argv) == 2 and sys.argv[1] in ITEMS, 'Expected fix number 83, 84 or 85')
number = sys.argv[1]
folder, branch = ITEMS[number]
ref = 'refs/heads/' + branch
head = git('rev-parse', 'HEAD').decode().strip()
require(not git('diff', '--cached', '--name-only').strip(), 'Index must be empty')
require(git('config', '--get', 'commit.gpgsign').decode().strip() == 'true', 'Signing must remain enabled')
require(subprocess.run(GIT + ['show-ref', '--verify', '--quiet', ref], cwd=ROOT).returncode == 1, 'Ref already exists')
plan = read_commit(head, 'artifacts/' + folder + '/COMMIT-PLAN.json')
pack = read_commit(head, 'artifacts/' + folder + '/PACKAGING.json')['standalone']
patch = git('show', head + ':' + pack['patch'])
require(hashlib.sha256(patch).hexdigest() == pack['sha256'], 'Patch pin mismatch')
roots = list(plan['roots'])
if number == '85':
    shared = read_commit(head, 'artifacts/css-variable-trailing-token-root-v1/COMMIT-PLAN.json')
    roots += [p for p in shared['roots'] if '/css-variable-terminal-span-' in p]
roots += ['artifacts/css-variable-whitespace-standalone-review-v1', 'artifacts/css-variable-whitespace-standalone-root-v1']
entries = git('ls-tree', '-r', head, '--', *roots).decode().splitlines()
require(bool(entries), 'Missing evidence entries')
paths = [line.split('\t', 1)[1] for line in entries]
require(all(p.startswith('artifacts/') for p in paths), 'Evidence contains native paths')
require(any(p.endswith('css-variable-whitespace-standalone-review-v1/REPORT.md') for p in paths), 'Independent review missing')
worktree_pins = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in pack['paths']}
with tempfile.TemporaryDirectory(prefix='css-whitespace-standalone-', dir='/private/tmp') as tmp:
    env = {**os.environ, 'GIT_INDEX_FILE': str(Path(tmp) / 'index')}
    git('read-tree', pack['base'], env=env)
    git('update-index', '--index-info', env=env, data=''.join(line.replace(' blob ', ' ', 1) + '\n' for line in entries).encode())
    evidence_tree = git('write-tree', env=env).decode().strip()
    evidence_delta = git('diff', '--cached', '--name-only', pack['base'], env=env).decode().splitlines()
    require(sorted(evidence_delta) == sorted(paths), 'Unexpected evidence delta')
    git('apply', '--cached', '--check', '-', env=env, data=patch)
    git('apply', '--cached', '-', env=env, data=patch)
    native_tree = git('write-tree', env=env).decode().strip()
    require(sorted(git('diff-tree', '--no-commit-id', '--name-only', '-r', evidence_tree, native_tree).decode().splitlines()) == sorted(pack['paths']), 'Native path roster mismatch')
    native_pins = {p: hashlib.sha256(git('show', ':' + p, env=env)).hexdigest() for p in pack['paths']}
    require(native_pins['servo/components/style/custom_properties.rs'] == pack['source_sha256'], 'Native source differs from accepted standalone source')
    for p in pack['paths']:
        if p.startswith('testing/'):
            require(native_pins[p] == hashlib.sha256(git('show', head + ':' + p)).hexdigest(), 'WPT differs from accepted committed test')
    git('apply', '--cached', '--reverse', '-', env=env, data=patch)
    require(git('write-tree', env=env).decode().strip() == evidence_tree, 'Reverse application differs')
    companion = git('commit-tree', '-S', evidence_tree, '-p', pack['base'], env=env,
        data=('No bug - Record standalone custom property whitespace fix ' + number + ' evidence\n').encode()).decode().strip()
    native = git('commit-tree', '-S', native_tree, '-p', companion, env=env,
        data=(plan['native_message'].rstrip() + '\n').encode()).decode().strip()
    for commit in [companion, native]:
        require(b'gpgsig ' in git('cat-file', 'commit', commit), 'Missing signature')
    git('update-ref', ref, native, '0' * 40)
require(git('rev-parse', 'HEAD').decode().strip() == head, 'HEAD moved')
require(not git('diff', '--cached', '--name-only').strip(), 'Index changed')
require(worktree_pins == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in pack['paths']}, 'Worktree changed')
record = {'fix': number, 'base': pack['base'], 'ref': ref, 'companion_commit': companion,
    'native_commit': native, 'source_head': head, 'evidence_files': len(paths), 'native_paths': pack['paths'],
    'native_pins': native_pins, 'patch_sha256': pack['sha256'], 'signatures_present': True,
    'exact_apply_reverse': True, 'head_index_worktree_preserved': True, 'isolated_upstream_build_browser': 'NOT_RUN'}
(HERE / ('STANDALONE-' + number + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
