import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
sys.dont_write_bytecode = True
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parent
capsule = root / 'capsule'
out = root / 'guard-controls'
if out.exists():
    raise SystemExit('fresh guard-controls output required')
out.mkdir()
records = []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reseal(path):
    files = {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob('*')) if p.is_file() and p.name not in ('FILES.json', 'FREEZE.json')}
    (path / 'FILES.json').write_text(json.dumps({'files': files}, indent=2, sort_keys=True) + '\n')
    pin = sha(path / 'FILES.json')
    (path / 'FREEZE.json').write_text(json.dumps({'FILES_sha256': pin, 'payload_count': len(files)}, indent=2, sort_keys=True) + '\n')
    return pin

cases = [
 ('nonisolated', 'REJECT: run python3 -I -S'),
 ('optimized', 'REJECT: run python3 -I -S'),
 ('wrong_manifest', 'MANIFEST_PIN'),
 ('source_modified', 'PAYLOAD_HASH'),
 ('extra_file', 'CLOSED_ROSTER'),
 ('empty_cache', 'CLOSED_DIRECTORIES'),
 ('resealed_extra_cache', 'PAYLOAD_ROSTER'),
 ('resealed_role_substitution', 'SOURCE_ROLE_PINS'),
 ('resealed_binding_corruption', 'SOURCE_BINDINGS'),
 ('resealed_sorry', 'MODEL_PROOF_ESCAPE'),
 ('output_inside', 'OUTPUT_OVERLAP'),
 ('output_ancestor', 'OUTPUT_OVERLAP'),
 ('output_exists', 'OUTPUT_EXISTS'),
 ('fifo', 'NONREGULAR'),
 ('resealed_imported_model', 'IMPORTED_MODEL_PIN'),
]
for name, expected in cases:
    copy = out / (name + '-capsule')
    shutil.copytree(capsule, copy)
    pin = sha(copy / 'FILES.json')
    args = [sys.executable, '-I', '-S']
    if name == 'nonisolated': args = [sys.executable, '-S']
    if name == 'optimized': args += ['-O']
    if name == 'wrong_manifest': pin = '0' * 64
    if name == 'source_modified':
        f = copy / 'input/original.cpp'; f.write_bytes(f.read_bytes() + b'\n')
    if name == 'extra_file': (copy / 'unlisted.txt').write_text('extra')
    if name == 'empty_cache': (copy / '__pycache__').mkdir()
    if name == 'resealed_extra_cache':
        (copy / '__pycache__').mkdir(); (copy / '__pycache__/extra.pyc').write_bytes(b'extra'); pin = reseal(copy)
    if name == 'resealed_role_substitution':
        shutil.copyfile(copy / 'input/original.cpp', copy / 'input/candidate.cpp'); pin = reseal(copy)
    if name == 'resealed_binding_corruption':
        f = copy / 'BINDINGS.json'; value = json.loads(f.read_text()); value[0]['unit_sha256'] = '0' * 64; f.write_text(json.dumps(value)); pin = reseal(copy)
    if name == 'resealed_sorry':
        f = copy / 'lean/Subtree.lean'; f.write_text(f.read_text() + '\ntheorem invalid_proof : False := by sorry\n'); pin = reseal(copy)
    if name == 'fifo': os.mkfifo(copy / 'pipe')
    if name == 'resealed_imported_model':
        f = copy / 'lean/Hidden.lean'; f.write_text(f.read_text() + '\n'); pin = reseal(copy)
    args += [str(copy / 'replay.py'), '--manifest-sha', pin]
    destination = None
    if name.startswith('output_'):
        destination = copy / 'output' if name == 'output_inside' else out if name == 'output_ancestor' else out / 'already-exists'
        if name == 'output_exists': destination.mkdir()
        args += ['--out', str(destination)]
    else: args += ['--verify-only']
    result = subprocess.run(args, capture_output=True, text=True)
    (out / (name + '.stdout')).write_text(result.stdout)
    (out / (name + '.stderr')).write_text(result.stderr)
    if result.returncode == 0 or expected not in result.stdout + result.stderr:
        raise RuntimeError('Unexpected guard result ' + name)
    if name == 'output_inside' and destination.exists():
        raise RuntimeError('Output created before rejection')
    records.append({'name': name, 'expected_gate': expected, 'exit': result.returncode, 'tested_manifest_sha256': pin})
    shutil.rmtree(copy)
    if name == 'output_exists': destination.rmdir()
(root / 'GUARDS.json').write_text(json.dumps(records, indent=2, sort_keys=True) + '\n')
print(json.dumps({'guards': len(records), 'outcome': 'all intended gates rejected'}))
