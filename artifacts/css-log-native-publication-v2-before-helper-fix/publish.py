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
encoded = lambda v: (json.dumps(v, indent=2, sort_keys=True) + '\n').encode()


def save(path, value):
    with path.open('xb') as stream:
        stream.write(encoded(value))


def authenticate(directory, pin):
    assert sha(directory / 'FILES.json') == pin
    records = read(directory / 'FILES.json')
    assert {p.name for p in directory.iterdir()} == set(records) | {'FILES.json'}
    for name, record in records.items():
        assert Path(name).name == name and not (directory / name).is_symlink()
        assert sha(directory / name) == record['sha256']
        assert (directory / name).stat().st_size == record['bytes']
    return records


def template(pin):
    records = authenticate(HERE, pin)
    for name, digest in read(HERE / 'INPUTS.json').items():
        assert sha(ROOT / name) == digest, name
    policy = read(HERE / 'POLICY.json')
    assert policy['bindings'] is None and policy['enabled_modes'] == []
    assert (HERE / 'run.py').read_bytes() == (ROOT / 'artifacts/css-log-native-publication-v1/run.py').read_bytes()
    assert (HERE / 'POLICY.json').read_bytes() == (ROOT / 'artifacts/css-log-native-publication-v1/POLICY.json').read_bytes()
    return policy, records


def owner_path(action):
    assert action in ('install', 'commit')
    return ROOT / ('artifacts/css-log-native-publication-' + action + '-v2')


def bind_owner(policy, binding, action, template_pin, records):
    result = copy.deepcopy(policy)
    result['bindings'] = binding
    result['enabled_modes'] = [action]
    for name, record in records.items():
        key = str((HERE / name).relative_to(ROOT))
        assert key not in result['references'] or result['references'][key] == record['sha256']
        result['references'][key] = record['sha256']
    result['references'][str((HERE / 'FILES.json').relative_to(ROOT))] = template_pin
    return result


def create_owner(policy, action):
    directory = owner_path(action)
    directory.mkdir()
    with (directory / 'run.py').open('xb') as stream:
        stream.write((HERE / 'run.py').read_bytes())
    save(directory / 'POLICY.json', policy)
    save(directory / 'FILES.json', {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size}
                                   for p in directory.iterdir()})
    return directory, sha(directory / 'FILES.json')


def execute(directory, action, pin):
    result = subprocess.run([sys.executable, '-I', '-S', '-B', str(directory / 'run.py'), action, pin], cwd=ROOT)
    raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('install', 'delivery', 'commit'))
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--receipt-sha256')
    parser.add_argument('--branch')
    parser.add_argument('--minmax-receipt', type=Path)
    parser.add_argument('--minmax-sha256')
    args = parser.parse_args()
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    policy, records = template(args.manifest)
    if args.action == 'install':
        assert args.receipt and args.receipt_sha256 and args.branch and args.minmax_receipt and args.minmax_sha256
        spec = importlib.util.spec_from_file_location('binding_extract', HERE / 'bindings.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        binding = module.extract(args.receipt, args.receipt_sha256, args.branch, args.minmax_receipt, args.minmax_sha256)
        subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', '-c',
                        'gpg.ssh.allowedSignersFile=' + str(ROOT / policy['allowed_signers']),
                        'verify-commit', binding['head']], cwd=ROOT, check=True)
        directory, pin = create_owner(bind_owner(policy, binding, 'install', args.manifest, records), 'install')
        execute(directory, 'install', pin)
    assert args.receipt is None and args.receipt_sha256 is None and args.branch is None and args.minmax_receipt is None and args.minmax_sha256 is None
    installed = read(ROOT / policy['runtime_output'] / 'INSTALL-RESULT.json')
    directory = owner_path('install')
    authenticate(directory, installed['manifest_sha256'])
    installed_policy = read(directory / 'POLICY.json')
    assert installed_policy == bind_owner(policy, installed_policy['bindings'], 'install', args.manifest, records)
    assert installed['installed'] and not installed['accepted'] and not installed['app_rebuilt']
    if args.action == 'delivery':
        spec = importlib.util.spec_from_file_location('delivery', HERE / 'delivery.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.run(installed_policy, installed['manifest_sha256'])
        return
    delivery = ROOT / policy['runtime_output'] / 'delivery' / 'DELIVERY.json'
    binding = copy.deepcopy(installed_policy['bindings'])
    controls = {name: sha(RUNTIME / name) for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    assert controls['CURRENT-EPOCH.json'] == installed['epoch_sha256']
    binding.update(controls=controls, installation_manifest=installed['manifest_sha256'],
                   delivery_receipt=str(delivery.relative_to(ROOT)), delivery_sha256=sha(delivery))
    directory, pin = create_owner(bind_owner(policy, binding, 'commit', args.manifest, records), 'commit')
    execute(directory, 'commit', pin)


if __name__ == '__main__':
    main()
