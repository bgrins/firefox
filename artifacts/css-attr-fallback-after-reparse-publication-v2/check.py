import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import shutil

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
assert sources == {'servo/components/style/custom_properties.rs'}
assert set(stage['files']) == sources | tests
assert tests == {'testing/web-platform/tests/css/css-values/attr-fallback-taint.html'}
test, = tests
for record in stage['files'].values():
    assert sha(ROOT / record['path']) == record['sha256']
capsule = ROOT / 'artifacts/css-attr-own-fallback-fix-v2'
for name, record in read(capsule / 'FILES.json')['files'].items():
    assert sha(capsule / name) == record['sha256']
typed_capsule = ROOT / 'artifacts/css-explicit-attribute-taint-typed-reparse-fix-v1'
base = typed_capsule / 'candidate/servo/components/style/custom_properties.rs'
assert sha(base) == stage['head_preimages'][source]
assert (HERE / 'native.patch').read_bytes() == (capsule / 'native.patch').read_bytes()

t = load('checked_transform', HERE / 'transform.py')
epoch = {
    'pins': dict(stage['head_preimages'], unrelated='untouched'),
    'staged_working': {}, 'committed_research_working_payloads': {},
    'installed_identities': {**{n:[1,i+2] for i,n in enumerate(sorted(sources))}, 'unrelated':[1,10]},
    'semantic_index': {'head': 'synthetic-research', 'entries': 'same', 'working_diff': hashlib.sha256(b'').hexdigest()},
    'raw_index_observation': {'current': 'synthetic-before', 'historical': 'preserve'},
    'modified_native_paths': [], 'counts': {'native_modified_paths': 0, 'roles': 2, 'installed_identities': 2},
    'prototype_overlay_state': {'installed': False, 'retired_by': 'earlier-publication'},
    'registered_color_image_publication': {'image': {'native_commit': 'earlier-image'}},
    'nowrap_publication': {'nowrap': {'native_commit': 'already-published-nowrap'}},
    'language_partition_publication': {'language': {'native_commit': 'already-published-language'}},
    'hyphenation_ownership_publication': {'ownership': {'native_commit': 'already-published-ownership'}},
    'prioritary_declaration_capacity_publication': {'capacity': {'native_commit': 'already-published-capacity'}},
    'registered_number_transition': {'role': 'published-native'},
    'explicit_taint_reparse_publication': {'reparse': {'native_commit': 'future-typed-synthetic'}},
    'accepted_fix_count': 149, 'accepted_records': ['historical'],
    'canonical_application': {'built': False, 'sha256': 'restored-old-app'},
    'untracked_native': ['unrelated-native'], 'nested_semantic_index': {'head': 'nested'},
}
owned = {'unrelated': {'identity': [1, 3]}}
role = {'built': False, 'variant': 'reparse', 'last_build': 'obsolete', 'last_install': 'obsolete'}
original = copy.deepcopy((epoch, owned, role))
claims = {name: {'path': name, 'identity': [1, 2 if name == source else 4], 'owned_sha256': record['sha256']} for name, record in stage['files'].items()}
semantic = dict(epoch['semantic_index'], working_diff='synthetic-ownership-diff')
current, new_owned, new_role = t.installed(epoch, owned, role, stage, claims, {'raw_index': 'synthetic-install'}, semantic, 'synthetic-manifest', 'synthetic-runtime')
assert (epoch, owned, role) == original
assert current['modified_native_paths'] == sorted(sources)
assert new_role['variant'] == 'fallback' and new_role['built'] is False
assert 'last_build' not in new_role and 'last_install' not in new_role
assert new_role['paired_head'] == 'synthetic-research'
allowed = {'pins', 'installed_identities', 'semantic_index', 'raw_index_observation', 'modified_native_paths', 'counts', 'attr_fallback_publication', 'registered_number_transition'}
assert {k: v for k, v in current.items() if k not in allowed} == {k: v for k, v in epoch.items() if k not in allowed}
assert current['pins']['unrelated'] == 'untouched' and new_owned['unrelated'] == owned['unrelated']
assert current['installed_identities'][test] == claims[test]['identity'] and new_owned[test] == claims[test]
for name in stage['files']:
    bad = copy.deepcopy(claims)
    bad[name]['owned_sha256'] = 'wrong'
    reject('wrong postimage claim: ' + name, lambda: t.installed(epoch, owned, role, stage, bad, {}, semantic, 'synthetic', 'synthetic'))
final = t.committed(current, 'fallback', {'raw_index': 'synthetic-committed'}, dict(semantic, head='synthetic-commit', working_diff=hashlib.sha256(b'').hexdigest()), 'synthetic-commit')
assert final['modified_native_paths'] == [] and final['counts']['native_modified_paths'] == 0
assert final['attr_fallback_publication']['fallback']['native_commit'] == 'synthetic-commit'
assert final['registered_number_transition']['paired_head'] == 'synthetic-commit'
assert final['pins'] == current['pins'] and final['installed_identities'] == current['installed_identities']
for name in ('prototype_overlay_state', 'registered_color_image_publication', 'nowrap_publication', 'language_partition_publication', 'hyphenation_ownership_publication', 'prioritary_declaration_capacity_publication', 'explicit_taint_reparse_publication', 'accepted_fix_count', 'accepted_records', 'canonical_application', 'nested_semantic_index', 'untracked_native'):
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
    tree = {target.name: [blob, [None, {'timeout': 'long'}]]}
    manifest = {'items': {'testharness': {'css': {'css-values': tree}}}}
    files = {test: stage['files'][test]['sha256']}
    assert delivery.verify_entries(manifest, scratch/'testing/web-platform/tests', files) == ['/css/css-values/'+target.name]
    fixture_manifest = read(capsule / 'MANIFEST.json')
    selected_manifest = dict(fixture_manifest, items={'testharness': fixture_manifest['items']['testharness']})
    assert delivery.verify_entries(selected_manifest, scratch/'testing/web-platform/tests', files) == ['/css/css-values/'+target.name]
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['css']['css-values'][target.name][0] = 'wrong'
    reject('wrong manifest blob', lambda: delivery.verify_entries(bad, scratch/'testing/web-platform/tests', files))
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['css']['css-values'][target.name][1][1] = {}
    reject('missing genuine long timeout', lambda: delivery.verify_entries(bad, scratch/'testing/web-platform/tests', files))
    owner.claim(scratch, test, created['owned_sha256'], created['identity'])
    assert parents.parent_pins(scratch, target) == parent_claims
    target.unlink()
    assert not target.exists()
assert not scratch.exists()
evidence = load('checked_evidence', HERE / 'evidence.py')
binding = read(HERE / 'PAIR-BINDING.json')
reject('pending authority cannot execute', lambda: evidence.verify(ROOT, binding, stage))
actual = evidence.verify_completed(ROOT, binding, stage)
assert (actual['candidate_pass'], actual['preserved_pass_signatures'], actual['preserved_ending_signatures'], actual['fail_to_pass']) == (82,69,7,13)
native_owner = ROOT / 'artifacts/css-explicit-taint-combined-native-candidate-browser-v1'
native_runtime = ROOT / 'artifacts/css-explicit-taint-combined-native-candidate-browser-runtime-v1'
assessor = load('checked_combined_assessor', native_owner / 'assess.py')
baseline = read(native_owner / 'BASELINE82.json')
rows, ends = [], []
for lane in ('reparse','fallback','controls','composition'):
    assessment = read(native_runtime / ('candidate-wpt-'+lane) / 'ASSESSMENT.json')
    rows.extend(assessor.signature(row) for row in assessment['rows'])
    ends.extend(assessor.signature(row) for row in assessment['ends'])
for label, mutate in [
    ('lost callback', lambda r,e: r.pop()),
    ('duplicate callback', lambda r,e: r.__setitem__(0,r[1])),
    ('candidate failure', lambda r,e: r[0].update(status='FAIL')),
    ('ending metadata changed', lambda r,e: e[0].update(message='changed')),
    ('old PASS message changed', lambda r,e: r[0].update(message='changed')),
]:
    r,e = copy.deepcopy((rows,ends));mutate(r,e)
    reject(label,lambda:evidence.require_comparison(baseline,r,e))
source_info=read(typed_capsule/'SOURCE.json')
future=dict(binding,typed_native_receipt={'path':'synthetic','sha256':'synthetic'},current_capture={'path':'synthetic','sha256':'synthetic'},current_epoch_sha256='synthetic-epoch')
receipt={'stage':'reparse','signature_verified':True,'files':sorted([source,evidence.TYPED_TEST]),'app_rebuilt':False,'accepted_fix_increment':0,'commit':'a'*40,'parent':'b'*40}
capture={'full_current_state_verified':True,'source_transition_lock_absent':True,'sources_match_head':True,'controls':{'CURRENT-EPOCH.json':'synthetic-epoch'},'payload_claims':{source:{'path':source,'owned_sha256':stage['head_preimages'][source],'identity':[1,2]}},'snapshot':{'index':{'cached_diff':hashlib.sha256(b'').hexdigest(),'working_diff':hashlib.sha256(b'').hexdigest()}}}
capture['sources']=copy.deepcopy(capture['payload_claims'])
capture['installed_identities']={source:[1,2]}
capture['epoch_payload_pins']=dict(stage['head_preimages'])
evidence.require_future(future,receipt,capture,source_info)
for key in ('typed_native_receipt','current_capture','current_epoch_sha256'):
    bad=dict(future);bad[key]=None
    reject('missing '+key,lambda:evidence.require_future(bad,receipt,capture,source_info))
for key,value in [('stage','capacity'),('signature_verified',False),('files',[source]),('app_rebuilt',True)]:
    bad=dict(receipt);bad[key]=value
    reject('wrong typed receipt '+key,lambda:evidence.require_future(future,bad,capture,source_info))
for label,mutate in [
    ('old source',lambda c:c['payload_claims'][source].update(owned_sha256='bb13')),
    ('wrong rich schema',lambda c:c['payload_claims'][source].update(sha256=c['payload_claims'][source].pop('owned_sha256'))),
    ('wrong claim path',lambda c:c['payload_claims'][source].update(path='other')),
    ('different captured inode',lambda c:c['installed_identities'].update({source:[1,3]})),
    ('wrong epoch',lambda c:c['controls'].update({'CURRENT-EPOCH.json':'wrong'})),
    ('dirty index digest',lambda c:c['snapshot']['index'].update(cached_diff=hashlib.sha256(b'dirty').hexdigest())),
    ('dirty working digest',lambda c:c['snapshot']['index'].update(working_diff=hashlib.sha256(b'dirty').hexdigest())),
    ('raw empty index schema',lambda c:c['snapshot']['index'].update(cached_diff='')),
    ('raw empty working schema',lambda c:c['snapshot']['index'].update(working_diff='')),
    ('missing lock check',lambda c:c.update(source_transition_lock_absent=False)),
]:
    bad=copy.deepcopy(capture);mutate(bad)
    reject(label,lambda:evidence.require_future(future,receipt,bad,source_info))
with tempfile.TemporaryDirectory(prefix='fallback-after-reparse-patch-',dir='/private/tmp') as directory:
    patch_scratch=Path(directory);target=patch_scratch/source;target.parent.mkdir(parents=True);shutil.copyfile(base,target)
    forward=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str((HERE/'native.patch').resolve())],cwd=patch_scratch,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert forward.returncode==0,forward.stdout
    assert b'fuzz' not in forward.stdout.lower()
    assert sha(target)==stage['files'][source]['sha256']
    assert sha(patch_scratch/test)==stage['files'][test]['sha256']
    reverse=subprocess.run(['patch','--batch','--fuzz=0','-R','-p1','-i',str((HERE/'native.patch').resolve())],cwd=patch_scratch,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert reverse.returncode==0,reverse.stdout
    assert b'fuzz' not in reverse.stdout.lower()
    assert sha(target)==sha(base) and not (patch_scratch/test).exists()
assert not patch_scratch.exists()
predecessor=ROOT/'artifacts/css-attr-fallback-publication-v1'
for name in ('run.py','publish.py','transform.py','delivery.py','evidence.py','check.py','POLICY.json','STAGES.json','PAIR-BINDING.json'):
    expected=''.join(difflib.unified_diff((predecessor/name).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile=str((predecessor/name).relative_to(ROOT)),tofile=str((HERE/name).relative_to(ROOT))))
    assert (HERE/(name+'.diff')).read_text()==expected
old,new=(predecessor/'run.py').read_text(),(HERE/'run.py').read_text()
start='            with tempfile.TemporaryDirectory('
assert new[new.index(start):]==old[old.index(start):]
for name in ('transform.py','delivery.py'):
    assert (HERE/name).read_bytes()==(predecessor/name).read_bytes()
assert (HERE/'publish.py').read_text()==(predecessor/'publish.py').read_text().replace('css-attr-fallback-publication-','css-attr-fallback-after-reparse-publication-')
print(json.dumps({'references':len(policy['references']),'negative_controls':negatives,'actual_combined':{k:actual[k] for k in ['candidate_pass','preserved_pass_signatures','preserved_ending_signatures','fail_to_pass']},'historical_standalone':[17,11,28],'zero_fuzz_forward_reverse':True,'patch_output':forward.stdout.decode()+reverse.stdout.decode(),'scratch_removed':True,'signing_rollback_tail_exact':True,'delivery_transform_exact':True,'all_future_authority_null':True,'no_native_git_browser_actions':True},sort_keys=True))
