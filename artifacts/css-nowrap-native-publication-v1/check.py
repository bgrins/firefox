import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


negatives = []


def reject(name, fn):
    try:
        fn()
    except (AssertionError, RuntimeError, KeyError):
        negatives.append(name)
    else:
        raise AssertionError(name)


policy = read(HERE / 'POLICY.json')
assert policy['bindings'] is policy['pair_binding'] is policy['stage'] is policy['runtime_output'] is None
assert policy['enabled_modes'] == []
for path, pin in policy['references'].items():
    assert sha(ROOT / path) == pin, path
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
stage, = read(HERE / 'STAGES.json')['stages']
source, = stage['head_preimages']
test, = stage['adopt_existing_tests']
assert set(stage['files']) == {source, test}
assert source == 'dom/base/nsLineBreaker.cpp'
assert test == 'testing/web-platform/tests/css/css-text/white-space/nowrap-inline-break-policies.html'
for record in stage['files'].values():
    assert sha(ROOT / record['path']) == record['sha256']
capsule = ROOT / 'artifacts/css-nowrap-standalone-formatted-v1'
for name, record in read(capsule / 'FILES.json').items():
    assert sha(capsule / name) == record['sha256']

correction = ROOT / 'artifacts/css-nowrap-native-outcome-review-v1'
for name, record in read(correction / 'FILES.json').items():
    assert sha(correction / name) == record['sha256']

t = load('checked_transform', HERE / 'transform.py')
epoch = {
    'pins': {source: stage['head_preimages'][source], 'unrelated': 'untouched'},
    'staged_working': {}, 'committed_research_working_payloads': {},
    'installed_identities': {source: [1, 2], 'unrelated': [1, 3]},
    'semantic_index': {'head': 'synthetic-research', 'entries': 'same', 'working_diff': ''},
    'raw_index_observation': {'current': 'synthetic-before', 'historical': 'preserve'},
    'modified_native_paths': [], 'counts': {'native_modified_paths': 0, 'roles': 2, 'installed_identities': 2},
    'prototype_overlay_state': {'installed': False, 'retired_by': 'earlier-publication'},
    'registered_color_image_publication': {'image': {'native_commit': 'earlier-image'}},
    'registered_number_transition': {'role': 'published-native'},
    'accepted_fix_count': 149, 'accepted_records': ['historical'],
    'canonical_application': {'built': False, 'sha256': 'restored-old-app'},
    'untracked_native': ['unrelated-native'], 'nested_semantic_index': {'head': 'nested'},
}
owned = {'unrelated': {'identity': [1, 3]}}
role = {'built': False, 'variant': 'registered-image', 'last_build': 'obsolete', 'last_install': 'obsolete'}
original = copy.deepcopy((epoch, owned, role))
claims = {name: {'path': name, 'identity': [1, 2 if name == source else 4], 'owned_sha256': record['sha256']} for name, record in stage['files'].items()}
semantic = dict(epoch['semantic_index'], working_diff='synthetic-nowrap-diff')
current, new_owned, new_role = t.installed(epoch, owned, role, stage, claims, {'raw_index': 'synthetic-install'}, semantic, 'synthetic-manifest', 'synthetic-runtime')
assert (epoch, owned, role) == original
assert current['modified_native_paths'] == [source]
assert new_role['variant'] == 'nowrap' and new_role['built'] is False
assert 'last_build' not in new_role and 'last_install' not in new_role
assert new_role['paired_head'] == 'synthetic-research'
allowed = {'pins', 'installed_identities', 'semantic_index', 'raw_index_observation', 'modified_native_paths', 'counts', 'nowrap_publication', 'registered_number_transition'}
assert {k: v for k, v in current.items() if k not in allowed} == {k: v for k, v in epoch.items() if k not in allowed}
assert current['pins']['unrelated'] == 'untouched' and new_owned['unrelated'] == owned['unrelated']
assert current['installed_identities'][test] == claims[test]['identity'] and new_owned[test] == claims[test]
for name in stage['files']:
    bad = copy.deepcopy(claims)
    bad[name]['owned_sha256'] = 'wrong'
    reject('wrong postimage claim: ' + name, lambda: t.installed(epoch, owned, role, stage, bad, {}, semantic, 'synthetic', 'synthetic'))
final = t.committed(current, 'nowrap', {'raw_index': 'synthetic-committed'}, dict(semantic, head='synthetic-commit', working_diff=''), 'synthetic-commit')
assert final['modified_native_paths'] == [] and final['counts']['native_modified_paths'] == 0
assert final['nowrap_publication']['nowrap']['native_commit'] == 'synthetic-commit'
assert final['registered_number_transition']['paired_head'] == 'synthetic-commit'
assert final['pins'] == current['pins'] and final['installed_identities'] == current['installed_identities']
for name in ('prototype_overlay_state', 'registered_color_image_publication', 'accepted_fix_count', 'accepted_records', 'canonical_application', 'nested_semantic_index', 'untracked_native'):
    assert final[name] == epoch[name]

owner = load('checked_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
parents = load('checked_parents', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
delivery = load('checked_delivery', HERE / 'delivery.py')
with tempfile.TemporaryDirectory(prefix='nowrap-publication-check-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    target = scratch / test
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / stage['files'][test]['path']).read_bytes())
    before = target.read_bytes(), target.stat().st_ino
    claim = owner.claim(scratch, test, stage['files'][test]['sha256'])
    parent_claims = parents.parent_pins(scratch, target)
    assert owner.claim(scratch, test, claim['owned_sha256'], claim['identity']) == claim
    assert parents.parent_pins(scratch, target) == parent_claims
    reject('wrong adopted identity', lambda: owner.claim(scratch, test, claim['owned_sha256'], [0, 0]))
    reject('wrong adopted bytes', lambda: owner.claim(scratch, test, 'wrong', claim['identity']))
    delivery.ROOT = scratch
    body = target.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
    manifest = {'items': {'testharness': {'css': {'css-text': {'white-space': {target.name: [blob, [None, {}]]}}}}}}
    files = {test: stage['files'][test]['sha256']}
    assert delivery.verify_entries(manifest, scratch / 'testing/web-platform/tests', files) == ['/css/css-text/white-space/nowrap-inline-break-policies.html']
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['css']['css-text']['white-space'][target.name][0] = 'wrong'
    reject('wrong genuine manifest blob', lambda: delivery.verify_entries(bad, scratch / 'testing/web-platform/tests', files))
    reject('missing genuine manifest entry', lambda: delivery.verify_entries({'items': {'testharness': {'css': {'css-text': {'white-space': {}}}}}}, scratch / 'testing/web-platform/tests', files))
    assert (target.read_bytes(), target.stat().st_ino) == before
assert not scratch.exists()
evidence = load('checked_evidence', HERE / 'evidence.py')
reject('pending actual pair cannot authorize publication', lambda: evidence.verify(ROOT, None, stage))

predecessor = ROOT / 'artifacts/css-registered-color-image-native-publication-v1'
for name in ('run.py', 'publish.py', 'transform.py', 'delivery.py'):
    expected = ''.join(difflib.unified_diff((predecessor / name).read_text().splitlines(True), (HERE / name).read_text().splitlines(True), fromfile='executed/' + name, tofile='nowrap/' + name))
    assert (HERE / (name + '.diff')).read_text() == expected
tree = ast.parse((HERE / 'run.py').read_text())
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
assert not any(isinstance(n.func, ast.Attribute) and n.func.attr in ('create_file', 'unlink', 'remove', 'rmtree') for n in calls)
assert "assert {path.encode() for path in tests} <= set(untracked.split(b'\\0'))" in (HERE / 'run.py').read_text()
assert "for name in ('run.py', 'transform.py', 'evidence.py', 'STAGES.json')" in (HERE / 'publish.py').read_text()
print(json.dumps({'references': len(policy['references']), 'pure_install_commit_transforms': 2, 'negative_controls': negatives, 'adopted_scratch_bytes_and_identity_unchanged': True, 'scratch_removed': True, 'exact_predecessor_deltas': 4, 'actual_pair_evidence': 'pending frozen runtime', 'native_git_browser_actions': False}, sort_keys=True))
