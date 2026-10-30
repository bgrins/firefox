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
tests = set(stage['adopt_existing_tests'])
created_test, = stage['create_tests']
assert len(tests)==2 and created_test not in tests
assert set(stage['files']) == {source, created_test} | tests
test = sorted(tests)[0]
assert source == 'dom/base/nsLineBreaker.cpp'
assert tests == {'testing/web-platform/tests/css/css-text/line-break/line-break-language-latin1-partitions.html','testing/web-platform/tests/css/css-text/line-break/line-break-language-text-partitions.html'}
assert created_test == 'testing/web-platform/tests/css/css-text/line-break/line-break-unknown-language-context.html'
for record in stage['files'].values():
    assert sha(ROOT / record['path']) == record['sha256']
capsule = ROOT / 'artifacts/css-language-partition-formatted-v1'
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
    'nowrap_publication': {'nowrap': {'native_commit': 'already-published-nowrap'}},
    'registered_number_transition': {'role': 'published-native'},
    'accepted_fix_count': 149, 'accepted_records': ['historical'],
    'canonical_application': {'built': False, 'sha256': 'restored-old-app'},
    'untracked_native': ['unrelated-native'], 'nested_semantic_index': {'head': 'nested'},
}
owned = {'unrelated': {'identity': [1, 3]}}
role = {'built': False, 'variant': 'nowrap', 'last_build': 'obsolete', 'last_install': 'obsolete'}
original = copy.deepcopy((epoch, owned, role))
claims = {name: {'path': name, 'identity': [1, 2 if name == source else 4], 'owned_sha256': record['sha256']} for name, record in stage['files'].items()}
semantic = dict(epoch['semantic_index'], working_diff='synthetic-nowrap-diff')
current, new_owned, new_role = t.installed(epoch, owned, role, stage, claims, {'raw_index': 'synthetic-install'}, semantic, 'synthetic-manifest', 'synthetic-runtime')
assert (epoch, owned, role) == original
assert current['modified_native_paths'] == [source]
assert new_role['variant'] == 'language' and new_role['built'] is False
assert 'last_build' not in new_role and 'last_install' not in new_role
assert new_role['paired_head'] == 'synthetic-research'
allowed = {'pins', 'installed_identities', 'semantic_index', 'raw_index_observation', 'modified_native_paths', 'counts', 'language_partition_publication', 'registered_number_transition'}
assert {k: v for k, v in current.items() if k not in allowed} == {k: v for k, v in epoch.items() if k not in allowed}
assert current['pins']['unrelated'] == 'untouched' and new_owned['unrelated'] == owned['unrelated']
assert current['installed_identities'][test] == claims[test]['identity'] and new_owned[test] == claims[test]
for name in stage['files']:
    bad = copy.deepcopy(claims)
    bad[name]['owned_sha256'] = 'wrong'
    reject('wrong postimage claim: ' + name, lambda: t.installed(epoch, owned, role, stage, bad, {}, semantic, 'synthetic', 'synthetic'))
final = t.committed(current, 'language', {'raw_index': 'synthetic-committed'}, dict(semantic, head='synthetic-commit', working_diff=''), 'synthetic-commit')
assert final['modified_native_paths'] == [] and final['counts']['native_modified_paths'] == 0
assert final['language_partition_publication']['language']['native_commit'] == 'synthetic-commit'
assert final['registered_number_transition']['paired_head'] == 'synthetic-commit'
assert final['pins'] == current['pins'] and final['installed_identities'] == current['installed_identities']
for name in ('prototype_overlay_state', 'registered_color_image_publication', 'nowrap_publication', 'accepted_fix_count', 'accepted_records', 'canonical_application', 'nested_semantic_index', 'untracked_native'):
    assert final[name] == epoch[name]

owner = load('checked_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
parents = load('checked_parents', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
delivery = load('checked_delivery', HERE / 'delivery.py')
with tempfile.TemporaryDirectory(prefix='language-publication-check-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    before = {}
    for test in sorted(tests):
        target = scratch / test
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / stage['files'][test]['path']).read_bytes())
        before[test] = target.read_bytes(), target.stat().st_ino
        claim = owner.claim(scratch, test, stage['files'][test]['sha256'])
        parent_claims = parents.parent_pins(scratch, target)
        assert owner.claim(scratch, test, claim['owned_sha256'], claim['identity']) == claim
        assert parents.parent_pins(scratch, target) == parent_claims
        reject('wrong adopted identity: '+test, lambda: owner.claim(scratch, test, claim['owned_sha256'], [0, 0]))
        reject('wrong adopted bytes: '+test, lambda: owner.claim(scratch, test, 'wrong', claim['identity']))
    new_path = scratch / created_test
    parent_claims = parents.parent_pins(scratch, new_path)
    created = parents.create_owned(owner, scratch, created_test, parent_claims)
    owner.write_owned(scratch, created, (ROOT / stage['files'][created_test]['path']).read_bytes())
    try:
        parents.create_owned(owner, scratch, created_test, parent_claims)
    except FileExistsError:
        negatives.append('exclusive creation refuses existing file')
    else:
        raise AssertionError('exclusive creation replaced existing file')
    reject('foreign identity cannot authorize rollback', lambda: owner.claim(scratch, created_test, created['owned_sha256'], [0,0]))
    delivery.ROOT = scratch
    tree = {}
    for test in sorted(tests | {created_test}):
        body = (scratch/test).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        tree[Path(test).name] = [blob, [None, {}]]
    manifest = {'items': {'testharness': {'css': {'css-text': {'line-break': tree}}}}}
    files = {test:stage['files'][test]['sha256'] for test in tests | {created_test}}
    assert delivery.verify_entries(manifest, scratch/'testing/web-platform/tests', files) == sorted('/'+test.removeprefix('testing/web-platform/tests/') for test in files)
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['css']['css-text']['line-break'][Path(created_test).name][0] = 'wrong'
    reject('wrong genuine manifest blob', lambda: delivery.verify_entries(bad, scratch/'testing/web-platform/tests', files))
    owner.claim(scratch, created_test, created['owned_sha256'], created['identity'])
    assert parents.parent_pins(scratch, new_path) == parent_claims
    new_path.unlink()
    assert not new_path.exists()
    assert all(((scratch/test).read_bytes(), (scratch/test).stat().st_ino) == record for test,record in before.items())
assert not scratch.exists()
evidence = load('checked_evidence', HERE / 'evidence.py')
reject('pending actual pair cannot authorize publication', lambda: evidence.verify(ROOT, None, stage))

predecessor = ROOT / 'artifacts/css-nowrap-native-publication-v1'
for name in ('run.py', 'publish.py', 'transform.py', 'delivery.py', 'evidence.py'):
    expected = ''.join(difflib.unified_diff((predecessor/name).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile='executed/'+name, tofile='language/'+name))
    assert (HERE/(name+'.diff')).read_text() == expected
old, new = (predecessor/'run.py').read_text(), (HERE/'run.py').read_text()
start = '            with tempfile.TemporaryDirectory('
end = '    except BaseException as error:'
assert new[new.index(start):new.index(end)] == old[old.index(start):old.index(end)].replace('css-nowrap-native-', 'css-language-partition-native-')
assert (HERE/'delivery.py').read_text() == (predecessor/'delivery.py').read_text().replace("['white-space']","['line-break']")
assert "for name in ('run.py', 'transform.py', 'evidence.py', 'STAGES.json')" in (HERE/'publish.py').read_text()
print(json.dumps({'references':len(policy['references']), 'pure_install_commit_transforms':2,
                  'negative_controls':negatives, 'adopted_scratch_bytes_and_identity_unchanged':True,
                  'exclusive_new_test_creation_and_owned_rollback':True, 'scratch_removed':True,
                  'signing_tail_preserved':True, 'actual_pair_evidence':'pending terminal and independent live audit',
                  'native_git_browser_actions':False}, sort_keys=True))
