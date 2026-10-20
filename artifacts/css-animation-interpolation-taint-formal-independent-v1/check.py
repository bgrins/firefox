import hashlib
import json
from pathlib import Path
import stat

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
actual = set()
for p in root.rglob('*'):
    mode = p.lstat().st_mode
    assert not stat.S_ISLNK(mode)
    if stat.S_ISDIR(mode):
        continue
    assert stat.S_ISREG(mode)
    actual.add(p.relative_to(root).as_posix())
assert actual == expected
for name, expected_hash in manifest.items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected_hash, name
freeze = json.loads((root / 'FREEZE.json').read_text())
assert hashlib.sha256((root / 'MANIFEST.json').read_bytes()).hexdigest() == freeze['manifest_sha256']
print(json.dumps({'status': 'pass', 'inputs': len(manifest), 'scope': 'review integrity only'}))
