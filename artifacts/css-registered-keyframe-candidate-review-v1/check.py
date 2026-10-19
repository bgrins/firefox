from pathlib import Path
import hashlib
import json
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).absolute().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('duplicate key', key)
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate():
    assert not ROOT.is_symlink()
    freeze = read(ROOT / 'FREEZE.json')
    assert digest(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    assert digest(ROOT / 'check.py') == freeze['checker_sha256']
    manifest = read(ROOT / 'MANIFEST.json')
    expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    files, dirs = set(), set()
    for path in ROOT.rglob('*'):
        assert not path.is_symlink(), path
        assert path.is_file() or path.is_dir(), path
        (files if path.is_file() else dirs).add(str(path.relative_to(ROOT)))
    assert files == expected, ('roster', files ^ expected)
    assert dirs == {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    for name, pin in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and str(path) == name
        assert (ROOT / path).resolve().is_relative_to(ROOT.resolve())
        assert digest(ROOT / path) == pin, name
    return len(manifest)

count = authenticate()
auth = read(ROOT / 'evidence/AUTHENTICATION.json')
for name, pin in auth['candidate'].items():
    assert digest(ROOT / 'candidate' / name) == pin
assert digest(ROOT / 'evidence/fix.patch') == auth['patch_sha256']
assert digest(ROOT / 'static/FREEZE.json') == auth['static_freeze_sha256']
assert digest(ROOT / 'static/MANIFEST.json') == auth['static_manifest_sha256']
for name, pin in read(ROOT / 'static/MANIFEST.json').items():
    assert digest(ROOT / 'static' / name) == pin
runtime = ROOT / 'evidence/runtime'
for name, pin in read(runtime / 'PINS.json').items():
    assert digest(runtime / name) == pin
pair = read(runtime / 'FINAL-PAIR.json')
assert pair['candidate_sources_restored']
assert [r['variant'] for r in pair['runs']] == ['baseline', 'candidate']
assert [r['test_exit'] for r in pair['runs']] == [1, 0]
for run in pair['runs']:
    assert run['build_exit'] == 0 and run['stable_after']
    assert len(run['sources']) == 2 and len(run['binaries']) == 2
    for name, pin in run['sources'].items():
        directory = 'original' if run['variant'] == 'baseline' else 'candidate'
        assert digest(ROOT / directory / name) == pin
assert pair['runs'][0]['tests'] == pair['runs'][1]['tests']
new = '/css/css-properties-values-api/registered-keyframe-substitution-interpolation.html'
new_names = ['Registered number interpolation: ' + n for n in [
    'literal control', 'attribute end value', 'attribute start value',
    'attribute fallback', 'variable end value', 'calculation end value control']]
new_names += [f'{p} interpolates {v} independently of the base value'
              for p in ['--keyframe-number', '--keyframe-inherited']
              for v in ['initial', 'unset', 'inherit', 'invalid', 'var(--missing)']]
failed = {new_names[i] for i in [1,2,3,4,9,10,14,15]}
number = '/css/css-properties-values-api/animation/custom-property-animation-number.html'
cross = '/css/css-properties-values-api/animation/registered-var-to-registered-animating.html'
security = '/css/css-values/attr-security-transition.html'
old_names = [
    'Animating a custom property of type <number>',
    'Animating a custom property of type <number> with a single keyframe',
    'Animating a custom property of type <number> with additivity',
    'Animating a custom property of type <number> with a single keyframe and additivity',
    'Animating a custom property of type <number> with iterationComposite']
cross_name = 'Animated registered custom properties can var() reference other animated registered custom properties across separate Animations.'
expected_keys = {(new, n) for n in new_names} | {(number, n) for n in old_names} | {
    (cross, cross_name), (security, 'background-image value should be attr-tainted')}
observations = read(runtime / 'OBSERVATIONS.json')
for variant in ['baseline', 'candidate']:
    events = [json.loads(l, object_pairs_hook=unique) for l in (runtime / f'final-{variant}-raw.json').read_text().splitlines()]
    ends = [r for r in events if r.get('action') == 'test_end']
    assert len(ends) == 4 and {r['test'] for r in ends} == {new, number, cross, security}
    assert all(r['status'] == 'OK' for r in ends)
    assert sum(r.get('action') == 'suite_end' for r in events) == 1
    assert events.index(next(r for r in events if r.get('action') == 'suite_end')) > max(events.index(r) for r in ends)
    rows = [r for r in events if r.get('action') == 'test_status']
    assert len(rows) == 23 and {(r['test'],r['subtest']) for r in rows} == expected_keys
    for row in rows:
        status = 'FAIL' if row['test'] == cross or (variant == 'baseline' and row['test'] == new and row['subtest'] in failed) else 'PASS'
        expectation = 'FAIL' if row['test'] == cross else 'PASS'
        assert row['status'] == status and row.get('expected',row['status']) == expectation
        if row['test'] == cross:
            message = ('assert_equals: target at 25%, to at 25% expected "131.25" but got "100"' if variant == 'baseline' else 'assert_equals: target at 25%, to at 25% expected "143.75" but got "131.25"')
            assert row['message'] == message
    summarized = [{'test':r['test'],'subtest':r['subtest'],'status':r['status'],'expected':r.get('expected',r['status']),'message':r.get('message')} for r in rows]
    assert observations[variant] == summarized
assert authenticate() == count
print(json.dumps({'status':'PASS','verdict':'ACCEPT_BOUNDED_SOURCE_WPT_REPAIR','inputs':count,'new_baseline_fail':8,'new_candidate_pass':16,'adjacent_statuses':'6PASS+1expectedFAIL','adjacent_diagnostic_changed':True,'reviewer_browser_executions':0}))
