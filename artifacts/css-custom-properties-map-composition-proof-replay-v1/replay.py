import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).absolute().parent
SOURCE = ROOT.parent / 'css-custom-properties-map-composition-proof-v1'
PINS = {
    'MANIFEST.json': 'edbe97d28bd36dbfdf684bc3adf05d2a9362d1924ab43759e79755a556885627',
    'FREEZE.json': '642d3b6e681794c7c1edf1f9cab8b8afcbfcde662ff410e6039b6151b9f950aa',
    'check.py': '331fb42e77d74714be791974cfd744c8d39487d03db88722d6515c8e74f8bddc',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for name, digest in PINS.items():
    assert sha(SOURCE / name) == digest
pins = json.loads((SOURCE / 'MANIFEST.json').read_text())
for name, digest in pins.items():
    p = Path(name)
    assert not p.is_absolute() and '..' not in p.parts and str(p) == name
    assert not (SOURCE / p).is_symlink() and sha(SOURCE / p) == digest
assert {str(p.relative_to(SOURCE)) for p in SOURCE.rglob('*') if p.is_file()} == set(pins) | {'MANIFEST.json', 'FREEZE.json'}
work = Path(sys.argv[1]).absolute()
assert not work.exists() and not work.is_relative_to(SOURCE)
work.mkdir(parents=True)

def copy_capsule(destination):
    destination.mkdir()
    for name in [*pins, 'MANIFEST.json', 'FREEZE.json']:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((SOURCE / name).read_bytes())

capsule = work / 'capsule'
copy_capsule(capsule)
env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'LEAN_'))}
command = [sys.executable, '-I', '-S', str(capsule / 'check.py'), '--output', str(work / 'output')]
p = subprocess.run(command, text=True, capture_output=True, env=env)
(ROOT / 'relocated-stdout.txt').write_text(p.stdout)
(ROOT / 'relocated-stderr.txt').write_text(p.stderr)
(ROOT / 'relocated-command.json').write_text(json.dumps({'command': command, 'returncode': p.returncode, 'source_pins': PINS}, indent=2) + '\n')
assert p.returncode == 0, p.stdout + p.stderr
results = []
for name in ['altered-proof', 'altered-native-source', 'unlisted-module', 'unlisted-directory', 'symlink', 'duplicate-json-key', 'unsafe-manifest-path', 'missing-input']:
    root = work / name
    copy_capsule(root)
    if name == 'altered-proof':
        f = root / 'lean/Composition.lean'
        f.write_text(f.read_text() + '\n-- corrupted\n')
    elif name == 'altered-native-source':
        f = root / 'imports/count/source/combined.rs'
        f.write_text(f.read_text() + '\n// corrupted\n')
    elif name == 'unlisted-module':
        (root / 'json.py').write_text('raise RuntimeError("unexpected import")\n')
    elif name == 'unlisted-directory':
        (root / 'extra').mkdir()
    elif name == 'symlink':
        f = root / 'lean/Composition.lean'
        f.unlink()
        f.symlink_to(SOURCE / 'lean/Composition.lean')
    elif name == 'duplicate-json-key':
        f = root / 'FREEZE.json'
        f.write_text(f.read_text().replace('{', '{"status": "duplicate",', 1))
    elif name == 'unsafe-manifest-path':
        f = root / 'MANIFEST.json'
        data = json.loads(f.read_text())
        data['../outside'] = '0' * 64
        f.write_text(json.dumps(data))
        seal = root / 'FREEZE.json'
        data = json.loads(seal.read_text())
        data['manifest_sha256'] = sha(f)
        seal.write_text(json.dumps(data))
    elif name == 'missing-input':
        (root / 'lean/Composition.lean').unlink()
    output = work / (name + '-output')
    cmd = [sys.executable, '-I', '-S', str(root / 'check.py'), '--output', str(output)]
    p = subprocess.run(cmd, text=True, capture_output=True, env=env)
    assert p.returncode != 0 and not output.exists(), name
    results.append({'case': name, 'command': cmd, 'returncode': p.returncode, 'output_absent': not output.exists(), 'stdout': p.stdout, 'stderr': p.stderr})
(ROOT / 'authentication-challenges.json').write_text(json.dumps(results, indent=2) + '\n')
evidence = ROOT / 'evidence'
evidence.mkdir()
for path in (work / 'output').rglob('*'):
    if path.is_file() and path.suffix in ['.json', '.log', '.lean']:
        target = evidence / path.relative_to(work / 'output')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
for name, digest in pins.items():
    assert sha(SOURCE / name) == digest
(ROOT / 'RESULT.json').write_text(json.dumps({'relocated_exit': 0, 'tamper_rejections': len(results), 'source_inputs': len(pins), 'source_postauth': True, 'work': str(work)}, indent=2) + '\n')
print((ROOT / 'RESULT.json').read_text())
