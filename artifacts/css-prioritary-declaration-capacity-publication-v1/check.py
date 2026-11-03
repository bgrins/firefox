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
sources = set(stage['head_preimages'])
source = sorted(sources)[0]
tests = set(stage['create_tests'])
assert len(tests) == 1 and stage['adopt_existing_tests'] == []
assert sources == {'servo/components/style/properties/cascade.rs'}
assert set(stage['files']) == sources | tests
assert tests == {'testing/web-platform/tests/css/css-cascade/prioritary-after-many-unrelated-declarations.html'}
test, = tests
for record in stage['files'].values():
    assert sha(ROOT / record['path']) == record['sha256']
capsule = ROOT / 'artifacts/css-prioritary-declaration-capacity-inputs-v1'
for name, record in read(capsule / 'FILES.json').items():
    assert sha(capsule / name) == record['sha256']
base = ROOT / 'artifacts/css-font-metric-synthesis-producer-v1/base/servo/components/style/properties/cascade.rs'
assert (ROOT / stage['files'][source]['path']).read_bytes() == base.read_bytes().replace(b'type DeclarationIndex = u16;', b'type DeclarationIndex = u32;')

t = load('checked_transform', HERE / 'transform.py')
epoch = {
    'pins': dict(stage['head_preimages'], unrelated='untouched'),
    'staged_working': {}, 'committed_research_working_payloads': {},
    'installed_identities': {**{n:[1,i+2] for i,n in enumerate(sorted(sources))}, 'unrelated':[1,10]},
    'semantic_index': {'head': 'synthetic-research', 'entries': 'same', 'working_diff': ''},
    'raw_index_observation': {'current': 'synthetic-before', 'historical': 'preserve'},
    'modified_native_paths': [], 'counts': {'native_modified_paths': 0, 'roles': 2, 'installed_identities': 2},
    'prototype_overlay_state': {'installed': False, 'retired_by': 'earlier-publication'},
    'registered_color_image_publication': {'image': {'native_commit': 'earlier-image'}},
    'nowrap_publication': {'nowrap': {'native_commit': 'already-published-nowrap'}},
    'language_partition_publication': {'language': {'native_commit': 'already-published-language'}},
    'hyphenation_ownership_publication': {'ownership': {'native_commit': 'already-published-ownership'}},
    'registered_number_transition': {'role': 'published-native'},
    'accepted_fix_count': 149, 'accepted_records': ['historical'],
    'canonical_application': {'built': False, 'sha256': 'restored-old-app'},
    'untracked_native': ['unrelated-native'], 'nested_semantic_index': {'head': 'nested'},
}
owned = {'unrelated': {'identity': [1, 3]}}
role = {'built': False, 'variant': 'language', 'last_build': 'obsolete', 'last_install': 'obsolete'}
original = copy.deepcopy((epoch, owned, role))
claims = {name: {'path': name, 'identity': [1, 2 if name == source else 4], 'owned_sha256': record['sha256']} for name, record in stage['files'].items()}
semantic = dict(epoch['semantic_index'], working_diff='synthetic-ownership-diff')
current, new_owned, new_role = t.installed(epoch, owned, role, stage, claims, {'raw_index': 'synthetic-install'}, semantic, 'synthetic-manifest', 'synthetic-runtime')
assert (epoch, owned, role) == original
assert current['modified_native_paths'] == sorted(sources)
assert new_role['variant'] == 'capacity' and new_role['built'] is False
assert 'last_build' not in new_role and 'last_install' not in new_role
assert new_role['paired_head'] == 'synthetic-research'
allowed = {'pins', 'installed_identities', 'semantic_index', 'raw_index_observation', 'modified_native_paths', 'counts', 'prioritary_declaration_capacity_publication', 'registered_number_transition'}
assert {k: v for k, v in current.items() if k not in allowed} == {k: v for k, v in epoch.items() if k not in allowed}
assert current['pins']['unrelated'] == 'untouched' and new_owned['unrelated'] == owned['unrelated']
assert current['installed_identities'][test] == claims[test]['identity'] and new_owned[test] == claims[test]
for name in stage['files']:
    bad = copy.deepcopy(claims)
    bad[name]['owned_sha256'] = 'wrong'
    reject('wrong postimage claim: ' + name, lambda: t.installed(epoch, owned, role, stage, bad, {}, semantic, 'synthetic', 'synthetic'))
final = t.committed(current, 'capacity', {'raw_index': 'synthetic-committed'}, dict(semantic, head='synthetic-commit', working_diff=''), 'synthetic-commit')
assert final['modified_native_paths'] == [] and final['counts']['native_modified_paths'] == 0
assert final['prioritary_declaration_capacity_publication']['capacity']['native_commit'] == 'synthetic-commit'
assert final['registered_number_transition']['paired_head'] == 'synthetic-commit'
assert final['pins'] == current['pins'] and final['installed_identities'] == current['installed_identities']
for name in ('prototype_overlay_state', 'registered_color_image_publication', 'nowrap_publication', 'language_partition_publication', 'hyphenation_ownership_publication', 'accepted_fix_count', 'accepted_records', 'canonical_application', 'nested_semantic_index', 'untracked_native'):
    assert final[name] == epoch[name]

owner = load('checked_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
parents = load('checked_parents', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
delivery = load('checked_delivery', HERE / 'delivery.py')
with tempfile.TemporaryDirectory(prefix='capacity-publication-check-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    target = scratch / test
    target.parent.mkdir(parents=True)
    parent_claims = parents.parent_pins(scratch, target)
    created = parents.create_owned(owner, scratch, test, parent_claims)
    owner.write_owned(scratch, created, (ROOT / stage['files'][test]['path']).read_bytes())
    try:
        parents.create_owned(owner, scratch, test, parent_claims)
    except FileExistsError:
        negatives.append('exclusive creation refuses existing file')
    else:
        raise AssertionError('exclusive creation replaced an existing file')
    reject('foreign identity cannot authorize rollback', lambda: owner.claim(scratch, test, created['owned_sha256'], [0, 0]))
    delivery.ROOT = scratch
    body = target.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
    tree = {target.name: [blob, [None, {}]]}
    manifest = {'items': {'testharness': {'css': {'css-cascade': tree}}}}
    files = {test: stage['files'][test]['sha256']}
    assert delivery.verify_entries(manifest, scratch/'testing/web-platform/tests', files) == ['/css/css-cascade/'+target.name]
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['css']['css-cascade'][target.name][0] = 'wrong'
    reject('wrong manifest blob', lambda: delivery.verify_entries(bad, scratch/'testing/web-platform/tests', files))
    owner.claim(scratch, test, created['owned_sha256'], created['identity'])
    assert parents.parent_pins(scratch, target) == parent_claims
    target.unlink()
    assert not target.exists()
assert not scratch.exists()
evidence = load('checked_evidence', HERE / 'evidence.py')
reject('pending actual pair cannot authorize publication', lambda: evidence.verify(ROOT, None, stage))
page = '/css/css-cascade/prioritary-after-many-unrelated-declarations.html'
name = 'Font-size survives 65536 higher-priority declarations for another property'
observation = {'rules':65538,'early':{'fontSize':'16px','width':'16px','color':'rgb(1, 2, 3)'},'late':{'fontSize':'37px','width':'37px','color':'rgb(1, 2, 3)'}}
def message(obs): return 'assert_equals: '+json.dumps(obs, separators=(',', ':'))+' expected "37px" but got "16px"'
original = {'complete':True,'rows':[{'test':page,'subtest':name,'status':'FAIL','message':message(observation)}], 'ends':[{'status':'OK'}]}
candidate = {'complete':True,'rows':[{'test':page,'subtest':name,'status':'PASS','message':None}], 'ends':[{'status':'OK'}], 'comparison_errors':[]}
behavior = {'publication_observation_gate':True}
assert evidence.require_witness(original,candidate,behavior) == observation
for field, wrong in [('rules',65537),('late.fontSize','16px'),('late.width','16px'),('early.color','rgb(0, 0, 0)'),('early.fontSize','37px')]:
    obs=copy.deepcopy(observation)
    parts=field.split('.')
    if len(parts)==1:obs[field]=wrong
    else:obs[parts[0]][parts[1]]=wrong
    before=copy.deepcopy(original);before['rows'][0]['message']=message(obs)
    reject('wrong original control '+field,lambda:evidence.require_witness(before,candidate,behavior))
for label, side, key, wrong in [('original must fail','original','status','PASS'),('candidate must pass','candidate','status','FAIL'),('wrong callback','candidate','subtest','other')]:
    before,after=copy.deepcopy(original),copy.deepcopy(candidate)
    (before if side=='original' else after)['rows'][0][key]=wrong
    reject(label,lambda:evidence.require_witness(before,after,behavior))
missing=copy.deepcopy(candidate);missing['rows']=[]
reject('missing candidate callback',lambda:evidence.require_witness(original,missing,behavior))
crash=copy.deepcopy(candidate);crash['ends'][0]['status']='CRASH'
reject('candidate crash ending',lambda:evidence.require_witness(original,crash,behavior))
reject('false behavior gate',lambda:evidence.require_witness(original,candidate,{'publication_observation_gate':False}))

predecessor = ROOT / 'artifacts/css-hyphenation-ownership-native-publication-v2'
for name in ('run.py', 'publish.py', 'transform.py', 'delivery.py', 'evidence.py'):
    expected = ''.join(difflib.unified_diff((predecessor/name).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile='executed/'+name, tofile='capacity/'+name))
    assert (HERE/(name+'.diff')).read_text() == expected
old, new = (predecessor/'run.py').read_text(), (HERE/'run.py').read_text()
start = '            with tempfile.TemporaryDirectory('
end = '    except BaseException as error:'
assert new[new.index(start):new.index(end)] == old[old.index(start):old.index(end)].replace('css-hyphenation-ownership-native-', 'css-prioritary-declaration-capacity-native-')
assert (HERE/'delivery.py').read_text() == (predecessor/'delivery.py').read_text().replace("['css-text']['hyphens']","['css-cascade']")
assert "for name in ('run.py', 'transform.py', 'evidence.py', 'STAGES.json')" in (HERE/'publish.py').read_text()
print(json.dumps({'references':len(policy['references']), 'pure_install_commit_transforms':2,
                  'negative_controls':negatives, 'exclusive_creation_and_owned_cleanup':True,
                  'scratch_removed':True, 'signing_tail_preserved':True,
                  'actual_pair_evidence':'pending terminal and independent live audit',
                  'native_git_browser_actions':False}, sort_keys=True))
