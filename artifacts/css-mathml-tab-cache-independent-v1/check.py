import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
manifest_bytes = (root / 'MANIFEST.json').read_bytes()
if hashlib.sha256(manifest_bytes).hexdigest() != args.manifest_sha:
    raise SystemExit('Manifest authentication failed')
manifest = json.loads(manifest_bytes)
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
expected = set(manifest['files']) | {'MANIFEST.json', 'FREEZE.json'}
if actual != expected:
    raise SystemExit('File inventory mismatch')
for name, digest in manifest['files'].items():
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise SystemExit('Unsafe input path: ' + name)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit('Input authentication failed: ' + name)
freeze = json.loads((root / 'FREEZE.json').read_text())
if freeze['manifest_sha256'] != args.manifest_sha:
    raise SystemExit('Freeze manifest mismatch')
spec = importlib.util.spec_from_file_location('authenticated_review', root / 'review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
result = review.inspect(root)
if result != json.loads((root / 'REVIEW.json').read_text()):
    raise SystemExit('Retained review mismatch')
print(json.dumps({'authenticated_files': len(manifest['files']), **result}, indent=2))
