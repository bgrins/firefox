import ast
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
PARENT = ROOT / 'artifacts/css-root-self-animation-publication-v1'
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
tests = set(stage['create_tests'])
assert len(stage['files']) == 5 and len(sources) == 1 and len(tests) == 4 and not stage['adopt_existing_tests']
assert set(stage['testharness_paths']) | set(stage['support_paths']) == tests
assert not set(stage['testharness_paths']) & set(stage['support_paths'])
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
    waapi = read(capsule / 'MANIFEST.json')
    manifest = read(ROOT / 'artifacts/css-root-self-smil-coverage-probe-v1/MANIFEST.json')
    manifest['items']['testharness']['web-animations'] = waapi['items']['testharness']['web-animations']
    files = {name: stage['files'][name]['sha256'] for name in tests}
    expected_urls = sorted('/' + p.removeprefix('testing/web-platform/tests/') for p in stage['testharness_paths'])
    assert delivery.verify_entries(manifest, scratch / 'testing/web-platform/tests', files) == expected_urls
    for label, mutate in [
        ('wrong SVG blob', lambda m:m['items']['support']['svg']['animations']['resources']['root-font-target.svg'].__setitem__(0,'wrong')),
        ('SVG registered runnable', lambda m:m['items']['support']['svg']['animations']['resources']['root-font-target.svg'].__setitem__(1,[None,{}])),
        ('missing support tree', lambda m:m['items'].pop('support')),
        ('missing SMIL timeout', lambda m:m['items']['testharness']['svg']['animations']['root-font-self-reference.html'].__setitem__(1,[None,{}])),
        ('missing WAAPI timeout', lambda m:m['items']['testharness']['web-animations']['animation-model']['keyframe-effects']['root-font-self-reference.html'].__setitem__(1,[None,{}]))]:
        bad=copy.deepcopy(manifest);mutate(bad)
        reject(label, lambda: delivery.verify_entries(bad, scratch / 'testing/web-platform/tests', files))
    body=(HERE/'run.py').read_text()
    assertions=[n for n in ast.walk(ast.parse(body)) if isinstance(n,ast.Assert) and any(
        "delivery['"+key+"']" in ast.get_source_segment(body,n) for key in ('files','registered_urls','support_files','lint_command'))]
    assert len(assertions)==4
    guard=compile(ast.Module(body=assertions,type_ignores=[]),'actual-delivery-commit-guards','exec')
    receipt={'files':files, 'registered_urls':expected_urls,
             'support_files':{p:files[p] for p in stage['support_paths']},
             'lint_command':policy['lint_prefix']+sorted(tests)}
    def commit_guard(value):
        exec(guard,{'delivery':value,'stage':stage,'tests':tests,'policy':policy})
    commit_guard(receipt)
    for label,mutate in [
        ('SVG included in runnable URLs',lambda r:r['registered_urls'].append('/svg/animations/resources/root-font-target.svg')),
        ('support omitted from receipt',lambda r:r['support_files'].pop(next(iter(r['support_files'])))),
        ('support digest changed',lambda r:r['support_files'].__setitem__(next(iter(r['support_files'])),'wrong')),
        ('support omitted from lint',lambda r:r['lint_command'].remove(stage['support_paths'][0])),
        ('support omitted from all files',lambda r:r['files'].pop(stage['support_paths'][0]))]:
        bad=copy.deepcopy(receipt);mutate(bad);reject(label,lambda:commit_guard(bad))
    reverse = subprocess.run(['patch', '--batch', '--fuzz=0', '-R', '-p1', '-i', str(HERE / 'native.patch')], cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert reverse.returncode == 0 and b'fuzz' not in reverse.stdout.lower(), reverse.stdout
    assert all(sha(scratch / path) == pin for path, pin in stage['head_preimages'].items())
    assert all(not (scratch / test).exists() for test in tests)
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
assert binding['smil_outcome'] and binding['smil_restoration_verifier']
reject('missing actual evidence', lambda:evidence.verify(ROOT,None,stage))
pending=copy.deepcopy(binding);pending['smil_outcome']=None
reject('pending SMIL evidence', lambda:evidence.verify(ROOT,pending,stage))
evidence.verify_stage(ROOT,binding,stage)
for label,mutate in [
    ('missing SVG stage',lambda s:s['files'].pop(s['support_paths'][0])),
    ('wrong source preimage',lambda s:s['head_preimages'].__setitem__(next(iter(sources)),'wrong')),
    ('SVG misclassified as runnable',lambda s:s['testharness_paths'].append(s['support_paths'].pop())),
    ('support not exclusively created',lambda s:s['create_tests'].remove(s['support_paths'][0])),
    ('extra native path',lambda s:s['files'].update({'servo/unexpected.rs':{'path':'wrong','sha256':'wrong'}}))]:
    bad=copy.deepcopy(stage);mutate(bad)
    reject(label,lambda:evidence.verify_stage(ROOT,binding,bad))
for name in ('run.py','publish.py','transform.py','delivery.py','evidence.py'):
    expected = ''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile=str((PARENT/name).relative_to(ROOT)), tofile=str((HERE/name).relative_to(ROOT))))
    assert (HERE/(name+'.diff')).read_text() == expected
old,new = (PARENT/'run.py').read_text(),(HERE/'run.py').read_text()
start = '            with tempfile.TemporaryDirectory('
assert new[new.index(start):] == old[old.index(start):]
assert (HERE/'transform.py').read_bytes()==(PARENT/'transform.py').read_bytes()
assert (HERE/'delivery.py').read_bytes()==(ROOT/'artifacts/css-root-self-smil-delivery-preparation-v1/delivery.py').read_bytes()
actual=evidence.verify(ROOT,binding,stage)
print(json.dumps({'actual_evidence':actual, 'smil_actual_evidence_pending': False, 'prior_native61_replayed_now': True, 'negative_controls': negatives, 'references': len(policy['references']),
                  'five_stage_paths': sorted(stage['files']), 'zero_fuzz_roundtrip': True, 'genuine_manifest_shape': True,
                  'canonical_installed_claim_inode_controls': True, 'scratch_removed': str(scratch), 'private_signing_rollback_tail_exact': True,
                  'future_publication_authority_pending': True, 'native_git_browser_actions': False}, sort_keys=True))
