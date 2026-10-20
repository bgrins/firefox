import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
dev = Path(sys.argv[2]).resolve()
receipt = Path(__file__).resolve().parent
manifest = json.loads((source / 'MANIFEST.json').read_text())
results = []
for kind, expected in [('changed', 'input hash'), ('missing', 'closed file roster'), ('extra', 'closed file roster'), ('empty-directory', 'closed directory roster'), ('symlink', 'nonregular input'), ('duplicate', 'duplicate key'), ('nonisolated', 'use python3 -I -S'), ('optimized', 'use python3 -I -S'), ('double-optimized', 'use python3 -I -S'), ('inside-output', 'fresh external output required')]:
    case = dev / ('guard-' + kind)
    case.mkdir()
    for name in [*manifest, 'MANIFEST.json', 'FREEZE.json']:
        target = case / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    if kind == 'changed':
        with (case / 'lean/PublicationModel.lean').open('a') as f: f.write('\n')
    if kind == 'missing': (case / 'lean/PublicationModel.lean').unlink()
    if kind == 'extra': (case / 'EXTRA').write_text('unexpected')
    if kind == 'empty-directory': (case / 'unexpected-empty').mkdir()
    if kind == 'symlink':
        (case / 'lean/PublicationModel.lean').unlink()
        (case / 'lean/PublicationModel.lean').symlink_to(source / 'lean/PublicationModel.lean')
    if kind == 'duplicate':
        text = (case / 'MANIFEST.json').read_text()
        key = next(iter(manifest))
        text = text.rstrip()[:-1] + ', ' + json.dumps(key) + ': ' + json.dumps(manifest[key]) + '}\n'
        (case / 'MANIFEST.json').write_text(text)
        seal = json.loads((case / 'FREEZE.json').read_text())
        seal['manifest_sha256'] = hashlib.sha256(text.encode()).hexdigest()
        (case / 'FREEZE.json').write_text(json.dumps(seal))
    out = dev / ('guard-output-' + kind)
    if kind == 'inside-output': out = case / '..' / case.name / 'new-output'
    options = [] if kind == 'nonisolated' else ['-I', '-S']
    if kind == 'optimized': options.append('-O')
    if kind == 'double-optimized': options.append('-OO')
    command = [sys.executable, *options, str(case / 'check.py'), '--output', str(out)]
    result = subprocess.run(command, capture_output=True, text=True)
    log = result.stdout + result.stderr
    (receipt / ('guard-' + kind + '.log')).write_text(log)
    assert result.returncode != 0 and expected in log, (kind, log)
    assert not out.exists(), kind
    results.append(dict(id=kind, command=command, exit=result.returncode, expected_reason=expected, no_output=True))
    shutil.rmtree(case)
(receipt / 'GUARDS.json').write_text(json.dumps(results, indent=2) + '\n')
print('10 rejection cases passed')
