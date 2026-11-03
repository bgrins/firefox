import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('reparse',))
    parser.add_argument('action', choices=('install', 'delivery', 'commit'))
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--predecessor', type=Path)
    parser.add_argument('--predecessor-sha256')
    parser.add_argument('--pair-binding', type=Path)
    parser.add_argument('--pair-binding-sha256')
    args = parser.parse_args()
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    owner = load('owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    records = owner.authenticate(HERE, args.manifest)
    policy = read(HERE / 'POLICY.json')
    assert policy['bindings'] is None and policy['stage'] is None and policy['enabled_modes'] == []
    for path, pin in policy['references'].items():
        assert sha(ROOT / path) == pin
    stage = next(s for s in read(HERE / 'STAGES.json')['stages'] if s['stage'] == args.stage)
    policy['stage'] = args.stage
    policy['runtime_output'] = 'artifacts/css-explicit-taint-typed-reparse-publication-' + args.stage + '-runtime-1'
    for name, record in records.items():
        policy['references'][str((HERE / name).relative_to(ROOT))] = record['sha256']
    policy['references'][str((HERE / 'FILES.json').relative_to(ROOT))] = args.manifest
    output = ROOT / policy['runtime_output']
    install_owner = ROOT / ('artifacts/css-explicit-taint-typed-reparse-publication-' + args.stage + '-install-v1')
    installed = None
    assert policy['pair_binding'] is None
    if args.action != 'install':
        assert args.predecessor is None and args.predecessor_sha256 is None
        assert args.pair_binding is None and args.pair_binding_sha256 is None
        installed = read(output / 'INSTALL-RESULT.json')
        owner.authenticate(install_owner, installed['manifest_sha256'])
        prior_policy = read(install_owner / 'POLICY.json')
        expected = copy.deepcopy(policy)
        expected.update(bindings=prior_policy['bindings'], pair_binding=prior_policy['pair_binding'], enabled_modes=['install'])
        assert expected == prior_policy
        assert installed['installed'] and installed['stage'] == args.stage and not installed['app_rebuilt']
        predecessor = prior_policy['bindings']['predecessor_receipt']
        policy['pair_binding'] = prior_policy['pair_binding']
    else:
        assert args.predecessor and args.predecessor_sha256 and args.pair_binding and args.pair_binding_sha256
        assert sha(args.pair_binding) == args.pair_binding_sha256
        policy['pair_binding'] = read(args.pair_binding)
        path = args.predecessor.resolve()
        assert sha(path) == args.predecessor_sha256
        predecessor = {'path': str(path.relative_to(ROOT)), 'sha256': args.predecessor_sha256}
    load('nowrap_pair_evidence', HERE / 'evidence.py').verify(ROOT, policy['pair_binding'], stage)
    if args.action == 'delivery':
        delivery = load('delivery', HERE / 'delivery.py')
        delivery_policy = dict(policy, files=stage['files'], lint_command=policy['lint_prefix'] + sorted(p for p in stage['files'] if p.startswith('testing/')))
        delivery.run(delivery_policy, installed['manifest_sha256'])
        return
    runner = load('runner', HERE / 'run.py')
    state = owner.load_state(RUNTIME)
    controls = {n: sha(RUNTIME / n) for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    epoch = read(RUNTIME / 'CURRENT-EPOCH.json')
    snapshot = state.a.verify_current(state.h, ROOT, runner.ENV, epoch)
    assert controls == {n: sha(RUNTIME / n) for n in controls}
    head = runner.git('rev-parse', 'HEAD').decode().strip()
    prior = read(ROOT / predecessor['path'])
    assert sha(ROOT / predecessor['path']) == predecessor['sha256']
    assert prior['head'] == head and prior['signature_verified']
    claims = {p: {'sha256': epoch['pins'][p], 'identity': identity}
              for p, identity in epoch['installed_identities'].items() if p not in stage['files']}
    binding = {'head': head, 'branch': runner.git('symbolic-ref', 'HEAD').decode().strip(),
               'controls': controls, 'snapshot': snapshot, 'predecessor_receipt': predecessor,
               'predecessor_kind': 'signed-research',
               'preserved_claims': claims,
               'historical_markers': {k:v for k,v in epoch.items() if k.startswith('accepted_')},
               'absent_metadata': sorted(p.replace('testing/web-platform/tests/', 'testing/web-platform/meta/') + '.ini'
                                         for p in stage['files'] if p.startswith('testing/'))}
    if installed is None:
        creation = load('adoption_parents', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
        binding['adopted_tests'] = {path: {'claim': owner.claim(ROOT, path, record['sha256']), 'parents': creation.parent_pins(ROOT, ROOT / path)} for path, record in stage['files'].items() if path in stage['adopt_existing_tests']}
        binding['created_test_parents'] = {path: creation.parent_pins(ROOT, ROOT/path) for path in stage['create_tests']}
        assert all(not os.path.lexists(ROOT/path) for path in stage['create_tests'])
        for name, record in records.items():
            assert hashlib.sha256(runner.git('show', head + ':' + str((HERE/name).relative_to(ROOT)))).hexdigest() == record['sha256']
    else:
        binding['adopted_tests'] = prior_policy['bindings']['adopted_tests']
        binding['created_test_parents'] = prior_policy['bindings']['created_test_parents']
    if installed is not None:
        assert controls['CURRENT-EPOCH.json'] == installed['epoch_sha256']
        binding['installation_manifest'] = installed['manifest_sha256']
        path = output / 'delivery/DELIVERY.json'
        binding['delivery_receipt'] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}
    policy.update(bindings=binding, enabled_modes=[args.action])
    directory = ROOT / ('artifacts/css-explicit-taint-typed-reparse-publication-' + args.stage + '-' + args.action + '-v1')
    directory.mkdir()
    for name in ('run.py', 'transform.py', 'evidence.py', 'STAGES.json'):
        with (directory / name).open('xb') as stream:
            stream.write((HERE / name).read_bytes())
    save(directory / 'POLICY.json', policy)
    save(directory / 'FILES.json', {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in directory.iterdir()})
    result = subprocess.run([sys.executable, '-I', '-S', '-B', str(directory / 'run.py'), args.action, sha(directory / 'FILES.json')], cwd=ROOT)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
