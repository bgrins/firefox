from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
expected = set(manifest['files'])
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} - {'MANIFEST.json', 'FREEZE.json'}
assert expected == actual, (expected - actual, actual - expected)
for name, digest in manifest['files'].items():
    path = root / name
    assert path.resolve().is_relative_to(root)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
freeze = json.loads((root / 'FREEZE.json').read_text())
assert hashlib.sha256((root / 'MANIFEST.json').read_bytes()).hexdigest() == freeze['manifest_sha256']
print(json.dumps({'status': 'PASS', 'files': len(expected), 'scope': 'research artifact integrity only; no semantic or producer replay'}))
