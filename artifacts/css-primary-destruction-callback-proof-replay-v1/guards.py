import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S without optimization')
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'relocated-source'
FILES = hashlib.sha256((SOURCE / 'FILES.json').read_bytes()).hexdigest()
WORK = ROOT / 'guard-work'
WORK.mkdir()
records = []

def run(name, entry, flags, mutation=None, expected='use python3 -I -S'):
    case = WORK / name
    shutil.copytree(SOURCE, case)
    marker = case / 'shadow-ran'
    if mutation:
        mutation(case)
    out = ROOT / ('forbidden-' + name)
    cmd = ['python3', *flags, str(case / entry)]
    if entry == 'check.py':
        cmd += ['--files-sha256', FILES, '--output', str(out)]
    p = subprocess.run(cmd, text=True, capture_output=True)
    valid = p.returncode != 0 and expected in p.stderr and not out.exists() and not marker.exists()
    row = dict(name=name, command=cmd, exit=p.returncode, stdout=p.stdout,
               stderr=p.stderr, output_absent=not out.exists(), shadow_absent=not marker.exists(),
               expected_rejection=expected, passed=valid)
    records.append(row)
    (ROOT / 'GUARDS.json').write_text(json.dumps(records, indent=2) + '\n')
    if not valid:
        raise RuntimeError(name)
    shutil.rmtree(case)

for entry in ['check.py', 'source_extract.py']:
    prefix = entry.removesuffix('.py')
    for name, flags in [('optimized', ['-I', '-S', '-O']), ('double-optimized', ['-I', '-S', '-OO']),
                        ('nonisolated', ['-S']), ('site-enabled', ['-I'])]:
        run(prefix + '-' + name, entry, flags)
    def shadow(case):
        (case / 'json.py').write_text('from pathlib import Path\nPath(__file__).with_name("shadow-ran").write_text("executed")\n')
    run(prefix + '-shadow', entry, ['-S'], shadow)

run('extra-directory', 'check.py', ['-I','-S'],
    lambda p: (p/'unlisted').mkdir(), 'unexpected directory: unlisted')
run('nested-seal', 'check.py', ['-I','-S'],
    lambda p: (p/'lean'/'FREEZE.json').write_text('{}'), 'unexpected file: lean/FREEZE.json')
def stale(p):
    f=p/'lean/Deletion.lean';f.write_text(f.read_text()+'\n')
run('stale-source', 'check.py', ['-I','-S'], stale, 'input hash mismatch: lean/Deletion.lean')
def symlink(p):
    f=p/'lean/Deletion.lean';f.unlink();f.symlink_to(SOURCE/'lean/Deletion.lean')
run('symlink-source', 'check.py', ['-I','-S'], symlink, 'nonregular input: lean/Deletion.lean')
def missing(p):
    (p/'lean/Deletion.lean').unlink()
run('missing-source', 'check.py', ['-I','-S'], missing, 'missing input')
WORK.rmdir()
print(json.dumps({'negative_guards': len(records), 'all_passed': all(x['passed'] for x in records)}))
