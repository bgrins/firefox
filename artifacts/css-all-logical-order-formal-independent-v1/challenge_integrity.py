import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--package', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
r = a.output / 'package'
shutil.copytree(a.package, r)
m = r / 'MANIFEST.json'
f = r / 'FREEZE.json'
mb, fb = m.read_bytes(), f.read_bytes()
records = []

def run(label, mutate, restore, isolated=True):
    mutate()
    cmd = [sys.executable, *(['-I', '-S'] if isolated else []), '-B', str(r / 'check.py')]
    result = subprocess.run(cmd, capture_output=True, text=True)
    restore()
    assert result.returncode != 0 and 'AssertionError' in result.stderr, (label, result)
    records.append({'label': label, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})

def manifest(text):
    m.write_text(text)
    freeze = json.loads(fb)
    freeze['manifest_sha256'] = hashlib.sha256(m.read_bytes()).hexdigest()
    f.write_text(json.dumps(freeze) + '\n')

def restore_manifest():
    m.write_bytes(mb)
    f.write_bytes(fb)

entries = json.loads(mb)
run('duplicate path with matching outer hash', lambda: manifest(json.dumps(entries + [entries[0]])), restore_manifest)
run('duplicate key with matching outer hash', lambda: manifest(mb.decode().replace('"path":', '"path": "ignored", "path":', 1)), restore_manifest)
run('parent path with matching outer hash', lambda: manifest(json.dumps([dict(entries[0], path='../outside')] + entries[1:])), restore_manifest)
run('absolute path with matching outer hash', lambda: manifest(json.dumps([dict(entries[0], path='/private/tmp/outside')] + entries[1:])), restore_manifest)
q = r / 'native/check_rows.py'
original = q.read_bytes()
external = a.output / 'same-check-rows.py'
external.write_bytes(original)
def make_link():
    q.unlink()
    q.symlink_to(external.resolve())
def restore_file():
    q.unlink()
    q.write_bytes(original)
run('listed byte-identical symlink', make_link, restore_file)
run('nonisolated invocation', lambda: None, lambda: None, isolated=False)
result = subprocess.run([sys.executable, '-I', '-S', '-B', str(r / 'check.py')], capture_output=True, text=True)
assert result.returncode == 0, result.stdout + result.stderr
records.append({'label': 'restored authentication', 'exit': 0, 'stdout': result.stdout, 'stderr': result.stderr})
(a.output / 'CHECK.json').write_text(json.dumps({'result': 'PASS', 'rejections': len(records)-1, 'records': records}, indent=2) + '\n')
shutil.rmtree(r)
