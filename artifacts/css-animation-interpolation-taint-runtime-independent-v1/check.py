import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
raw = (root / 'MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == json.loads((root / 'FREEZE.json').read_text())['manifest_sha256']
manifest = json.loads(raw)
assert set(manifest) == {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name not in {'MANIFEST.json', 'FREEZE.json'}}
for name, expected in manifest.items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
print(f'PASS {len(manifest)} review inputs; retained runtime evidence; no browser replay')
