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
        'FREEZE.json': 'ab963101784ea7d7fd077ac96a63b2d1075bf586eda752fc13a803859567261b',
        'MANIFEST.json': 'f6a64601cd26d168e98c8dd17bccd75f93e12d916a1eb506788b8a01742191d5',
        'check.py': '84c490eeb94a8aacf3d592492c27797d2bf1333b00e752ca2b3c6d5f12a80bf4',
    }
    for name, pin in pins.items():
        assert digest(ROOT / 'package' / name) == pin
    return len(manifest)

parser = argparse.ArgumentParser()
parser.add_argument('--challenges', type=Path)
args = parser.parse_args()
count = authenticate()
replay = read(ROOT / 'evidence/replay/REPLAY.json')
assert replay['status'] == 'PASS' and replay['authenticated_inputs'] == 428
assert (replay['proof']['modules'], replay['proof']['audits']) == (51, 388)
assert replay['native']['states'] == dict(cases=59, seams=56, helpers=230, slices=56, bulk=46)
finding = read(ROOT / 'evidence/trace-challenges/FINDINGS.json')
assert finding['verdict'] == 'BLOCKER' and len(finding['records']) == 5
for record in finding['records']:
    assert record['exit'] == 0 and not record['stderr']
    assert digest(ROOT / 'evidence/trace-challenges' / (record['name'] + '.txt')) == record['raw_sha256']
for command in replay['proof']['commands']:
    if command['log'].endswith('-witness.log'):
        assert command['exit'] == 0
    if command['log'].endswith('-rejected.log'):
        assert command['exit'] == 1
if args.challenges:
    target = args.challenges.absolute()
    assert not target.exists() and not target.resolve().is_relative_to(ROOT.resolve())
    subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT / 'challenge_v1_trace.py'),
                    '--package', str(ROOT / 'package'), '--raw', str(ROOT / 'evidence/replay/native/debug/raw.txt'),
                    '--output', str(target)], check=True)
    fresh = read(target / 'FINDINGS.json')
    assert [(r['name'], r['exit'], r['raw_sha256']) for r in fresh['records']] == [
        (r['name'], r['exit'], r['raw_sha256']) for r in finding['records']]
assert authenticate() == count
print(json.dumps({'status': 'PASS', 'review_verdict': 'BLOCKED_V1_TRACE_VALIDATOR', 'inputs': count}))
