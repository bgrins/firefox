import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
root = Path(__file__).absolute().parent
assert not any(p.is_symlink() for p in [root, *root.parents])
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result
        result[key] = value
    return result
def read(name):
    return json.loads((root / name).read_text(), object_pairs_hook=unique)
for path in root.rglob('*'):
    assert not path.is_symlink() and (path.is_file() or path.is_dir())
seal = read('FREEZE.json')
assert digest(root / 'MANIFEST.json') == seal['manifest_sha256']
assert digest(root / 'check.py') == seal['checker_sha256']
manifest = read('MANIFEST.json')
expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == expected
expected_dirs = {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir()} == expected_dirs
for name, sha in manifest.items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts and str(Path(name)) == name
    assert digest(root / name) == sha
result = read('receipts/replay/CHECK.json')
assert result['inputs'] == 29 and result['axiom_reports'] == 31 and result['source_bindings'] == 27
assert all(c['exit'] == 0 for c in result['commands'])
mutations = result['mutations']
assert len(mutations) == 5 and mutations[0]['observed'] == '|'.join(['true'] * 7)
assert all(m['compiled_definitions'] and m['observed'] != mutations[0]['observed'] for m in mutations[1:])
guards = read('receipts/GUARDS.json')
assert len(guards) == 5 and all(g['exit'] != 0 and g['output_not_created'] for g in guards)
assert read('PRODUCER.json')['post_replay_inputs_authenticated'] == 29
print(json.dumps({'review_inputs': len(manifest), 'fresh_replay_audits': 31, 'compiled_semantic_mutants': 4, 'integrity_negatives': 5, 'verdict': 'accepted conditional component; full native refinement open'}))
