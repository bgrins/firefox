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
PARENT = ROOT / 'artifacts/css-keyframe-font-unit-publication-v1'
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
    except (AssertionError, RuntimeError, KeyError, TypeError, subprocess.CalledProcessError):
        negatives.append(label)
    else:
        raise AssertionError(label)


policy = read(HERE / 'POLICY.json')
assert policy['enabled_modes'] == []
assert all(policy[key] is None for key in ('bindings', 'pair_binding', 'stage', 'runtime_output'))
for path, pin in policy['references'].items():
    assert sha(ROOT / path) == pin, path
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
stage, = read(HERE / 'STAGES.json')['stages']
assert len(stage['files']) == 5 and len(stage['head_preimages']) == 3
assert len(stage['create_tests']) == 2 and not stage['adopt_existing_tests']
for record in stage['files'].values():
    assert sha(ROOT / record['path']) == record['sha256']
runner = load('checked_runner', HERE / 'run.py')
evidence = load('checked_evidence', HERE / 'evidence.py')
owner = load('real_ownership', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
transform = load('checked_transform', HERE / 'transform.py')
delivery = load('checked_delivery', HERE / 'delivery.py')
binding = read(HERE / 'PAIR-BINDING.json')
reject('pending signed font receipt', lambda: evidence.verify(ROOT, binding, stage))
parent = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-fix-v1/parent'
with tempfile.TemporaryDirectory(prefix='selective-publication-check-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    epoch = {'pins': dict(stage['head_preimages']), 'installed_identities': {}}
    ownership = {}
    for path, pin in stage['head_preimages'].items():
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(parent / path, target)
        claim = owner.claim(scratch, path, pin)
        if path in runner.INSTALLED_SOURCES:
            epoch['installed_identities'][path] = claim['identity']
            ownership[path] = claim
        assert runner.claim_source(owner, scratch, epoch, ownership, path, pin, claim) == claim
        wrong = copy.deepcopy(epoch); wrong['pins'][path] = 'wrong'
        reject('wrong source pin ' + path, lambda: runner.claim_source(owner, scratch, wrong, ownership, path, pin, claim))
        wrong = copy.deepcopy(epoch)
        if path in runner.INSTALLED_SOURCES:
            wrong['installed_identities'].pop(path)
        else:
            wrong['installed_identities'][path] = claim['identity']
        reject('wrong installed role ' + path, lambda: runner.claim_source(owner, scratch, wrong, ownership, path, pin, claim))
        wrong_owned = copy.deepcopy(ownership)
        if path in runner.INSTALLED_SOURCES:
            wrong_owned[path]['owned_sha256'] = 'wrong'
        else:
            wrong_owned[path] = claim
        reject('wrong ownership ' + path, lambda: runner.claim_source(owner, scratch, epoch, wrong_owned, path, pin, claim))
        retained = target.with_suffix('.retained'); target.rename(retained); target.write_bytes(retained.read_bytes())
        reject('same bytes replaced inode ' + path, lambda: runner.claim_source(owner, scratch, epoch, ownership, path, pin, claim))
        target.unlink(); retained.rename(target)
    for name in stage['create_tests']:
        (scratch / name).parent.mkdir(parents=True, exist_ok=True)
    for reverse in (False, True):
        args = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / 'native.patch')]
        if reverse:
            args.append('-R')
        result = subprocess.run(args, cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert result.returncode == 0 and b'fuzz' not in result.stdout.lower(), result.stdout
        if not reverse:
            assert all(sha(scratch / path) == record['sha256'] for path, record in stage['files'].items())
            delivery.ROOT = scratch
            entries = {}
            for name in stage['create_tests']:
                body = (scratch / name).read_bytes()
                entries[Path(name).name] = [hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest(), [None, {'timeout': 'long'}]]
            manifest = {'items': {'testharness': {'web-animations': {'animation-model': {'keyframe-effects': entries}}}}}
            files = {name: stage['files'][name]['sha256'] for name in stage['create_tests']}
            assert len(delivery.verify_entries(manifest, scratch / 'testing/web-platform/tests', files)) == 2
            bad = copy.deepcopy(manifest)
            next(iter(bad['items']['testharness']['web-animations']['animation-model']['keyframe-effects'].values()))[0] = 'wrong'
            reject('wrong delivered blob', lambda: delivery.verify_entries(bad, scratch / 'testing/web-platform/tests', files))
    assert all(sha(scratch / path) == pin for path, pin in stage['head_preimages'].items())
    assert all(not (scratch / path).exists() for path in stage['create_tests'])
assert not scratch.exists()
font_stage, = read(PARENT / 'STAGES.json')['stages']
receipt = {'stage': 'font-units', 'signature_verified': True, 'files': sorted(font_stage['files']), 'app_rebuilt': False,
           'accepted_fix_increment': 0, 'commit': '1' * 40, 'parent': '2' * 40, 'epoch_sha256': '3' * 64}
evidence.require_font_receipt(receipt, font_stage)
for key, value in [('stage', 'other'), ('signature_verified', False), ('files', []), ('app_rebuilt', True),
                   ('accepted_fix_increment', 1), ('commit', 'bad'), ('parent', receipt['commit'])]:
    bad = dict(receipt); bad[key] = value
    reject('font receipt ' + key, lambda: evidence.require_font_receipt(bad, font_stage))
base = ROOT / 'artifacts/css-keyframe-font-unit-dependency-fix-v1/original'
records = {}
for path, record in font_stage['files'].items():
    records[receipt['commit'] + ':' + path] = (ROOT / record['path']).read_bytes()
    if path in font_stage['head_preimages']:
        records[receipt['parent'] + ':' + path] = (base / path).read_bytes()


def git_double(*args):
    if args[0] == 'rev-list': return (receipt['commit'] + ' ' + receipt['parent']).encode()
    if args[0] == '-c': return b''
    if args[0] == 'diff':
        return ('\n'.join(sorted(font_stage['files'])) if args[2] == receipt['parent'] else 'artifacts/example').encode()
    if args[0] == 'show': return records[args[1]]
    if args[0] in ('ls-tree', 'merge-base'): return b''
    raise AssertionError(args)


evidence.verify_font_history(git_double, 'signers', receipt, font_stage, evidence.BASE)
for label, command, replacement in [('extra native path', 'diff', b'servo/other.rs'), ('merge parent', 'rev-list', b'bad'),
                                     ('wrong native blob', 'show', b'bad'), ('existing WPT', 'ls-tree', b'exists'),
                                     ('failed ancestry', 'merge-base', b'not-ancestor')]:
    def changed(*args):
        return replacement if args[0] == command else git_double(*args)
    reject(label, lambda: evidence.verify_font_history(changed, 'signers', receipt, font_stage, evidence.BASE))
def dirty_research(*args):
    if args[0] == 'diff' and args[2] == evidence.BASE: return b'servo/unrelated.rs'
    return git_double(*args)
reject('native change before font', lambda: evidence.verify_font_history(dirty_research, 'signers', receipt, font_stage, evidence.BASE))
epoch = {'pins': dict(stage['head_preimages']), 'staged_working': {}, 'committed_research_working_payloads': {},
         'installed_identities': {}, 'semantic_index': {'head': 'synthetic'}, 'raw_index_observation': {'current': 'old'},
         'modified_native_paths': [], 'counts': {}, 'registered_number_transition': {}}
for marker in ('prototype_overlay_state', 'registered_color_image_publication', 'nowrap_publication', 'language_partition_publication',
               'hyphenation_ownership_publication', 'prioritary_declaration_capacity_publication', 'keyframe_font_unit_publication'):
    epoch[marker] = {'preserved': marker}
claims = {path: {'path': path, 'owned_sha256': record['sha256'], 'identity': [1, number + 2]}
          for number, (path, record) in enumerate(stage['files'].items())}
installed, _, _ = transform.installed(epoch, {}, {}, stage, claims, {'raw_index': 'new'}, {'head': 'font'}, 'manifest', 'runtime')
committed = transform.committed(installed, stage['stage'], {'raw_index': 'end'}, {'head': 'cancellation'}, 'cancellation')
assert committed['keyframe_font_unit_publication'] == epoch['keyframe_font_unit_publication']
assert committed['modified_native_paths'] == []
actual = evidence.verify_completed(ROOT, binding, stage)
comparison = read(ROOT / binding['comparison']['directory'] / 'RESULT.json')
lane = comparison['lanes'][0]
old, end = evidence.signatures(evidence.events(ROOT / 'artifacts' / lane['original']), lane['page'], 8)
new, new_end = evidence.signatures(evidence.events(ROOT / 'artifacts' / lane['candidate']), lane['page'], 8)
targets = {row['before']['subtest'] for row in lane['changed']}
for label, mutate in [('missing callback', lambda r:r.pop()), ('duplicate callback', lambda r:r.__setitem__(0, r[1])),
                       ('candidate FAIL', lambda r:r[0].update(status='FAIL')),
                       ('prior PASS message', lambda r:next(x for x in r if x['subtest'] not in targets).update(message='changed'))]:
    bad = copy.deepcopy(new); mutate(bad)
    reject(label, lambda: evidence.compare_lane(old, bad, end, new_end, targets))
bad_end = dict(new_end, message='changed')
reject('ending changed', lambda: evidence.compare_lane(old, new, end, bad_end, targets))
old, new = (PARENT / 'run.py').read_text(), (HERE / 'run.py').read_text()
start = '            with tempfile.TemporaryDirectory('
assert new[new.index(start):] == old[old.index(start):].replace('css-keyframe-font-unit-native-', 'css-selective-cancellation-native-')
assert (HERE / 'delivery.py').read_bytes() == (PARENT / 'delivery.py').read_bytes()
print(json.dumps({'actual_evidence': actual, 'negative_controls': negatives, 'references': len(policy['references']),
                  'patch_roundtrip': True, 'real_claim_inode_controls': True, 'scratch_removed': str(scratch),
                  'pure_transforms': 2, 'future_git_protocol_double': True, 'delivery_shape_is_synthetic': True,
                  'signing_rollback_tail_exact': True, 'future_authority_pending': True, 'live_actions': False}, sort_keys=True))
