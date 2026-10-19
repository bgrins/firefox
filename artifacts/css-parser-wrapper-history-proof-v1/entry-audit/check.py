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
    return len(manifest)

count = authenticate()
for item in read(ROOT/'SOURCE-PINS.json'):
    p=ROOT/item['retained'] if 'retained' in item else ROOT/'source'/item['path']
    assert digest(p)==item['sha256']
prior=ROOT/'prior'
assert digest(prior/'FREEZE.json')=='0a290a6cbf83b6fa1be729cd13a3aeae23b77a4c6f86718baacbe0655bb83afe'
assert digest(prior/'MANIFEST.json')=='a158bf5fb0be52bb3d252c69e18160e4d3e623a4650204fcff0279eea04fe75a'
m=read(prior/'MANIFEST.json')
for name,pin in read(ROOT/'PRIOR-PINS.json').items():
    assert digest(prior/name)==pin
    if name in m:assert pin==m[name]
for name in ['COMMANDS.json','SECOND-COMMANDS.json']:
    assert all(r['exit']==0 for r in read(ROOT/'discovery'/name))
assert 'Total matches: 6' in (ROOT/'discovery/enable.txt').read_text()
assert 'Total matches: 7' in (ROOT/'discovery/query.txt').read_text()
assert 'Total matches: 4' in (ROOT/'discovery/parse-into.txt').read_text()
assert authenticate()==count
print(json.dumps({'status':'PASS','inputs':count,'kind':'STATIC_SOURCE_ADMISSION_PROPOSAL','new_browser_bug_established':False,'new_proofs':0,'generated_build_outputs':0}))
