import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S, without optimization')
sys.dont_write_bytecode = True

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'css-primary-destruction-callback-audit-v1'
manifest = SOURCE / 'FILES.json'
expected = hashlib.sha256(manifest.read_bytes()).hexdigest()
files = json.loads(manifest.read_text())
results = []

def run(label, capsule, flags, success, needle=None):
    command = [sys.executable, *flags, str(capsule / 'check.py'), '--files-sha256', expected]
    result = subprocess.run(command, text=True, capture_output=True)
    (ROOT / (label + '.stdout')).write_text(result.stdout)
    (ROOT / (label + '.stderr')).write_text(result.stderr)
    if (result.returncode == 0) != success:
        raise RuntimeError((label, result.returncode, result.stdout, result.stderr))
    if needle and needle not in result.stderr:
        raise RuntimeError((label, 'wrong rejection', result.stderr))
    if 'AUDIT_SHADOW_EXECUTED' in result.stderr:
        raise RuntimeError('shadow imported before guard')
    results.append({'label': label, 'command': command, 'exit': result.returncode,
                    'expected_success': success, 'expected_reason': needle,
                    'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest(),
                    'stderr_sha256': hashlib.sha256(result.stderr.encode()).hexdigest()})

def copy_capsule(destination):
    destination.mkdir()
    for name in [*files, 'FILES.json', 'FREEZE.json']:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, target)

run('canonical', SOURCE, ['-I', '-S'], True)
with tempfile.TemporaryDirectory(prefix='primary-destruction-audit-') as temporary:
    path = Path(temporary) / 'source'
    copy_capsule(path)
    run('relocated', path, ['-I', '-S'], True)
    for label, flags in [('optimized', ['-I', '-S', '-O']),
                         ('double-optimized', ['-I', '-S', '-OO']),
                         ('nonisolated', ['-S']), ('site-enabled', ['-I'])]:
        run(label, path, flags, False, 'use python3 -I -S')
    (path / 'json.py').write_text("raise RuntimeError('AUDIT_SHADOW_EXECUTED')\n")
    run('preimport-shadow', path, ['-S'], False, 'use python3 -I -S')
    (path / 'json.py').unlink()
    (path / 'unexpected').mkdir()
    run('extra-directory', path, ['-I', '-S'], False, 'unexpected directory')
    (path / 'unexpected').rmdir()
    (path / 'source' / 'alias').symlink_to('nsIFrame.frozen.cpp')
    run('source-symlink', path, ['-I', '-S'], False, 'nonregular input')
    (path / 'source' / 'alias').unlink()
    target = path / 'source' / 'nsIFrame.frozen.cpp'
    target.write_bytes(target.read_bytes() + b'\n')
    run('stale-source', path, ['-I', '-S'], False, 'input hash mismatch')
    shutil.copyfile(SOURCE / 'source/nsIFrame.frozen.cpp', target)
    run('restored', path, ['-I', '-S'], True)

if hashlib.sha256(manifest.read_bytes()).hexdigest() != expected:
    raise RuntimeError('source manifest changed')
(ROOT / 'CHECKS.json').write_text(json.dumps({'source_FILES_sha256': expected,
    'source_FREEZE_sha256': hashlib.sha256((SOURCE / 'FREEZE.json').read_bytes()).hexdigest(),
    'checks': results, 'cleanup': 'temporary manifest-only copy removed; no compiler products created',
    'history': 'A metadata-generation import without isolation rejected at the extractor guard; retried with -I -S. No extractor payload executed in rejected attempt.'}, indent=2) + '\n')
print(json.dumps({'result': 'PASS', 'positive': 3, 'negative': 8,
                  'source_FILES_sha256': expected}))
