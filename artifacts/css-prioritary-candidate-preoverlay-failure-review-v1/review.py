import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def saved_inventory(pre, app, extra, backup, roles, policy, admission):
    assert pre['controls'] == policy['controls']
    assert set(pre['sources']) == set(roles) and len(roles) == 3
    for name, role in roles.items():
        assert pre['sources'][name] == dict(role, identity=admission['sources'][name]['identity'])
    assert set(extra) == set(policy['extra_backup_paths'])
    expected = {'.', 'app', 'extra'}
    size = 0
    for prefix, rows in [('app', app), ('extra', extra)]:
        mapping = {name: str(index) for index, (name, row) in enumerate(sorted(rows.items())) if row['kind'] == 'file'}
        assert backup[prefix] == mapping
        for name, relative in mapping.items():
            path = prefix + '/' + relative
            expected.add(path)
            row = rows[name]
            saved = backup['owned_inventory'][path]
            assert saved['kind'] == 'file' and saved['nlink'] == 1
            assert saved['identity'] != row['identity']
            assert (saved['sha256'], saved['size']) == (row['sha256'], row['size'])
            size += row['size']
    assert set(backup['owned_inventory']) == expected
    assert all(backup['owned_inventory'][name]['kind'] == 'directory' for name in ('.', 'app', 'extra'))
    assert size == pre['owned_backup_bytes'] == backup['bytes']
    return size


def authenticate():
    config = read(HERE / 'POLICY.json')
    for name, digest in read(HERE / 'REFERENCES.json').items():
        path = ROOT / name
        assert path.is_file() and not path.is_symlink() and sha(path) == digest, name
    owner = ROOT / config['owner_directory']
    assert sha(owner / 'FILES.json') == config['owner_manifest_sha256']
    for name, record in read(owner / 'FILES.json').items():
        assert sha(owner / name) == record['sha256']
    trace = (ROOT / config['trace_path']).read_text()
    assert 'line 111, in main' in trace and 'assert free() >= 27 * 1024**3' in trace
    assert trace.rstrip().endswith('AssertionError')
    receipt = config['terminal_receipt']
    assert sha(ROOT / receipt['path']) == receipt['sha256']
    body = read(ROOT / receipt['path'])
    assert body == receipt['body']
    assert {'session':body['session_id'], **{key:body[key] for key in ('launch_chunk','terminal_chunk','exit')}} == config['reported_terminal']
    assert body['log'] == config['trace_path'] and body['log_sha256'] == sha(ROOT / config['trace_path'])
    return config, owner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    config, owner = authenticate()
    if not args.verify:
        print('Saved owner, pre-overlay receipts and failure trace authenticated; no live checks')
        return
    assert config['execution_enabled']
    baseline = load('preoverlay_baseline', owner / 'baseline.py')
    policy, ownership, roles = baseline.prepare(config['owner_manifest_sha256'])
    assert policy['runtime_output'] == config['runtime_directory']
    pair = ROOT / config['runtime_directory']
    expected_entries = {'CANDIDATE-PRE.json', 'APP-PRE.json', 'EXTRA-PRE.json', 'BACKUPS.json', 'backups'}
    assert not pair.is_symlink() and {path.name for path in pair.iterdir()} == expected_entries
    pre, app, extra, backup = (read(pair / name) for name in ('CANDIDATE-PRE.json', 'APP-PRE.json', 'EXTRA-PRE.json', 'BACKUPS.json'))
    admission = read(ROOT / policy['source_equivalence']['path'])
    size = saved_inventory(pre, app, extra, backup, roles, policy, admission)
    control = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
    lock = control / 'SOURCE-TRANSITION.lock'
    assert not lock.exists() and not lock.is_symlink()
    state, env, controls, epoch, flags, verify = baseline.guard(policy, ownership, roles)
    before = verify()
    assert before == pre['snapshot']
    for name, role in roles.items():
        ownership.claim(ROOT, name, role['base_sha256'], pre['sources'][name]['identity'])
    bundle = load('preoverlay_bundle', ROOT / policy['bundle_helper'])
    assert bundle.scan(ROOT / policy['bundle_path']) == app
    assert {name: bundle.entry(ROOT / name) for name in extra} == extra
    assert bundle.scan(pair / 'backups') == backup['owned_inventory']
    assert verify() == before
    assert not lock.exists() and not lock.is_symlink()
    assert {path.name for path in pair.iterdir()} == expected_entries
    authenticate()
    report = {'terminal': config['reported_terminal'], 'owner_manifest_sha256': config['owner_manifest_sha256'],
              'pre_overlay_unchanged': True, 'snapshot': before, 'controls': pre['controls'],
              'source_claims': pre['sources'], 'application_metadata': policy['prepared_application_metadata'],
              'application_and_extras_exact': True, 'backup_inventory_exact': True, 'owned_backup_bytes': size,
              'backup_inventory_sha256': sha(pair / 'BACKUPS.json'), 'backup_retained': True,
              'build_or_browser_started': False, 'lock_absent': True,
              'backup_deleted_by_reviewer': False, 'canonical_updated': False,
              'input_hashes': read(HERE / 'REFERENCES.json')}
    with (HERE / config['output']).open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'verified': True, 'pre_overlay_unchanged': True, 'owned_backup_bytes': size, 'backup_deleted': False}))


if __name__ == '__main__':
    main()
