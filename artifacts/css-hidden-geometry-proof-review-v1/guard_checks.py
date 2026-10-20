import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
sys.dont_write_bytecode = True
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parent
pin = 'a4dc6e88cf8bd4f431875a619017339a2d4ac658d0588ba3585def2d9e419c8c'
results = []
with tempfile.TemporaryDirectory(prefix='hidden-review-guards-') as temp:
    base = Path(temp)
    capsule = base / 'capsule'
    shutil.copytree(root / 'capsule', capsule)
    def attempt(name, flags, expected, reason=None):
        output = base / name
        command = [sys.executable, *flags, str(capsule / 'replay.py'),
                   '--manifest-sha', pin, '--out', str(output), '--verify-only']
        result = subprocess.run(command, capture_output=True, text=True)
        good = (result.returncode == 0) == expected and not output.exists()
        if reason:
            good = good and reason in result.stderr
        results.append(dict(name=name, command=command, exit=result.returncode,
                            stdout=result.stdout, stderr=result.stderr,
                            output_created=output.exists(), passed=good))
        if not good:
            raise RuntimeError(name)
    attempt('intact', ['-I', '-S'], True)
    for name, flags in [('optimized', ['-I', '-S', '-O']),
                        ('double_optimized', ['-I', '-S', '-OO']),
                        ('site_enabled', ['-I']),
                        ('not_isolated', ['-S'])]:
        attempt(name, flags, False, 'REJECT: run python3')
    shadow = capsule / 'json.py'
    marker = base / 'SHADOW_RAN'
    shadow.write_text('from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("ran")\n')
    attempt('unsafe_shadow', ['-S'], False, 'REJECT: run python3')
    if marker.exists():
        raise RuntimeError('shadow executed')
    shadow.unlink()
    extra = capsule / 'extra.txt'
    extra.write_text('extra')
    attempt('extra_file', ['-I', '-S'], False, 'CLOSED_ROSTER')
    extra.unlink()
    extra.mkdir()
    attempt('extra_empty_dir', ['-I', '-S'], False, 'CLOSED_DIRECTORIES')
    extra.rmdir()
    extra.symlink_to(capsule / 'lean/Hidden.lean')
    attempt('symlink', ['-I', '-S'], False, 'SYMLINK')
    extra.unlink()
    model = capsule / 'lean/Hidden.lean'
    old = model.read_bytes()
    model.write_bytes(old + b'\n')
    attempt('model_tamper', ['-I', '-S'], False, 'PAYLOAD_HASH:lean/Hidden.lean')
    model.write_bytes(old)
(root / 'GUARDS.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({'checks': len(results), 'passed': all(r['passed'] for r in results)}))
