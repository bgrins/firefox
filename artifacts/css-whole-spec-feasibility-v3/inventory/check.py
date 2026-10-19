from pathlib import Path
import hashlib
import json
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def pairs(items):
    out = {}
    for key, value in items:
        assert key not in out
        out[key] = value
    return out


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((ROOT / 'MANIFEST.json').read_text(), object_pairs_hook=pairs)
assert set(manifest) == {'files'}
expected = manifest['files']
assert isinstance(expected, dict)
for name, hashed in expected.items():
    rel = Path(name)
    assert not rel.is_absolute() and '..' not in rel.parts and str(rel) == name
    assert len(hashed) == 64 and all(c in '0123456789abcdef' for c in hashed)
    assert digest(ROOT / name) == hashed, name
files = set(expected) | {'MANIFEST.json', 'FREEZE.json'}
directories = {str(parent) for name in files for parent in Path(name).parents if str(parent) != '.'}
for path in ROOT.rglob('*'):
    name = str(path.relative_to(ROOT))
    mode = path.lstat().st_mode
    if stat.S_ISREG(mode):
        assert name in files, name
    elif stat.S_ISDIR(mode):
        assert name in directories, name
    else:
        raise AssertionError(('nonregular entry', name))
assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == files
freeze = json.loads((ROOT / 'FREEZE.json').read_text(), object_pairs_hook=pairs)
assert freeze['manifest_sha256'] == digest(ROOT / 'MANIFEST.json')
assert freeze['checker_sha256'] == digest(ROOT / 'check.py')
result = subprocess.run([sys.executable, '-I', str(ROOT / 'validate.py')], check=True, capture_output=True, text=True)
assert json.loads(result.stdout) == json.loads((ROOT / 'VALIDATION.json').read_text())
print(json.dumps({'status': 'pass', 'manifest_files': len(expected), 'validation': json.loads(result.stdout)}, indent=2))
