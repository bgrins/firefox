import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = json.loads((HERE / 'POLICY.json').read_text())
assert policy['bindings'] is None and policy['enabled_modes'] == []
assert set(policy['files']) == {'servo/components/style/values/generics/calc.rs', 'testing/web-platform/tests/css/css-values/log-clear-special-values.html'}
assert policy['deleted_metadata']['path'] == 'testing/web-platform/meta/css/css-values/exp-log-compute.html.ini'
assert policy['base_sha256'] == '065c05d8c9fee140c07a7ef68841c95a6339ca66021c72122fc8832b136e0103'
for name, pin in policy['references'].items():
    assert name.startswith('artifacts/') and sha(ROOT / name) == pin
for name, pin in policy['packages'].items():
    folder = ROOT / name
    assert sha(folder / 'FILES.json') == pin
    for relative, record in json.loads((folder / 'FILES.json').read_text()).items():
        assert sha(folder / relative) == (record if isinstance(record, str) else record['sha256'])
for name in ('run.py', 'evidence.py'):
    compile((HERE / name).read_bytes(), name, 'exec')
evidence = load('evidence')
observed = evidence.verify(ROOT, policy)
run = load('run')
blobs = {'calc': b'calc body', 'test1': b'first test', 'test2': b'second test'}
sample = {'source_path': 'calc', 'allowed_signers': 'artifacts/synthetic-public-signers', 'minmax_files': {n: hashlib.sha256(v).hexdigest() for n,v in blobs.items()}}
binding = {'head': 'later-artifact-commit'}
research = {'committed': True, 'signature_verified': True, 'head': 'research'}
predecessor = {'signature_verified': True, 'accepted': False, 'app_rebuilt': False,
               'commit': 'minmax', 'parent': 'research-parent', 'files': list(blobs)}


def fake_git(*args):
    if args[0] == 'rev-parse':
        return b'research-parent\n'
    if args[0] == 'merge-base':
        return (args[1] + '\n').encode()
    if args[0] == 'rev-list':
        return b'artifact-commit artifact-parent\n'
    if args[0] == 'diff-tree':
        if '--name-only' in args:
            return b'artifacts/research-record.json\n'
        return b'M\tcalc\nA\ttest1\nA\ttest2\n'
    if args[0] == 'show':
        return blobs[args[1].split(':', 1)[1]]
    assert args[0] == '-c' and args[2:] == ('verify-commit', 'minmax')
    return b''


assert run.verify_predecessor(sample, binding, research, predecessor, fake_git) == 'minmax'
negative = []


def reject(name, mutation=None, replacement=None):
    r, p = copy.deepcopy(research), copy.deepcopy(predecessor)
    if mutation:
        mutation(r, p)
    def query(*args):
        if replacement:
            value = replacement(args)
            if value is not None:
                return value
        return fake_git(*args)
    try:
        run.verify_predecessor(sample, binding, r, p, query)
    except (AssertionError, RuntimeError):
        negative.append(name)
    else:
        raise AssertionError(name)


reject('unsigned research', lambda r,p:r.update(signature_verified=False))
reject('failed predecessor', lambda r,p:p.update(signature_verified=False))
reject('wrong predecessor files', lambda r,p:p.update(files=['calc']))
reject('wrong actual parent', replacement=lambda a:b'other\n' if a[0]=='rev-parse' else None)
reject('nonancestor research or current head', replacement=lambda a:b'other\n' if a[0]=='merge-base' else None)
reject('intervening native change', replacement=lambda a:b'servo/native.rs\n' if a[0]=='diff-tree' and '--name-only' in a else None)
reject('test modified instead of added', replacement=lambda a:b'M\tcalc\nM\ttest1\nA\ttest2\n' if a[0]=='diff-tree' and '--name-status' in a else None)
reject('native change then revert', replacement=lambda a:(b'change parent\nrevert change\n' if a[0]=='rev-list' else b'servo/reverted-native.rs\n' if a[0]=='diff-tree' and '--name-only' in a else None))
reject('intervening merge', replacement=lambda a:b'merge parent1 parent2\n' if a[0]=='rev-list' else None)
reject('wrong predecessor blob', replacement=lambda a:b'wrong' if a[0]=='show' else None)
for key, value in [('wrong_candidate_postimage', 'bad'), ('metadata_targets', policy['metadata_targets'] + ['unrelated'])]:
    altered = copy.deepcopy(policy)
    altered[key] = value
    if key == 'wrong_candidate_postimage':
        altered['files'][policy['source_path']]['sha256'] = 'bad'
    try:
        evidence.verify(ROOT, altered)
    except AssertionError:
        negative.append(key)
    else:
        raise AssertionError(key)
print(json.dumps({'references':len(policy['references']), 'packages':len(policy['packages']),
    'historical_evidence':observed, 'synthetic_predecessor_positive':True,
    'negative_checks':negative, 'execution_enabled':False,
    'browser_raw_replay_native_git_or_live_operations':False}, indent=2))
