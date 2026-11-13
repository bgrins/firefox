import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
PREVIOUS = [ROOT / ('artifacts/' + name + '/standalone.patch') for name in [
    'css-flex-signed-wrap-repair-20261111-v1',
    'css-flex-accumulated-mbp-repair-20261111-v1',
    'css-flex-total-violation-repair-20261111-v1']]
changed = sorted(json.loads((HERE / 'BUILD-SOURCE.json').read_text()))
paths = set(changed)
for patch in PREVIOUS:
    paths.update(line[6:] for line in patch.read_text().splitlines() if line.startswith('+++ b/'))
head = subprocess.check_output(GIT + ['rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == '5fcf976eeb79ddc057e9c73d7b73a422058b1903'
baseline = {}
for name in sorted(paths):
    result = subprocess.run(GIT + ['show', head + ':' + name], cwd=ROOT, capture_output=True)
    if result.returncode == 0:
        baseline[name] = result.stdout
    else:
        assert result.returncode == 128 and (
            b'does not exist in' in result.stderr or b'exists on disk, but not in' in result.stderr)
current = {name: (ROOT / name).read_bytes() for name in paths if (ROOT / name).exists()}
for name, expected in json.loads((HERE / 'BUILD-SOURCE.json').read_text()).items():
    assert hashlib.sha256(current[name]).hexdigest() == expected, name
commands = []


def populate(work, files):
    work.mkdir()
    for name, data in files.items():
        path = work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def snapshot(work):
    return {str(p.relative_to(work)): p.read_bytes() for p in work.rglob('*') if p.is_file()}


def apply(work, patch, reverse=False):
    for check in [True, False]:
        argv = GIT + ['apply'] + (['--reverse'] if reverse else []) + (['--check'] if check else []) + [str(patch)]
        result = subprocess.run(argv, cwd=work, capture_output=True)
        commands.append({'argv': argv, 'cwd': str(work), 'exit': result.returncode,
                         'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
        (HERE / 'PATCH-COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
        assert result.returncode == 0, commands[-1]


def export(name, before, after):
    chunks = []
    for path in changed:
        a, b = before.get(path, b''), after.get(path, b'')
        if a == b:
            continue
        chunks.append('diff --git a/' + path + ' b/' + path + '\n')
        if path not in before:
            chunks.append('new file mode 100644\n')
        chunks.extend(difflib.unified_diff(a.decode().splitlines(True), b.decode().splitlines(True),
                      fromfile='a/' + path if path in before else '/dev/null', tofile='b/' + path))
    with (HERE / name).open('x') as out:
        out.write(''.join(chunks))


with tempfile.TemporaryDirectory(prefix='css-flex-wide-patches-', dir='/private/tmp') as temporary:
    parent = Path(temporary)
    isolated = parent / 'isolated'
    populate(isolated, current)
    for patch in reversed(PREVIOUS[:2]):
        apply(isolated, patch, True)
    final = snapshot(isolated)
    predecessor = parent / 'predecessor'
    populate(predecessor, baseline)
    apply(predecessor, PREVIOUS[2])
    export('standalone.patch', baseline, final)
    export('after-total-violation.patch', snapshot(predecessor), final)

    single = parent / 'standalone'
    populate(single, baseline)
    apply(single, HERE / 'standalone.patch')
    assert all((single / name).read_bytes() == final[name] for name in changed)
    apply(single, HERE / 'standalone.patch', True)
    assert snapshot(single) == baseline

    stack = parent / 'stack'
    populate(stack, baseline)
    for patch in PREVIOUS:
        apply(stack, patch)
    apply(stack, HERE / 'after-total-violation.patch')
    assert snapshot(stack) == current
    apply(stack, HERE / 'after-total-violation.patch', True)
    for patch in reversed(PREVIOUS):
        apply(stack, patch, True)
    assert snapshot(stack) == baseline

result = {'head': head, 'paths': changed, 'commands': len(commands),
          'standalone_applies_and_reverses': True, 'ordered_stack_matches_current': True,
          'scratch_removed': not Path(temporary).exists(),
          'patches': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                      for name in ['standalone.patch', 'after-total-violation.patch']},
          'scope': 'Patch transport and byte comparison only; runtime validation is of the combined local branch.',
          'overlap': 'Standalone includes necessary total-violation widening; use the incremental patch after the earlier total-violation fix. No arbitrary-order claim.'}
(HERE / 'PATCH-RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
