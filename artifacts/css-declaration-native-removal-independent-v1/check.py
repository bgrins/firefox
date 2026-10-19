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
        'FREEZE.json': 'e361bfbd09002e5c67d1bf6932ee6126251173307b4af4aa49e2aef37f20aa7c',
        'MANIFEST.json': '802f53f59828660556896e1e6895f5deea947f6b250253aa1586de7a3d095088',
        'check.py': '8ba8ebd022ecd927c62a5f29536980fd84c26636e25522e9a1bb71917ae21b3b',
    }
    for name, pin in pins.items():
        assert digest(ROOT / 'package' / name) == pin
    return len(manifest)

count = authenticate()
result = read(ROOT / 'evidence/replay/RESULT.json')
assert result['modules'] == 7 and result['audited_theorems'] == 65
assert result['inherited_checkpoint_audits'] == 44 and result['new_audits'] == 21
assert result['native_compilation'] == 'NOT_RUN'
assert result['advance_delete_mutated_module_rejected']
assert result == read(ROOT / 'package/receipts/RESULT.json')
commands = read(ROOT / 'evidence/replay/COMMANDS.json')
failed = [c for c in commands if c['exit'] != 0]
assert len(failed) == 1 and 'NativeRemoval.lean:46' in failed[0]['stdout']
assert 'loop selected (rawDelete raw old.id pre.length) (pre.length + 1)' in failed[0]['stdout']
guards = read(ROOT / 'evidence/replay/guards/RESULT.json')
assert len(guards) == 2 and all(c['rejected_before_output'] and c['exit'] != 0 for c in guards)
assert read(ROOT / 'evidence/EXACT-MUTANT.json')['exit'] == 0
source = read(ROOT / 'evidence/CURRENT-SOURCE-COMPARISON.json')
assert len(source['complete_bindings']) == 10 and all(c['complete_body_match'] for c in source['complete_bindings'])
assert all(c['full_file_equal'] for c in source['files'])
import re
names = read(ROOT / 'package/THEOREMS.json')
audits = re.findall(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", (ROOT / 'evidence/replay/AXIOMS.txt').read_text())
assert [n for n, _ in audits] == names and len(set(names)) == 65
assert all({x.strip() for x in group.split(',') if x.strip()} <= {'propext','Quot.sound','Classical.choice'} for _, group in audits)
assert authenticate() == count
print(json.dumps({'status': 'PASS', 'verdict': 'ACCEPT_SCOPED_LOOP_COMPONENT', 'inputs': count, 'native_executions': 0}))
