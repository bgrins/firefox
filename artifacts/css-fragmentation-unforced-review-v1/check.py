import hashlib
import json
from pathlib import Path
import stat

root = Path(__file__).resolve().parent
files = json.loads((root / 'FILES.json').read_text())
allowed = set(files) | {'FILES.json'}
actual = set()
allowed_dirs = {str(parent) for name in allowed for parent in Path(name).parents if str(parent) != '.'}
actual_dirs = set()
for p in root.rglob('*'):
    mode = p.lstat().st_mode
    assert stat.S_ISDIR(mode) or stat.S_ISREG(mode), str(p)
    if stat.S_ISDIR(mode):
        actual_dirs.add(p.relative_to(root).as_posix())
    if stat.S_ISREG(mode):
        actual.add(p.relative_to(root).as_posix())
assert actual == allowed and actual_dirs == allowed_dirs
for name, expected in files.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
result = json.loads((root / 'receipts/RESULT.json').read_text())
assert len(result['producer']['exact_audits']) == 34
assert result['producer']['mutants'] == 9
assert len(result['independent_challenges']) == 7 and len(result['guards']) == 4
print('Independent review receipt integrity: 34 producer audits, 9 mutants, 7 challenges, 4 guards')
