import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
freeze = json.loads((root / 'FREEZE.json').read_text())
manifest_bytes = (root / 'MANIFEST.json').read_bytes()
assert hashlib.sha256(manifest_bytes).hexdigest() == freeze['manifest_sha256']
manifest = json.loads(manifest_bytes)
assert set(manifest) == {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name not in {'MANIFEST.json', 'FREEZE.json'}}
for name, digest in manifest.items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
print(f'PASS: {len(manifest)} retained research inputs; no proof or runtime replay claimed')
