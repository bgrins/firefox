import hashlib
import json
from pathlib import Path


def external_inputs(root, policy, roles):
    result = dict(policy['references'])
    def add(path, pin):
        assert not Path(path).is_absolute() and '..' not in Path(path).parts
        assert path not in result or result[path] == pin
        result[path] = pin
    for key in ('typecheck_binding', 'source_binding', 'capture_owner', 'capture_source_owner', 'predecessor_binding', 'native_owner_binding'):
        binding = policy[key]
        if binding is None:
            assert key in ('capture_owner', 'native_owner_binding') and not policy['execution_enabled'] and policy['activation_pending']
            continue
        path = root / binding['directory'] / 'FILES.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == binding['manifest_sha256']
        add(str(path.relative_to(root)), binding['manifest_sha256'])
        inventory = json.loads(path.read_bytes())
        for name, record in inventory.get('files', inventory).items():
            add(str((path.parent / name).relative_to(root)), record if isinstance(record, str) else record['sha256'])
    for binding in policy['suite_bindings'].values():
        path = root / binding['directory'] / 'FILES.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == binding['manifest_sha256']
        add(str(path.relative_to(root)), binding['manifest_sha256'])
        inventory = json.loads(path.read_bytes())
        for name, record in inventory.get('files', inventory).items():
            add(str((path.parent / name).relative_to(root)), record if isinstance(record, str) else record['sha256'])
    for record in roles.values():
        for kind in ('base', 'candidate'):
            add(record[kind + '_capture'], record[kind + '_sha256'])
    for settings in policy['wpt_lanes'].values():
        for group in ('resources', 'install_managed_resources', 'manifests'):
            for record in settings[group].values():
                add(record['path'], record['sha256'])
        for records in settings['metadata'].values():
            for record in records.values():
                if record['path'] is not None:
                    add(record['path'], record['sha256'])
                else:
                    assert record['sha256'] is None and record['require_absent_in_staged_root'] is True
        add(settings['server_config']['path'], settings['server_config']['sha256'])
        if settings['capture'] is not None:
            add(settings['capture']['path'], settings['capture']['sha256'])
    for path, pin in policy['required_typecheck_inputs'].items():
        add(path, pin)
    for path, pin in policy['metadata_current_pins'].items():
        add(path, pin)
    for path in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        add(path, None)
    if policy['current_binding'] is not None:
        add(policy['current_binding']['path'], policy['current_binding']['sha256'])
        capture = json.loads((root / policy['current_binding']['path']).read_bytes())
        add(capture['checkpoint_receipt']['path'], capture['checkpoint_receipt']['sha256'])
    assert not any(path.startswith(policy['owner_directory'] + '/') for path in result)
    return result


def require_epoch_coverage(epoch, policy):
    paths = {'mozconfig', 'testing/profiles/profiles.json'}
    paths.update(settings['wpt_config'] for settings in policy['wpt_lanes'].values())
    paths.update(settings['server_config']['path'] for settings in policy['wpt_lanes'].values())
    assert all(path in epoch['pins'] and epoch['pins'][path] is not None for path in paths)
    assert all(epoch['pins'][settings['server_config']['path']] == settings['server_config']['sha256']
               for settings in policy['wpt_lanes'].values())
