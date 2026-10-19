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
pins = read(ROOT / 'ROOT-INPUT-PINS.json')
source = 'servo/components/style/properties/cascade.rs'
assert digest(ROOT / 'candidate' / source) == pins[source]
packaging = read(ROOT / 'runtime/STANDALONE-PACKAGING.json')
assert packaging['exact_files'] == [source, 'testing/web-platform/tests/css/css-properties-values-api/registered-inherit-invalid.html']
assert digest(ROOT / 'runtime/final.patch') == packaging['patch_sha256'] == 'f2bc94413f3fbfccee03b4619369f64ed4f8440991a8cbb26cdd0084f872c07e'
assert all(row['apply'] == row['reverse'] == 'PASS' for row in packaging['bases'])
assert read(ROOT / 'FINAL-STANDALONE.json')['exact_source_and_wpt_match']
assert digest(ROOT / 'native.patch') == 'd08c62e54edce722675ec7c7f1edcf6ad05aa652fa0c867a1321ae3be74a3359'
assert digest(ROOT / 'test.html') == '24e78978243100995c46138fdae4a4844637046cf397002d99e8c7d1d9c216aa'
assert digest(ROOT / 'readiness-controls.html') == '21be1691a7a3a055c4f4883afd83ff3be1cf97d5625793aaab924ada21699c89'
a = (ROOT / 'source' / source).read_text()
anchor = """                                inherited_value,
                            );
                        }
                    },
                    // handled in value_may_affect_style"""
replacement = """                                inherited_value,
                            );
                        } else {
                            context
                                .builder
                                .substitution_functions
                                .remove_var(registration, name);
                        }
                    },
                    // handled in value_may_affect_style"""
old = """                        // existing_value is the registered initial value.
                        // Don't bother adding it to self.custom_properties.non_inherited
                        // if the key is also absent from self.inherited.non_inherited.
                        if context
                            .inherited_custom_properties()
                            .non_inherited
                            .get(name)
                            .is_none()
                        {"""
new = """                        // Root inheritance uses the already-seeded initial value.
                        if context.is_root_element() {"""
for left,right in [(anchor,replacement),(old,new)]:
    assert a.count(left) == 1
    a = a.replace(left,right)
assert a == (ROOT / 'candidate' / source).read_text()
b = (ROOT / 'upstream' / source).read_text()
for left,right in [(anchor,replacement),(old,new)]:
    assert b.count(left) == 1
    b = b.replace(left,right)
assert b == (ROOT / 'upstream-patched.rs').read_text()
standalone = read(ROOT / 'STANDALONE.json')
assert standalone['reverse_exact'] and not standalone['isolated_base_build_or_browser']
assert all(r['exit'] == 0 for r in standalone['actions'])
runtime = ROOT / 'runtime'
pair = read(runtime / 'FINAL-PAIR.json')
assert pair['candidate_sources_restored']
assert [r['variant'] for r in pair['runs']] == ['baseline','candidate']
assert [r['test_exit'] for r in pair['runs']] == [1,0]
for run in pair['runs']:
    assert run['build_exit'] == 0 and run['stable_after']
    assert set(run['sources']) == {source} and len(run['binaries']) == 2
    directory = 'source' if run['variant'] == 'baseline' else 'candidate'
    assert digest(ROOT / directory / source) == run['sources'][source]
assert pair['runs'][0]['tests'] == pair['runs'][1]['tests']
testfiles = {
    'registered-inherit-invalid.html': ROOT / 'test.html',
    'registered-defaulting-readiness-controls.html': ROOT / 'readiness-controls.html',
    **{n: ROOT / 'tests' / n for n in ['registered-initial-computed-value.html','registered-properties-inheritance.html','var-reference-registered-properties-cycles.html']}}
for name,path in testfiles.items():
    assert pair['stable_sources']['testing/web-platform/tests/css/css-properties-values-api/'+name] == digest(path)
prefix = '/css/css-properties-values-api/'
counts = {'registered-inherit-invalid.html':12,'registered-defaulting-readiness-controls.html':3,'registered-initial-computed-value.html':12,'registered-properties-inheritance.html':8,'var-reference-registered-properties-cycles.html':5}
failures = {'missing parent, direct inherit','cyclic parent, direct inherit','Explicit inheritance follows parent changes to and from invalid values'}
new_names = {
    'missing parent, direct inherit','cyclic parent, direct inherit',
    'missing parent, substituted inherit','missing parent, direct unset',
    'missing parent, substituted unset','inherited property, direct inherit',
    'inherited property, substituted unset','present parent, direct inherit',
    'typed reset invalid value','typed inherited invalid value',
    'Root explicit inherit uses the registered initial value',
    'Explicit inheritance follows parent changes to and from invalid values'}
observed = {}
for variant in ['baseline','candidate']:
    events = [json.loads(line, object_pairs_hook=unique) for line in (runtime / f'final-{variant}-raw.json').read_text().splitlines()]
    ends = [r for r in events if r.get('action')=='test_end']
    assert len(ends)==5 and {r['test'] for r in ends} == {prefix+n for n in counts}
    assert all(r['status']=='OK' for r in ends)
    assert sum(r.get('action')=='suite_end' for r in events)==1
    assert events.index(next(r for r in events if r.get('action')=='suite_end')) > max(events.index(r) for r in ends)
    rows = [r for r in events if r.get('action')=='test_status']
    assert len(rows)==40
    assert {r['subtest'] for r in rows if r['test']==prefix+'registered-inherit-invalid.html'}==new_names
    assert len({(r['test'],r['subtest']) for r in rows})==40
    observed[variant] = {(r['test'],r['subtest']): (r['status'],r.get('expected',r['status']),r.get('message')) for r in rows}
    for name,count_expected in counts.items():
        assert sum(r['test']==prefix+name for r in rows)==count_expected
    for row in rows:
        failed = variant=='baseline' and row['test']==prefix+'registered-inherit-invalid.html' and row['subtest'] in failures
        assert row['status']==('FAIL' if failed else 'PASS')
        assert row.get('expected',row['status'])=='PASS'
assert observed['baseline'].keys()==observed['candidate'].keys()
changed = [key for key in observed['baseline'] if observed['baseline'][key]!=observed['candidate'][key]]
assert {k[1] for k in changed}==failures and len(changed)==3
assert authenticate()==count
print(json.dumps({'status':'PASS','verdict':'ACCEPT_BOUNDED_NATIVE_REPAIR','inputs':count,'new_baseline':'3FAIL/9PASS','new_candidate':'12PASS','adjacent_and_readiness':'28PASS unchanged','harnesses':5,'reviewer_browser_executions':0,'standalone_source_apply_reverse':True,'isolated_upstream_runtime':False}))
