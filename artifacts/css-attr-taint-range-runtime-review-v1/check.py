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
r = read('candidate/RESULT.json')
b = read('baseline/RUN.json')
prior = read('prior82/PAIR.json')
assert digest(root / 'baseline/RUN.json') == r['baseline_receipt_sha256']
assert digest(root / 'prior82/PAIR.json') == r['prior_82_pair_sha256']
assert digest(root / 'run-candidate.py') == r['driver_sha256']
assert digest(root / 'prior82/raw.json') == prior['phases'][-1]['raw_sha256']
def events(name):
    return [json.loads(line, object_pairs_hook=unique) for line in (root / name).read_text().splitlines()]
def rows(name):
    return [e for e in events(name) if e.get('action') == 'test_status']
x, y, z = rows('candidate/raw.json'), rows('baseline/raw.json'), rows('prior82/raw.json')
assert x == r['rows'] and y == b['rows'] and (len(x),len(y),len(z)) == (89,7,82)
key = lambda e: (e['test'],e['subtest'])
old, new = {key(e):e for e in y+z}, {key(e):e for e in x}
assert len(old) == len(new) == 89 and old.keys() == new.keys()
changes = [{'test':k[0],'subtest':k[1],'before':old[k]['status'],'after':new[k]['status']} for k in old if old[k]['status'] != new[k]['status']]
assert changes == read('COMPARISON.json')['improvements']
assert [c['subtest'] for c in changes] == ['Touching untainted URL and attr resolution','Touching URL function and attr resolution']
assert all(c['before']=='FAIL' and c['after']=='PASS' for c in changes)
assert all(e['status']=='PASS' for e in x)
cp, op = r['candidate_pins'],r['original_pins']
assert cp.keys() == op.keys()
assert [n for n in op if op[n] != cp[n]] == ['servo/components/style/custom_properties.rs']
for variant,pins in [('original',op),('candidate',cp)]:
    assert digest(root / 'native' / (variant+'.rs')) == pins['servo/components/style/custom_properties.rs']
a=(root / 'native/original.rs').read_text()
c=(root / 'native/candidate.rs').read_text()
before='.any(|r| r.start <= range.end && r.end >= range.start)'
after='.any(|r| r.start.max(range.start) < r.end.min(range.end))'
assert a.count(before)==1 and a.replace(before,after)==c
assert prior['stable_pins'] | prior['source_pins']['candidate'] | {'testing/web-platform/tests/css/css-values/attr-taint-touching-url-boundary.html':digest(root/'test.html')} == op
assert digest(root/'test.html') == '6b29bcb18f02123f74ff715bf3873943b902d6209b99edc946ac45632247a32a'
assert r['build']['exit']==r['wpt']['exit']==0 and r['complete'] and r['source_stable_after'] and r['binary_stable_after'] and r['build']['sources_stable']
assert prior['complete'] and prior['candidate_binary_validated'] and prior['phases'][-1]['exit']==0
assert prior['final_binaries']==r['baseline_binaries']==prior['phases'][-1]['binaries_after']==prior['phases'][-1]['binaries_before']
for n,v in b['pins'].items():
    if n in op: assert op[n]==v
for n,v in r['baseline_binaries'].items():
    assert b['pins']['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/'+n]==v
    assert r['candidate_binaries'][n] != v
assert b['stable_after'] and b['exit']==1
raw=events('candidate/raw.json')
ends=[e for e in raw if e.get('action')=='test_end']
assert ends==r['harness'] and len(ends)==10 and all(e['status']=='OK' for e in ends)
suite=[i for i,e in enumerate(raw) if e.get('action')=='suite_end']
assert len(suite)==1 and suite==r['suite_end_positions']
assert all(i<suite[0] for i,e in enumerate(raw) if e.get('action') in ['test_status','test_end'])
assert (root/'candidate/build.log').read_text().count("KeyError: 'export'")==4
assert 'Your build was successful!' in (root/'candidate/build.log').read_text()
print(json.dumps({'review_inputs':len(manifest),'subtests':89,'harnesses_ok':10,'improvements':2,'unchanged_pass':87,'source_delta_files':1,'build_exit':0,'runtime_review':'accepted captured local pair','upstream_runtime':'not executed'}))
