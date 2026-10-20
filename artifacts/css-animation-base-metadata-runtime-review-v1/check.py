from pathlib import Path
import hashlib
import json
root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
assert set(manifest) == {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} - {'MANIFEST.json', 'FREEZE.json'}
for name, digest in manifest.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
assert hashlib.sha256((root / 'MANIFEST.json').read_bytes()).hexdigest() == json.loads((root / 'FREEZE.json').read_text())['manifest_sha256']
print('PASS: review integrity only')
