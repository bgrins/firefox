from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

r = Path(__file__).resolve().parent
work = r / 'generated-guards'
assert not work.exists()
work.mkdir()
results = []
cases = [('extra-file', 'closed file roster'), ('empty-dir', 'closed directory roster'),
         ('changed-input', 'input hash:'), ('missing-input', 'closed file roster'),
         ('symlink-input', 'nonregular input'), ('duplicate-key', 'duplicate JSON key'),
         ('escaping-name', 'unsafe input name'), ('no-isolation', 'invoke Python with -I -S')]
for name, reason in cases:
    d = work / name
    shutil.copytree(r / 'capsule', d)
    if name == 'extra-file': (d / 'extra').write_text('x')
    elif name == 'empty-dir': (d / 'extra').mkdir()
    elif name == 'changed-input':
        p = d / 'lean/Composition.lean'; p.write_text(p.read_text() + '\n')
    elif name == 'missing-input': (d / 'lean/Composition.lean').unlink()
    elif name == 'symlink-input':
        p = d / 'lean/Composition.lean'; p.unlink(); p.symlink_to('Histories.lean')
    elif name in {'duplicate-key', 'escaping-name'}:
        manifest = d / 'MANIFEST.json'
        if name == 'duplicate-key':
            value = json.loads(manifest.read_text())['REPORT.md']
            manifest.write_text(manifest.read_text().rstrip()[:-1] + ',"REPORT.md":' + json.dumps(value) + '}')
        else:
            value = json.loads(manifest.read_text()); value['./REPORT.md'] = value.pop('REPORT.md')
            manifest.write_text(json.dumps(value))
        freeze = json.loads((d / 'FREEZE.json').read_text())
        freeze['manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        (d / 'FREEZE.json').write_text(json.dumps(freeze))
    args = [sys.executable] + ([] if name == 'no-isolation' else ['-I', '-S']) + [str(d / 'check.py'), '--output', str(work / (name + '-output'))]
    p = subprocess.run(args, capture_output=True, text=True)
    text = p.stdout + p.stderr
    # Alias path changes roster first; this is still a deliberate path/roster rejection.
    if name == 'escaping-name': reason = 'closed file roster'
    assert p.returncode != 0 and 'AssertionError: ' + reason in text, (name, text)
    assert not (work / (name + '-output')).exists()
    results.append({'case': name, 'exit': p.returncode, 'expected_rejection': reason,
                    'output_created': False, 'output': text})
(r / 'GUARDS.json').write_text(json.dumps(results, indent=2) + '\n')
print('PASS', len(results))
