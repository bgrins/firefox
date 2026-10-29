import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    policy = read(HERE / 'POLICY.json')
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    if (HERE / 'FILES.json').exists():
        for name, record in read(HERE / 'FILES.json').items():
            assert sha(HERE / name) == record['sha256']
            assert (HERE / name).stat().st_size == record['bytes']
    assert policy['build_enabled'] and not policy['install_enabled'] and not policy['activation_pending']
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    for directory, pin in policy['packages'].items():
        manifest = ROOT / directory / 'FILES.json'
        assert sha(manifest) == pin, directory
        for name, record in read(manifest).items():
            assert sha(manifest.parent / name) == (record['sha256'] if isinstance(record, dict) else record), name
    predecessor = ROOT / 'artifacts/css-hypot-finite-scale-final-build-v2'
    assert (HERE / 'phase.py').read_bytes() == (predecessor / 'phase.py').read_bytes()
    runtime = ROOT / policy['installation_runtime']
    state = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
    assert sha(runtime / 'INSTALLED-EPOCH.json') == sha(state / 'CURRENT-EPOCH.json') == policy['installed_epoch_sha256']
    epoch = read(state / 'CURRENT-EPOCH.json')
    assert sha(state / 'ROLE.json') == policy['role_sha256']
    assert sha(state / 'OWNED.json') == policy['owned_sha256']
    assert epoch['semantic_index']['head'] == policy['head']
    assert epoch['staged_working'] == {}
    for key, value in policy['accepted_preservation_markers'].items():
        assert epoch[key] == value
    for key, value in policy['accepted_transitions'].items():
        assert epoch[key] == value
    assert len(policy['preserved_accepted_payload']) == 28
    for name, record in policy['preserved_accepted_payload'].items():
        expected = policy['source']['candidate_sha256'] if name == policy['source']['path'] else record['sha256']
        assert epoch['pins'][name] == sha(ROOT / name) == expected
        stat = (ROOT / name).stat()
        assert epoch['installed_identities'][name] == record['identity'] == [stat.st_dev, stat.st_ino]
    for name, record in policy['tests'].items():
        assert sha(ROOT / name) == epoch['pins'][name] == record['sha256']
    assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs', policy['source']['path'], policy['deleted_metadata']['path']])
    terminal = read(ROOT / policy['install_terminal'])
    assert terminal['exit'] == 0 and terminal['epoch_sha256'] == policy['installed_epoch_sha256']
    assert terminal['result_sha256'] == sha(runtime / 'INSTALL-RESULT.json')
    result = read(runtime / 'INSTALL-RESULT.json')
    assert result['installed'] and result['preservation_verified'] and not result['compiled'] and not result['accepted']
    assert result['deleted_path'] == policy['deleted_metadata']['path']
    assert set(result['files']) == {policy['source']['path'], *policy['tests']}
    deletion = load('check_deletion', str((HERE / 'deletion.py').relative_to(ROOT)))
    deletion.verify(ROOT, policy, epoch)
    metadata = load('check_metadata', policy['metadata_helper'])
    assert metadata.application_metadata(ROOT / policy['application_ini'], policy['original_build_revision']) == policy['prepared_application_metadata']
    lint = read(ROOT / policy['lint_result'])
    command = read(ROOT / policy['lint_command_receipt'])
    assert lint['exit'] == lint['errors'] == lint['warnings'] == lint['fixed'] == 0
    assert lint['fixture_sha256'] == policy['tests'][lint['fixture_path']]['sha256']
    assert lint['log_sha256'] == sha(ROOT / policy['lint_log'])
    assert command['command'] == policy['lint_command']
    assert command['lint_receipt_sha256'] == sha(ROOT / policy['lint_result'])
    assert not (runtime / policy['build_label']).exists()
    print(json.dumps({'checked': True, 'references': len(policy['references']), 'accepted_claims': 28, 'build_executed': False, 'native_or_canonical_mutation': False}, sort_keys=True))


if __name__ == '__main__':
    main()
