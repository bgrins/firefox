import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATCHES = [
    ROOT / 'artifacts/css-flex-signed-wrap-repair-20261111-v1/standalone.patch',
    ROOT / 'artifacts/css-flex-accumulated-mbp-repair-20261111-v1/standalone.patch',
    ROOT / 'artifacts/css-flex-total-violation-repair-20261111-v1/standalone.patch',
    HERE / 'standalone.patch',
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


git = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
head = subprocess.check_output(git + ['rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
paths = set()
for patch in PATCHES:
    for line in patch.read_text().splitlines():
        if line.startswith('+++ b/'):
            paths.add(line[6:])
baseline = {}
for name in sorted(paths):
    result = subprocess.run(git + ['show', head + ':' + name], cwd=ROOT, capture_output=True)
    if result.returncode == 0:
        baseline[name] = result.stdout
    else:
        assert result.returncode == 128 and (
            b'does not exist in' in result.stderr or b'exists on disk, but not in' in result.stderr
        ), result.stderr

commands = []
results = []
with tempfile.TemporaryDirectory(prefix='css-flex-four-patches-', dir='/private/tmp') as scratch:
    parent = Path(scratch)
    orders = [(i,) for i in range(4)] + list(itertools.permutations(range(4)))
    for ordinal, order in enumerate(orders):
        work = parent / str(ordinal)
        work.mkdir()
        for name, data in baseline.items():
            out = work / name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
        for reverse, indices in [(False, order), (True, tuple(reversed(order)))]:
            for index in indices:
                for check in [True, False]:
                    argv = git + ['apply'] + (['--reverse'] if reverse else []) + (['--check'] if check else []) + [str(PATCHES[index])]
                    result = subprocess.run(argv, cwd=work, capture_output=True)
                    commands.append({'order': order, 'argv': argv, 'exit': result.returncode,
                                     'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
                    (HERE / 'PATCH-COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
                    assert result.returncode == 0, commands[-1]
            if not reverse:
                installed = {name: digest((work / name).read_bytes()) for name in paths if (work / name).exists()}
                if len(order) == 4:
                    assert installed == {name: digest((ROOT / name).read_bytes()) for name in paths}
        restored = {str(p.relative_to(work)): p.read_bytes() for p in work.rglob('*') if p.is_file()}
        assert restored == baseline
        results.append({'order': order, 'applies_and_reverses': True, 'installed': installed})

(HERE / 'PATCH-RESULT.json').write_text(json.dumps({
    'head': head, 'patches': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in PATCHES},
    'individual_cases': 4, 'combined_orders': 24, 'commands': len(commands),
    'results': results, 'scratch_removed': not Path(scratch).exists(),
    'scope': 'Independent patch application and exact tree restoration; no clean-upstream runtime claim',
}, indent=2) + '\n')
print(json.dumps({'individual_cases': 4, 'combined_orders': 24, 'commands': len(commands)}))
