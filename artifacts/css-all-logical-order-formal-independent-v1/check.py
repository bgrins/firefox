import sys
assert sys.flags.isolated and sys.flags.no_site, 'invoke with -I -S'
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).absolute().parent
PINS = {
    'FREEZE.json': 'e89fb0788f7fde9c69fa36c5329e72f1190b697a87168157b5500ca785bc4f04',
    'MANIFEST.json': '492aefc7aa5ae7a0a62b138737d34648adf5122325a40ee47520fdb59ad30ff5',
    'check.py': '213f9c06e4e487a6a1ae75625161b7e8e0422c43e31dcddc3104cec275ceea80',
    'REPORT.md': '6f27972223ceac77ff422d729aceacfc677b02f8bc940404cbbcac29a5c508cf',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('duplicate key', key)
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate():
    assert not ROOT.is_symlink()
    for path in ROOT.rglob('*'):
        assert not path.is_symlink()
        assert path.is_file() or path.is_dir()
    freeze = read(ROOT / 'FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    assert sha(ROOT / 'check.py') == freeze['checker_sha256']
    manifest = read(ROOT / 'MANIFEST.json')
    expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == expected
    directories = {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()} == directories
    for name, pin in manifest.items():
        p = Path(name)
        assert not p.is_absolute() and '..' not in p.parts and str(p) == name
        assert (ROOT / p).resolve().is_relative_to(ROOT.resolve())
        assert sha(ROOT / p) == pin, name
    return manifest

parser = argparse.ArgumentParser()
parser.add_argument('--run', action='store_true')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
manifest = authenticate()
package = ROOT / 'package'
for name, pin in PINS.items():
    assert sha(package / name) == pin
entries = read(package / 'MANIFEST.json')
assert len(entries) == 101 and len({e['path'] for e in entries}) == 101
for e in entries:
    assert sha(package / e['path']) == e['sha256']
replay = ROOT / 'evidence/replay'
result = read(replay / 'RESULT.json')
assert result == read(package / 'receipts/RESULT.json')
assert result['theorems'] == 55
assert result['variants']['candidate']['rows'] == 3042
assert not result['variants']['candidate']['failures']
assert len(result['variants']['original']['failures']) == 294
for name, record in result['variants'].items():
    data = gzip.decompress((replay / 'native' / (name + '.tsv.gz')).read_bytes())
    assert hashlib.sha256(data).hexdigest() == result['raw_sha256'][name]
    if name.startswith('mutant_'):
        assert record['failures'] and record['execution_exit'] in (0, 42)
commands = read(replay / 'COMMANDS.json')
compiles = [c for c in commands if Path(c['command'][0]).name == 'rustc']
assert len(compiles) == 8 and all(c['exit'] == 0 for c in compiles)
axioms = (replay / 'AXIOMS.txt').read_text()
names = read(package / 'THEOREMS.json')
observed = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", axioms, re.M)
assert [n for n, _ in observed] == names and len(names) == 55
for _, group in observed:
    assert set(filter(None, (s.strip() for s in group.split(',')))) <= {'propext', 'Quot.sound', 'Classical.choice'}
for name, count in [('row-challenges', 10), ('integrity', 6)]:
    receipt = read(ROOT / 'evidence' / (name + '.json'))
    assert receipt['result'] == 'PASS' and receipt['rejections'] == count
assert read(ROOT / 'VERDICT.json')['full_native_cssom_closure'] is False
print('PASS:', len(manifest), 'review entries; 55 audits, 3042 candidate operations, six compiled mutants, 16 independent rejection challenges')
if args.run:
    assert args.output and not args.output.exists()
    output = args.output.resolve()
    assert not output.is_relative_to(ROOT.resolve())
    env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'LEAN_'))}
    def run(arguments):
        subprocess.run([sys.executable, '-I', '-S', '-B', *map(str, arguments)], check=True, env=env)
    run([package / 'check.py', '--output', output])
    run([ROOT / 'challenge_rows.py', '--package', package, '--freeze', PINS['FREEZE.json'], '--manifest', PINS['MANIFEST.json'], '--output', output / 'independent-row-challenges'])
    run([ROOT / 'challenge_integrity.py', '--package', package, '--output', output / 'independent-integrity'])
    assert authenticate() == manifest
