import hashlib
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p != root / 'MANIFEST.json'}
expected = set(manifest['files'])
errors = []
if actual != expected:
    errors.append({'missing': sorted(expected - actual), 'extra': sorted(actual - expected)})
for name, digest in manifest['files'].items():
    path = root / name
    if path.is_symlink() or not path.is_file():
        errors.append({'invalid_path': name})
    elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        errors.append({'hash_mismatch': name})
print(json.dumps({'status': 'FAIL' if errors else 'PASS', 'entries': len(expected), 'errors': errors}))
sys.exit(bool(errors))
