import hashlib
import json
import sys
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site, 'Use python3 -I -S'
root = Path(__file__).absolute().parent


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, 'duplicate JSON key'
        result[key] = value
    return result


def read(name):
    return json.loads((root / name).read_text(), object_pairs_hook=unique)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not root.is_symlink()
for path in root.rglob('*'):
    assert not path.is_symlink() and (path.is_file() or path.is_dir())
freeze = read('FREEZE.json')
assert digest(root / 'MANIFEST.json') == freeze['manifest_sha256']
assert digest(root / 'check.py') == freeze['checker_sha256']
manifest = read('MANIFEST.json')
expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == expected
for name, expected_hash in manifest.items():
    relative = Path(name)
    assert not relative.is_absolute() and '..' not in relative.parts and str(relative) == name
    assert digest(root / relative) == expected_hash, name
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir()} == {
    str(parent) for name in expected for parent in Path(name).parents if str(parent) != '.'
}
ledger = read('ledger-slice.json')
rows = ledger['requirements']
ids = [row['id'] for row in rows]
assert len(ids) == len(set(ids)) == 19
features = {row['id']: row for row in read('local/coverage.json')['features']}
for row in rows:
    assert row['revision'] == 1 and row['certified_closed'] is False
    assert row['statement'] and row['coverage']['remaining']
    assert row['source']['section_url'].startswith(row['source']['document'])
    assert row['source']['binding'].endswith('complete HTML/source lock pending')
    for dep in row['dependencies']:
        assert dep in ids or dep in ledger['external_dependencies'], dep
    for feature in row['coverage']['feature_ids']:
        assert feature in features, feature
for feature in read('local/selected-coverage.json'):
    assert feature == features[feature['id']]
for row in read('LOCAL-SOURCES.json')['lean_read_only_not_replayed']:
    assert digest(root / row['copy']) == row['sha256']
print(json.dumps({'authenticated_files': len(manifest), 'worked_requirement_records': len(rows),
                  'certified_closed_records': 0, 'status': 'research schema/reference checks only',
                  'lean_native_browser_execution': False}, sort_keys=True))
