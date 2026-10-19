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
        'FREEZE.json': 'e8a1ef4c1e66b08fb7f49dcd8ff58ae3eb08e84e71a55a2d26c5e653c0c82c1d',
        'MANIFEST.json': '57aaf02359108b1c986523bb35ffb0cba68eb74dfb1a0592c22f3196e1b38347',
        'check.py': 'badcb9a5010717a9bf6a6ce3cde818cea02579c5f108883747920c6fa1d79081',
    }
    for name, pin in pins.items():
        assert digest(ROOT / 'package' / name) == pin
    return len(manifest)

count = authenticate()
result = read(ROOT / 'evidence/replay/RESULT.json')
assert result['total_theorems'] == 49 and result['universal_theorems'] == 28
assert result['concrete_kernel_examples'] == 21 and result['native_executions'] == 0
assert result == read(ROOT / 'package/receipts/RESULT.json')
assert (ROOT / 'evidence/replay/AXIOMS.txt').read_bytes() == (ROOT / 'package/receipts/AXIOMS.txt').read_bytes()
commands = read(ROOT / 'evidence/replay/COMMANDS.json')
assert all(c['exit'] == 0 for c in commands)
guards = read(ROOT / 'evidence/replay/capsule-guards/RESULT.json')
assert len(guards) == 9 and all(c['rejected_before_local_execution'] and c['exit'] != 0 for c in guards)
assert read(ROOT / 'evidence/TYPE-CHECK.json')['exit'] == 0
observation = read(ROOT / 'evidence/LIVE-OBSERVATION.json')
assert observation['historical_capsule_remains_proof_target'] and observation['not_new_candidate_acceptance']
assert sum(c['exact_slice_equal'] for c in observation['bindings']) == 14
assert sum(c['visibility_only_difference'] for c in observation['bindings']) == 1
import re
names = read(ROOT / 'package/THEOREMS.json')
audits = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", (ROOT / 'evidence/replay/AXIOMS.txt').read_text(), re.M)
assert [n for n, _ in audits] == names and len(set(names)) == 49
assert all({x.strip() for x in group.split(',') if x.strip()} <= {'propext','Quot.sound','Classical.choice'} for _, group in audits)
assert authenticate() == count
print(json.dumps({'status': 'PASS', 'verdict': 'ACCEPT_CONDITIONAL_IDENTITY_COMPONENT', 'inputs': count, 'native_executions': 0}))
