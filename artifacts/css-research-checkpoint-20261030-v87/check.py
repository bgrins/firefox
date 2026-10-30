import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('checkpoint', HERE / 'commit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert not m.EXECUTION_ENABLED


def reject(call):
    try:
        call()
    except (AssertionError, RuntimeError):
        return
    raise AssertionError('negative accepted')


binding_negatives = 0
if m.BINDINGS['pending_current_admission']:
    assert m.HEAD is None and m.EPOCH is None
    reject(m.saved_admission)
else:
    m.saved_admission()
    original = copy.deepcopy(m.BINDINGS)
    for mutate in (lambda b:b.update(pending_current_admission=True),
                   lambda b:b.update(head='wrong'),
                   lambda b:b.update(epoch_sha256='wrong'),
                   lambda b:b['controls'].update(**{'ROLE.json':'wrong'}),
                   lambda b:b['native_receipts'][1].update(sha256='wrong')):
        m.BINDINGS = copy.deepcopy(original)
        mutate(m.BINDINGS)
        m.HEAD, m.EPOCH = m.BINDINGS['head'], m.BINDINGS['epoch_sha256']
        reject(m.saved_admission)
        binding_negatives += 1
    m.BINDINGS = original
    m.HEAD, m.EPOCH = original['head'], original['epoch_sha256']
selected = read(HERE / 'SELECTION.json')
prior_path = ROOT / m.BINDINGS['prior_selected_manifest']
assert sha(prior_path) == m.BINDINGS['prior_selected_sha256']
assert not set(selected).intersection(read(prior_path))
for name, record in selected.items():
    path = ROOT / name
    assert path.is_file() and not path.is_symlink()
    assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']
for name, digest in m.BINDINGS['completed_packages'].items():
    manifest = ROOT / name
    assert sha(manifest) == digest
    for member, record in read(manifest).items():
        path = str((manifest.parent / member).relative_to(ROOT))
        assert selected[path]['sha256'] == record['sha256']
policies = [read(ROOT / ('artifacts/' + name + '/POLICY.json')) for name in
            ('css-minmax-native-publication-v3', 'css-log-native-publication-v2')]
source_stages = read(ROOT / 'artifacts/css-registered-color-image-native-publication-v1/STAGES.json')['stages']
stages = read(HERE / 'NATIVE-COMMITS.json')
actual_receipts = 0
parent = '8f0f2859676d19f41848f376724e1281c12f1f00'
for stage, binding in zip(stages, m.BINDINGS['native_receipts']):
    if binding['path'] is None:
        break
    path = ROOT / binding['path']
    assert sha(path) == binding['sha256']
    parent = m.verify_publication_receipt(stage, read(path), parent)
    actual_receipts += 1

receipt_positives = []
for stage in stages:
    receipt = {'signature_verified':True, 'parent':'prior', 'commit':'published',
               'accepted':False, 'app_rebuilt':False, 'accepted_fix_increment':0,
               'files':sorted(stage['statuses'])}
    if stage['stage'] in ('union', 'image'):
        receipt['stage'] = stage['stage']
    assert m.verify_publication_receipt(stage, receipt, 'prior') == 'published'
    receipt_positives.append(stage['stage'])
    if stage['stage'] == 'log':
        missing_deleted = dict(receipt, files=sorted(stage['files']))
        reject(lambda:m.verify_publication_receipt(stage, missing_deleted, 'prior'))
        wrong_added = dict(receipt, files=receipt['files']+['unrelated-file'])
        reject(lambda:m.verify_publication_receipt(stage, wrong_added, 'prior'))

blobs = {}
for i, policy in enumerate(policies):
    assert stages[i]['files'] == {n:r['sha256'] for n,r in policy['files'].items()}
    for name, record in policy['files'].items():
        blobs[(i, name)] = (ROOT / record['capture']).read_bytes()
    if 'deleted_metadata' in policy:
        deletion = policy['deleted_metadata']
        blobs[(i, deletion['path'])] = (ROOT / deletion['capture']).read_bytes()
for i, stage in enumerate(source_stages, 2):
    assert stages[i]['files'] == {n:r['sha256'] for n,r in stage['files'].items()}
    for name, record in stage['files'].items():
        blobs[(i, name)] = (ROOT / record['path']).read_bytes()
original_root, original_bindings = m.ROOT, m.BINDINGS
with tempfile.TemporaryDirectory(prefix='css-v87-chain-check-', dir='/private/tmp') as directory:
    m.ROOT = Path(directory)
    m.BINDINGS = copy.deepcopy(original_bindings)
    receipts = []
    for i, stage in enumerate(stages):
        path = m.ROOT / ('receipt' + str(i) + '.json')
        path.write_text(json.dumps({'commit': 'commit' + str(i), 'parent': 'research' if i == 0 else 'commit' + str(i-1)}))
        receipts.append({'stage':stage['stage'], 'path':path.name, 'sha256':sha(path)})
    m.BINDINGS['native_receipts'] = receipts
    failure = None
    calls = []
    def fake_git(*args):
        calls.append(args)
        if args[0] == 'rev-list':
            commit = args[-1]; i = int(commit.removeprefix('commit'))
            parent = 'research' if i == 0 else 'commit' + str(i-1)
            return (commit + ' ' + ('wrong' if failure == 'parent' else parent)).encode()
        if args[0] == 'diff-tree':
            i = int(args[-1].removeprefix('commit'))
            rows = [status+'\t'+name for name,status in stages[i]['statuses'].items()]
            if failure == 'paths': rows.append('A\tunrelated-file')
            return '\n'.join(rows).encode()
        if args[0] == 'show':
            commit, name = args[1].split(':', 1)
            i = int(commit.removeprefix('commit'))
            if name in stages[1]['deleted']: i = 1
            return b'wrong' if failure == 'blob' else blobs[(i, name)]
        assert args[-2] == 'verify-commit'
        if failure == 'signature': raise RuntimeError('signature rejected')
        return b''
    m.git = fake_git
    m.verify_native_commits()
    assert sum(args[-2] == 'verify-commit' for args in calls if len(args)>1) == 4
    for failure in ('parent', 'paths', 'blob', 'signature'):
        reject(m.verify_native_commits)
m.ROOT, m.BINDINGS = original_root, original_bindings
assert not Path(directory).exists()
first_git_mocked = False
if not m.BINDINGS['pending_current_admission']:
    class GitBoundary(Exception):
        pass
    def boundary(*args, **kwargs):
        assert args == ('rev-parse', 'HEAD')
        raise GitBoundary()
    m.git = boundary
    sys.argv = ['commit.py', '--check']
    try:
        m.main()
    except GitBoundary:
        first_git_mocked = True
    assert first_git_mocked
sys.argv = ['commit.py', '--run']
reject(m.main)
print(json.dumps({'selected':len(selected), 'bytes':sum(r['bytes'] for r in selected.values()),
                  'packages':len(m.BINDINGS['completed_packages']), 'no_v86_reselection':True,
                  'mocked_native_chain_positive':1, 'native_chain_negatives':4,
                  'publication_receipt_positives':receipt_positives, 'log_deletion_membership_negatives':2,
                  'actual_publication_receipts':actual_receipts, 'actual_binding_negatives':binding_negatives, 'first_git_mocked':first_git_mocked,
                  'pending_admission_rejected':True, 'disabled_run_rejected':True,
                  'scratch_removed':True, 'actual_git_or_native_operations':False}))
