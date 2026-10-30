import hashlib
import json
from pathlib import Path


RUNTIME_MODULES = (
    'artifacts/css-round-context-quotient-reversible-pair-v2/bundle.py',
    'artifacts/css-registered-number-source-transition-v4/transition.py',
    'artifacts/css-shadow-move-promotion-v1/phase.py',
    'artifacts/css-registered-number-native-runtime-v1/process_control.py',
    'artifacts/css-registered-number-native-runtime-v1/state.py',
    'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py',
    'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py',
    'artifacts/css-counter-scope-append-comparison-execution-v1/compare.py',
    'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py',
    'artifacts/css-keyframe-typed-attribute-demand-runtime-v1/process_control.py',
    'artifacts/css-round-context-quotient-paired-wpt-runner-v2/run.py',
    'artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py',
)


def external_inputs(root, policy, roles):
    result = dict(policy['references'])

    def add(path, digest):
        assert not Path(path).is_absolute() and '..' not in Path(path).parts
        assert path not in result or result[path] == digest, path
        result[path] = digest

    bindings = [policy[key] for key in ('predecessor', 'candidate_lifecycle_predecessor', 'proposal', 'suite_binding', 'capture_binding', 'intermediate_guard_binding')]
    bindings.extend(policy['target_evidence'].values())
    if policy['baseline_binding'] is not None:
        bindings.append({'directory':policy['baseline_capsule']['directory'],'manifest_sha256':policy['baseline_capsule']['sha256']})
        bindings.append(policy['baseline_binding'])
    if policy['restoration_binding'] is not None:
        bindings.append(policy['restoration_binding'])
    if policy['disabled_preimage'] is not None:
        bindings.append(policy['disabled_preimage'])
    if policy['execution_handoff'] is not None:
        bindings.append({'directory':policy['execution_handoff']['reviewer_directory'],'manifest_sha256':policy['execution_handoff']['reviewer_manifest_sha256']})
    for binding in bindings:
        manifest = root / binding['directory'] / 'FILES.json'
        body = manifest.read_bytes()
        assert hashlib.sha256(body).hexdigest() == binding['manifest_sha256']
        add(str(manifest.relative_to(root)), binding['manifest_sha256'])
        for name, record in json.loads(body).items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            add(str((manifest.parent / name).relative_to(root)), record['sha256'])
    for name in RUNTIME_MODULES:
        assert name in policy['references'], name
    for role in roles.values():
        for kind in ('base', 'candidate'):
            add(role[kind + '_capture'], role[kind + '_sha256'])
    for settings in policy['wpt_lanes'].values():
        for group in ('resources', 'install_managed_resources', 'manifests'):
            for record in settings[group].values():
                add(record['path'], record['sha256'])
        for records in settings['metadata'].values():
            for record in records.values():
                add(record['path'], record['sha256'])
        add(settings['server_config']['path'], settings['server_config']['sha256'])
        if settings['capture'] is not None:
            add(settings['capture']['path'], settings['capture']['sha256'])
    for path, digest in policy['metadata_current_pins'].items():
        add(path, digest)
    for path in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
        add(path, None)
    for path in (policy['source_equivalence']['path'], policy['native_checkpoint']['path'],
                 *policy['closed_process_receipts'],
                 *(policy['original_build'][key] for key in ('epoch', 'result', 'inner_result', 'application_metadata'))):
        assert path in result, path
    assert not any(path.startswith(policy['owner_directory'] + '/') for path in result)
    return result


def require_epoch_coverage(epoch, policy):
    paths = {'mozconfig', 'testing/profiles/profiles.json'}
    paths.update(settings['wpt_config'] for settings in policy['wpt_lanes'].values())
    paths.update(settings['server_config']['path'] for settings in policy['wpt_lanes'].values())
    assert all(path in epoch['pins'] and epoch['pins'][path] is not None for path in paths)
    assert all(epoch['pins'][settings['server_config']['path']] == settings['server_config']['sha256']
               for settings in policy['wpt_lanes'].values())
