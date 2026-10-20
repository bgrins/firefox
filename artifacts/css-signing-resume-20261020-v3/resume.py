import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HELPER = ROOT / 'artifacts/css-ahom-lf-partition-probe-v1/commit-item-v2.py'
GIT = ['git', '-c', 'core.fsmonitor=false']
os.environ['GIT_OPTIONAL_LOCKS'] = '0'

def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def snapshot():
    return {
        'head': git('rev-parse', 'HEAD').decode().strip(),
        'index_diff_sha256': sha(git('diff', '--cached', '--binary')),
        'index_entries_sha256': sha(git('ls-files', '--stage', '-z')),
        'staged': git('diff', '--cached', '--name-only').decode().splitlines(),
    }

recipes = [
    'artifacts/css-cssom-exact-traversal-commit-v3/lifecycle-results.json',
    'artifacts/css-cssom-exact-traversal-commit-v3/runtime-results.json',
    'artifacts/css-cssom-exact-traversal-commit-v4/research-source-draft.json',
    'artifacts/css-cssom-exact-traversal-commit-v4/research-runtime-draft.json',
    'artifacts/css-primary-destruction-ownership-refinement-commit-v1/draft.json',
    'artifacts/css-cssom-exact-traversal-commit-v4/standalone-evidence-draft.json',
    'artifacts/css-cssom-exact-traversal-commit-v4/native-accepted.json',
]
before = snapshot()
save('BEFORE.json', before)
expected = json.loads((ROOT / 'artifacts/css-cssom-exact-traversal-commit-v4/SIGNING-RESUME-PREFLIGHT.json').read_text())
assert all(before[k] == expected[k] for k in ['head', 'index_diff_sha256', 'index_entries_sha256'])
assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
items = [json.loads((ROOT / name).read_text()) for name in recipes]
assert sorted(before['staged']) == sorted(items[0]['files'])
assert len(before['staged']) == 229
for item in items[:6]:
    assert set(item['files']) == set(item['source_pins'])
    assert all(n.startswith('artifacts/') for n in item['files'])
    for name, pin in item['source_pins'].items():
        assert sha((ROOT / name).read_bytes()) == pin, name
for name, pin in items[0]['source_pins'].items():
    assert sha(git('show', ':' + name)) == pin, name
dependency = items[5]['dependencies']['commit_helper']
assert sha(HELPER.read_bytes()) == dependency['sha256']
native = items[-1]
assert sha((ROOT / native['patch']).read_bytes()) == native['patch_sha256']
assert sha((ROOT / native['acceptance']['path']).read_bytes()) == native['acceptance']['sha256']
assert not git('diff', '--name-only', '--', *native['files']).strip()
subprocess.run(GIT + ['apply', '--check', native['patch']], cwd=ROOT, check=True)
native_original = {n: sha((ROOT / n).read_bytes()) if (ROOT / n).exists() else None for n in native['files']}
dirty_names = git('diff', '--name-only', '--', 'layout', 'dom', 'servo').decode().splitlines()
dirty_pins = {n: sha((ROOT / n).read_bytes()) for n in dirty_names}
save('PREFLIGHT.json', {'native_original': native_original, 'dirty_native_pins': dirty_pins, 'recipes': recipes})
previous = before['head']
records = []
try:
    for number, (name, draft) in enumerate(zip(recipes, items), 1):
        assert git('rev-parse', 'HEAD').decode().strip() == previous
        item = dict(draft, expected_head=previous, base_recipe_id=draft['id'], id=draft['id'] + '-resume-20261020-v3')
        finalized = HERE / (str(number) + '-recipe.json')
        assert not finalized.exists()
        save(finalized.name, item)
        print('Signing ' + str(number) + '/7: ' + item['message'], flush=True)
        with (HERE / (str(number) + '-signing.log')).open('w') as output:
            result = subprocess.run([sys.executable, '-I', '-S', '-B', str(HELPER), str(finalized)], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        for suffix in ['message.txt', 'commit.log', 'receipt.json']:
            source = HELPER.parent / (item['id'] + '-' + suffix)
            if source.exists():
                shutil.copyfile(source, HERE / (str(number) + '-' + suffix))
        records.append({'number': number, 'recipe': name, 'exit': result.returncode, 'state': snapshot()})
        save('SIGNING.json', records)
        if result.returncode:
            print('Signing stopped; see ' + str(HERE / (str(number) + '-commit.log')), flush=True)
            raise SystemExit(result.returncode)
        after = git('rev-parse', 'HEAD').decode().strip()
        assert git('rev-parse', after + '^').decode().strip() == previous
        assert b'\ngpgsig ' in git('cat-file', 'commit', after)
        assert sorted(git('diff-tree', '--no-commit-id', '--name-only', '-r', after).decode().splitlines()) == sorted(item['files'])
        for path, pin in item.get('source_pins', {}).items():
            assert sha(git('show', after + ':' + path)) == pin, path
        assert not git('diff', '--cached', '--name-only').strip()
        previous = after
        print('Committed ' + after, flush=True)
    assert all(sha((ROOT / n).read_bytes()) == pin for n, pin in dirty_pins.items())
    assert all((sha((ROOT / n).read_bytes()) if (ROOT / n).exists() else None) == pin for n, pin in native_original.items())
    subprocess.run(GIT + ['apply', '--check', native['patch']], cwd=ROOT, check=True)
    subprocess.run(GIT + ['apply', native['patch']], cwd=ROOT, check=True)
    assert not git('diff', '--name-only', '--', *native['files']).strip()
    assert all(sha((ROOT / n).read_bytes()) == pin for n, pin in dirty_pins.items())
    save('COMPLETE.json', {'status': 'SEVEN_SIGNED_COMMITS_NATIVE_PATCH_INSTALLED', 'head': previous, 'preserved_dirty_native_files': len(dirty_pins), 'records': records})
    print('Seven signed commits complete; accepted patch installed; other native edits preserved.', flush=True)
finally:
    save('AFTER.json', snapshot())
