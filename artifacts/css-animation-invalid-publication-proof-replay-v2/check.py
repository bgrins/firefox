import hashlib
import json
from pathlib import Path
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')
root = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
seal = json.loads((root/'FREEZE.json').read_text())
assert sha(root/'FILES.json') == seal['files_sha256']
files = json.loads((root/'FILES.json').read_text())
assert all(not p.is_symlink() for p in root.rglob('*'))
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == set(files) | {'FILES.json', 'FREEZE.json'}
for name, expected in files.items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert sha(root/name) == expected, name
for label in ['canonical', 'relocated']:
    row = json.loads((root/label/'CHECK.json').read_text())
    assert (row['inputs'], row['reports'], row['new'], row['bindings']) == (49, 81, 42, 29)
guards = json.loads((root/'GUARDS.json').read_text())
assert len(guards) == 10 and all(r['exit'] != 0 and r['no_output'] for r in guards)
print('PASS retained receipt integrity; proof replay and native admissions remain separate')
