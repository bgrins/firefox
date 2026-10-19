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
        'FREEZE.json': '133a15bc867d76b46af31f55e3f9126c7d699b834278d82c95e6ae225a884549',
        'MANIFEST.json': '9776f7c0c24b18d7cae27b25fc8a1673472a57382516d1198ae32c25a3e64847',
        'check.py': 'f5256d82e1f034ce5339ecbb9b5210c4a7ac1cfb6b5fa529b50636f2ae5321b7',
    }
    for name, pin in pins.items():
        assert digest(ROOT / 'package' / name) == pin
    return len(manifest)

count = authenticate()
replay = read(ROOT / 'evidence/replay/REPLAY.json')
assert replay['status'] == 'PASS' and replay['authenticated_inputs'] == 442
assert (replay['proof']['modules'], replay['proof']['audits']) == (51, 388)
assert replay['native']['states'] == dict(cases=59, seams=56, helpers=230, slices=56, bulk=46, ordered_events=503, complete_trace_equal=True)
mutations = replay['native']['trace_mutations']
assert mutations['status'] == 'PASS' and mutations['rejected'] == len(mutations['checks']) == 3043
assert all(c['status'] == 'REJECTED' for c in mutations['checks'])
assert len(mutations['historical_acceptances']) == 9
assert all(c['v1_exit'] == 0 and c['v2'] == 'REJECTED' for c in mutations['historical_acceptances'])
five = read(ROOT / 'evidence/old-five/CHECK.json')
assert five['status'] == 'PASS' and len(five['records']) == 5
for record in five['records']:
    assert record['exit'] != 0
    path = ROOT / 'evidence/old-five' / (record['name'] + '.txt')
    assert digest(path) == record['raw_sha256']
    assert record['intended_reason'] in path.with_suffix('.log').read_text()
integrity = read(ROOT / 'evidence/integrity/CHECK.json')
assert integrity['status'] == 'PASS' and len(integrity['cases']) == 8
assert all(c['exit'] != 0 and not c['output_created'] for c in integrity['cases'])
for command in replay['proof']['commands']:
    if command['log'].endswith('-witness.log'):
        assert command['exit'] == 0
    if command['log'].endswith('-rejected.log'):
        assert command['exit'] == 1
assert authenticate() == count
print(json.dumps({'status': 'PASS', 'review_verdict': 'ACCEPT_BOUNDED_COMPONENT', 'inputs': count}))
