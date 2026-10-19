from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).absolute().parent

def digest(path):
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
    freeze = read(ROOT / 'FREEZE.json')
    assert digest(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    assert digest(ROOT / 'check.py') == freeze['checker_sha256']
    manifest = read(ROOT / 'MANIFEST.json')
    expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    files, dirs = set(), set()
    for path in ROOT.rglob('*'):
        assert not path.is_symlink(), path
        assert path.is_file() or path.is_dir(), path
        (files if path.is_file() else dirs).add(str(path.relative_to(ROOT)))
    assert files == expected, ('roster', files ^ expected)
    assert dirs == {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    for name, pin in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and str(path) == name
        assert (ROOT / path).resolve().is_relative_to(ROOT.resolve())
        assert digest(ROOT / path) == pin, name
    pins = {
        'FREEZE.json': '7c0e667019f4da11be3b206d22f2434710930e0a6b8bb55c6a79b419003bc0e8',
        'MANIFEST.json': 'a722d9c8dbc6a5c69cc12ffa95a0128fc9da1a4e898ee26e8e221e099be5871c',
        'check.py': 'be2e47694b54f69e5009add101832f855626b1b01f96d2ff3cb12b5c0575a426',
    }
    for name, pin in pins.items():
        assert digest(ROOT / 'package' / name) == pin
    return len(manifest)

count = authenticate()
result = read(ROOT / 'evidence/replay/RESULT.json')
assert result['total_theorems'] == 136 and result['new_universal_theorems'] == 46
assert result['new_concrete_kernel_examples'] == 9 and result['native_executions'] == 0
assert result == read(ROOT / 'package/receipts/RESULT.json')
assert (ROOT / 'evidence/replay/AXIOMS.txt').read_bytes() == (ROOT / 'package/receipts/AXIOMS.txt').read_bytes()
commands = read(ROOT / 'evidence/replay/COMMANDS.json')
assert all(c['exit'] == 0 for c in commands)
guards = read(ROOT / 'evidence/replay/capsule-guards/RESULT.json')
assert len(guards) == 9 and all(c['rejected_before_local_execution'] and c['exit'] != 0 for c in guards)
assert read(ROOT / 'evidence/TYPE-CHECK.json')['exit'] == 0
assert authenticate() == count
print(json.dumps({'status': 'PASS', 'verdict': 'ACCEPT_SCOPED_MATHEMATICAL_COMPONENT', 'inputs': count, 'native_executions': 0}))
