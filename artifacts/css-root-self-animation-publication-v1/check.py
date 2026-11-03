import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-explicit-taint-typed-reparse-publication-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


negatives = []


def reject(label, fn):
    try:
        fn()
    except (AssertionError, RuntimeError, KeyError, FileExistsError):
        negatives.append(label)
    else:
        raise AssertionError(label)


policy = read(HERE / 'POLICY.json')
assert policy['enabled_modes'] == []
assert all(policy[k] is None for k in ('bindings', 'pair_binding', 'stage', 'runtime_output'))
for path, pin in policy['references'].items():
    assert sha(ROOT / path) == pin, path
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
stage, = read(HERE / 'STAGES.json')['stages']
sources = set(stage['head_preimages'])
test, = stage['create_tests']
assert len(stage['files']) == 2 and len(sources) == 1 and not stage['adopt_existing_tests']
assert test == 'testing/web-platform/tests/web-animations/animation-model/keyframe-effects/root-font-self-reference.html'
for record in stage['files'].values():
    assert sha(ROOT / record['path']) == record['sha256']
runner = load('tested_runner', HERE / 'run.py')
owner = load('actual_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
transform = load('tested_transform', HERE / 'transform.py')
delivery = load('tested_delivery', HERE / 'delivery.py')
capsule = ROOT / 'artifacts/css-root-self-animation-context-fix-v3'
with tempfile.TemporaryDirectory(prefix='root-self-publication-check-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    epoch = {'pins': dict(stage['head_preimages']), 'installed_identities': {}}
    for path, pin in stage['head_preimages'].items():
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(capsule / 'original' / path, target)
        claim = owner.claim(scratch, path, pin)
        epoch['installed_identities'][path] = claim['identity']
        assert owner.claim(scratch, path, epoch['pins'][path], epoch['installed_identities'][path]) == claim
        reject('wrong canonical preimage', lambda: owner.claim(scratch, path, '0' * 64, claim['identity']))
        reject('wrong installed identity', lambda: owner.claim(scratch, path, pin, [0, 0]))
        retained = target.with_suffix('.retained')
        target.rename(retained); target.write_bytes(retained.read_bytes())
        reject('identical bytes different inode', lambda: owner.claim(scratch, path, pin, claim['identity']))
        target.unlink(); retained.rename(target)
    forward = subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / 'native.patch')], cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert forward.returncode == 0 and b'fuzz' not in forward.stdout.lower(), forward.stdout
    assert all(sha(scratch / path) == record['sha256'] for path, record in stage['files'].items())
    delivery.ROOT = scratch
    fixture = read(capsule / 'MANIFEST.json')
    manifest = dict(fixture, items={'testharness': fixture['items']['testharness']})
    files = {test: stage['files'][test]['sha256']}
    assert delivery.verify_entries(manifest, scratch / 'testing/web-platform/tests', files) == ['/' + test.removeprefix('testing/web-platform/tests/')]
    entries = manifest['items']['testharness']['web-animations']['animation-model']['keyframe-effects']
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['web-animations']['animation-model']['keyframe-effects'][Path(test).name][0] = 'wrong'
    reject('wrong WPT blob', lambda: delivery.verify_entries(bad, scratch / 'testing/web-platform/tests', files))
    bad = copy.deepcopy(manifest)
    bad['items']['testharness']['web-animations']['animation-model']['keyframe-effects'][Path(test).name][1][1] = {}
    reject('missing timeout long', lambda: delivery.verify_entries(bad, scratch / 'testing/web-platform/tests', files))
    reverse = subprocess.run(['patch', '--batch', '--fuzz=0', '-R', '-p1', '-i', str(HERE / 'native.patch')], cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert reverse.returncode == 0 and b'fuzz' not in reverse.stdout.lower(), reverse.stdout
    assert all(sha(scratch / path) == pin for path, pin in stage['head_preimages'].items())
    assert not (scratch / test).exists()
assert not scratch.exists()
epoch = {'pins': dict(stage['head_preimages']), 'staged_working': {}, 'committed_research_working_payloads': {},
         'installed_identities': {}, 'semantic_index': {'head': 'synthetic'}, 'raw_index_observation': {'current': 'old'},
         'modified_native_paths': [], 'counts': {}, 'registered_number_transition': {}}
for marker in ('prototype_overlay_state', 'registered_color_image_publication', 'nowrap_publication',
               'language_partition_publication', 'hyphenation_ownership_publication',
               'prioritary_declaration_capacity_publication', 'explicit_taint_reparse_publication', 'attr_fallback_publication'):
    epoch[marker] = {'preserved': marker}
claims = {path: {'path': path, 'owned_sha256': record['sha256'], 'identity': [1, i + 2]}
          for i, (path, record) in enumerate(stage['files'].items())}
original = copy.deepcopy(epoch)
installed, owned, role = transform.installed(epoch, {}, {'built': False}, stage, claims,
                                           {'raw_index': 'installed'}, {'head': 'synthetic'}, 'manifest', 'runtime')
assert epoch == original and installed['modified_native_paths'] == sorted(sources)
assert all(installed['installed_identities'][p] == claims[p]['identity'] for p in claims)
committed = transform.committed(installed, 'root-identity', {'raw_index': 'committed'}, {'head': 'native'}, 'native')
assert committed['modified_native_paths'] == [] and committed['root_self_animation_publication']['root-identity']['native_commit'] == 'native'
for marker in ('explicit_taint_reparse_publication', 'attr_fallback_publication', 'prototype_overlay_state'):
    assert committed[marker] == epoch[marker]
evidence = load('publication_evidence', HERE / 'evidence.py')
binding = read(HERE / 'PAIR-BINDING.json')
reject('missing actual evidence', lambda: evidence.verify(ROOT, None, stage))
bad = copy.deepcopy(stage); bad['files'].pop(test)
reject('missing WPT stage path', lambda: evidence.verify(ROOT, binding, bad))
bad = copy.deepcopy(stage); bad['head_preimages'][next(iter(sources))] = 'wrong'
reject('wrong source preimage', lambda: evidence.verify(ROOT, binding, bad))
actual = evidence.verify(ROOT, binding, stage)
comparison = load('pure_signatures', ROOT / binding['outcome']['directory'] / 'compare.py')
original = read(ROOT / 'artifacts/css-root-self-animation-native-validation-plan-v1/ORIGINAL61.json')
runtime = ROOT / 'artifacts/css-root-self-animation-candidate-browser-runtime-v1'
assessor = load('signatures', ROOT / 'artifacts/css-root-self-animation-candidate-browser-v2/assess.py')
baseline = {'rows': [assessor.signature(row) for row in original['rows']],
            'ends': [assessor.signature(row) for row in original['endings']]}
rows, ends = [], []
for lane in ('root_identity', 'controls'):
    a = read(runtime / ('candidate-wpt-' + lane) / 'ASSESSMENT.json')
    rows.extend(assessor.signature(row) for row in a['rows'])
    ends.extend(assessor.signature(row) for row in a['ends'])
for label, mutate in [('missing callback', lambda r,e:r.pop()), ('duplicate callback', lambda r,e:r.__setitem__(0,r[1])),
                      ('candidate FAIL', lambda r,e:r[0].update(status='FAIL')),
                      ('old PASS metadata changed', lambda r,e:next(x for x in r if x['test'] != '/' + test.removeprefix('testing/web-platform/tests/')).update(message='changed')),
                      ('ending metadata changed', lambda r,e:e[0].update(message='changed'))]:
    r,e = copy.deepcopy((rows,ends)); mutate(r,e)
    reject(label, lambda: comparison.compare_signatures(baseline,r,e))
for name in ('run.py','publish.py','transform.py','delivery.py','evidence.py'):
    expected = ''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile=str((PARENT/name).relative_to(ROOT)), tofile=str((HERE/name).relative_to(ROOT))))
    assert (HERE/(name+'.diff')).read_text() == expected
old,new = (PARENT/'run.py').read_text(),(HERE/'run.py').read_text()
start = '            with tempfile.TemporaryDirectory('
assert new[new.index(start):] == old[old.index(start):].replace('css-explicit-taint-typed-reparse-native','css-root-self-animation-native')
print(json.dumps({'actual_evidence': actual, 'negative_controls': negatives, 'references': len(policy['references']),
                  'two_stage_paths': sorted(stage['files']), 'zero_fuzz_roundtrip': True, 'genuine_manifest_shape': True,
                  'canonical_installed_claim_inode_controls': True, 'scratch_removed': str(scratch), 'private_signing_rollback_tail_exact': True,
                  'future_publication_authority_pending': True, 'native_git_browser_actions': False}, sort_keys=True))
