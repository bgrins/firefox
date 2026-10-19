#!/usr/bin/env python3
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

P = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_text())
def run(args, cwd):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout
freeze = load(P / 'FREEZE.json')
assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
inputs = load(P / 'INPUTS.json')
for name, expected in inputs.items():
    assert sha(P / name) == expected, name
assert len(inputs) == freeze['entries']
common = P / 'evidence/css-fontface-provider-common-candidate-v1'
wpt = P / 'evidence/css-fontface-provider-wpt-v2'
assert sha(common / 'MANIFEST.json') == '8814399049cbf897b2dfb226cfd7f8fba74090eafd13c64f74c89736b2a8fd90'
assert sha(wpt / 'MANIFEST.json') == 'd2d0b2806fcf5845c04728256162dc28d9919e9d4bfd89c4c881e6f3b5ad6fd8'
cm = load(common / 'MANIFEST.json')['files']
wm = load(wpt / 'MANIFEST.json')
pins = load(P / 'NATIVE-PINS.json')
assert len(pins) == 16
for rel, row in pins.items():
    prefix = '' if 'original/' + rel in cm else 'backend/'
    for label in ['original', 'candidate']:
        assert sha(P / label / rel) == row[label] == cm[prefix + label + '/' + rel]
assert sha(P / 'common.patch') == cm['common.patch']
assert sha(P / 'backend.patch') == cm['backend/backend-clone.patch']
assert (P / 'native.patch').read_bytes() == (P / 'common.patch').read_bytes() + (P / 'backend.patch').read_bytes()
for rel, row in load(P / 'TEST-PINS.json').items():
    assert sha(P / 'live-tests' / rel) == row['live']
    assert sha(P / 'tests' / rel) == row['proposed'] == wm['proposal/' + Path(rel).name]
    assert (P / 'tests' / rel).read_bytes() == (P / 'proposal' / Path(rel).name).read_bytes()
for kind, directory in [('CONTEXT', 'context'), ('RESOURCE', 'resources'), ('REGRESSION', 'regressions'), ('METADATA', 'metadata'), ('CONFIG', 'config')]:
    for rel, expected in load(P / (kind + '-PINS.json')).items():
        if expected is not None:
            assert sha(P / directory / rel) == expected
for name in ['harness.py', 'check.py']:
    ast.parse((P / name).read_text())
registered = json.loads(run(['node', str(P / 'register.cjs'), str(P)], P))
assert registered == load(P / 'CASES.json')
assert list(map(len, registered.values())) == [12, 28, 28]
with tempfile.TemporaryDirectory(prefix='fontface-integration-check-') as tmp:
    tree = Path(tmp)
    shutil.copytree(P / 'original', tree, dirs_exist_ok=True)
    shutil.copytree(P / 'live-tests', tree, dirs_exist_ok=True)
    for patch in ['test-install.patch', 'native.patch']:
        run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(P / patch)], tree)
    for rel, row in pins.items():
        assert sha(tree / rel) == row['candidate']
    for rel, row in load(P / 'TEST-PINS.json').items():
        assert sha(tree / rel) == row['proposed']
    js = tree / 'testing/web-platform/tests/css/css-font-loading/fontface-loaded-size-adjust-canvas.any.js'
    run(['node', '--check', str(js)], tree)
    html = js.with_name('fontface-loaded-size-adjust-update.html').read_text()
    script = tree / 'dom.js';script.write_text(re.findall(r'<script>(.*?)</script>', html, re.S)[0])
    run(['node', '--check', str(script)], tree)
    for patch in ['native.patch', 'test-install.patch']:
        run(['patch', '--batch', '--fuzz=0', '-R', '-p1', '-i', str(P / patch)], tree)
    for rel, row in pins.items():
        assert sha(tree / rel) == row['original']
    for rel, row in load(P / 'TEST-PINS.json').items():
        assert sha(tree / rel) == row['live']
print(json.dumps({'status':'PASS', 'entries':len(inputs), 'native_files':16,
                  'exact_apply_reverse':True, 'registered_case_counts':[12,28,28],
                  'callbacks_executed':False, 'native_build_or_browser_run':False}, indent=2))
