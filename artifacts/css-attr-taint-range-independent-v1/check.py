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
assert result['audits'] == 14 and all(c['exit'] == 0 for c in result['commands'])
assert result['observations'] == {'original':['441 146','[true, true, true, true, true]'], 'candidate':['441 0','[true, false, false, false, false]']}
mutant = read('receipts/replay/MUTANT.json')
assert mutant['compile_exit'] == 0 and mutant['run_exit'] == 0
assert mutant['output'].splitlines() == ['441 40','[true, false, false, false, false]']
guards = read('receipts/GUARDS.json')
assert len(guards) == 6 and all(g['exit'] != 0 and g['output_absent'] for g in guards)
assert read('PRODUCER.json')['inputs_post_replay'] == 10
for name, pin in read('SOURCE-PINS.json').items():
    assert digest(root / name) == pin['sha256']
assert digest(root / 'root-baseline/test.html') == '6b29bcb18f02123f74ff715bf3873943b902d6209b99edc946ac45632247a32a'
raw = [json.loads(line, object_pairs_hook=unique) for line in (root / 'root-baseline/raw.json').read_text().splitlines()]
rows = [r for r in raw if r.get('action') == 'test_status']
assert [r['status'] for r in rows] == ['FAIL','FAIL','PASS','PASS','PASS','PASS','PASS']
assert [r['status'] for r in raw if r.get('action') == 'test_end'] == ['OK']
print(json.dumps({'review_inputs':len(manifest),'audits':14,'native_pairs':441,'original_mismatches':146,'candidate_mismatches':0,'independent_strict_mutant_mismatches':40,'integrity_negatives':6,'root_browser_baseline':'2 FAIL, 5 PASS, 1 OK','verdict':'source and bounded interval component accepted; candidate browser acceptance separate'}))
