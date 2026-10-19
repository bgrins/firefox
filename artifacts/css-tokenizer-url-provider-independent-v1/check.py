#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site, 'invoke with -I -S'
ROOT = Path(__file__).absolute().parent
PINS = {
    'FREEZE.json': '4731757d012a20c450ba10185676f4d9c8be90a5154717809f79528fedbff56a',
    'MANIFEST.json': '7de3087ee7380f3b9fd2e8eb4cb8d9fb31074706e67333fec707d986faab2f97',
    'check.py': '0116f3d2ed1066938de810a4bd91fa80c0b10bc6dd8dc2a38b7f8aa6e3bdee84',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('duplicate JSON key', key)
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate(root):
    assert not root.is_symlink()
    for path in root.rglob('*'):
        assert not path.is_symlink(), ('symlink', str(path))
        assert path.is_file() or path.is_dir(), ('nonregular', str(path))
    freeze = read(root / 'FREEZE.json')
    assert sha(root / 'MANIFEST.json') == freeze['manifest_sha256']
    assert sha(root / 'check.py') == freeze['checker_sha256']
    manifest = read(root / 'MANIFEST.json')
    expected = set(manifest) | {'FREEZE.json', 'MANIFEST.json'}
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    assert actual == expected, ('closed file roster', actual ^ expected)
    directories = {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    assert directories == {str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir()}
    for name, pin in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and str(path) == name
        assert (root / path).resolve().is_relative_to(root.resolve())
        assert sha(root / path) == pin, ('hash', name)
    return manifest

parser = argparse.ArgumentParser()
parser.add_argument('--run', action='store_true')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
manifest = authenticate(ROOT)
package = ROOT / 'package'
for name, pin in PINS.items():
    assert sha(package / name) == pin
assert len(authenticate(package)) == 436
receipt = read(ROOT / 'evidence/replay/REPLAY.json')
assert receipt['status'] == 'PASS' and receipt['source_definitions'] == 44
proof = receipt['proof']
assert (proof['modules'], proof['audits'], proof['new_modules'], proof['new_audits']) == (34, 281, 11, 96)
assert len(proof['mutations']) == 4
assert all(m['definition_and_counterexample'] == 'PASS' and m['unchanged_theorems'] == 'REJECTED' for m in proof['mutations'])
native = receipt['native']
assert native['status'] == 'PASS' and native['cases'] == 57 and len(native['modes']) == 3
assert len(native['native_mutants']) == 4
assert all(m['compiled'] and m['unexpected_differences'] > 0 for m in native['native_mutants'])
for mode in ['debug', 'release', 'fast-release']:
    assert sha(ROOT / 'evidence/replay/native' / mode / 'raw.txt') == native['raw_sha256']
    comp = read(ROOT / 'evidence/replay/native' / (mode + '-reference') / 'COMPARISON.json')
    assert not comp['unexpected_differences'] and comp['tokens'] == 130
    assert len(comp['intentional_intermediate_cursor_differences']) == 7
model = read(ROOT / 'evidence/replay/native/model/CHECK.json')
assert model['status'] == 'PASS' and (model['first_tokens'], model['delegated_strings']) == (57, 11)
for name, count, field in [('integrity', 8, 'rejections'), ('comparator', 4, 'rejected')]:
    challenge = read(ROOT / 'evidence' / name / 'CHECK.json')
    assert challenge['result'] == 'PASS' and challenge[field] == count
    for record in challenge['records']:
        assert (record['exit'] == 0) == (record['label'] == 'restored authentication')
assert read(ROOT / 'VERDICT.json')['full_native_provider_complete'] is False
print('PASS: authenticated', len(manifest), 'review entries; scoped URL component and retained independent evidence')
if args.run:
    assert args.output and not args.output.exists()
    output = args.output.resolve()
    assert not output.is_relative_to(ROOT.resolve())
    env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'LEAN_'))}
    subprocess.run([sys.executable, '-I', '-S', '-B', str(package / 'check.py'), '--run', '--output', str(output)], env=env, check=True)
    assert authenticate(ROOT) == manifest
