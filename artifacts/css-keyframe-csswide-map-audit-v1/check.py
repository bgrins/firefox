import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


seal = json.loads((ROOT / 'FREEZE.json').read_text())
assert sha(ROOT / 'MANIFEST.json') == seal['manifest_sha256']
manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
for name, expected in manifest.items():
    path = ROOT / name
    assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
    assert sha(path) == expected, name
for name, expected in json.loads((ROOT / 'SOURCE-PINS.json').read_text()).items():
    assert sha(ROOT / 'source' / name) == expected
source = (10 + 90) / 2
assert source == 50 and (source + 2 * source) / 2 == 75
assert (42 + 2 * 42) / 2 == 63
assert (14 + 10) / 2 == 12
print(json.dumps({'inputs': len(manifest), 'source_files': 8, 'native_runtime': 'NOT_RUN',
                  'same_effect_expected': 75, 'important_expected': 63, 'initial_fallback_expected': 12}))
