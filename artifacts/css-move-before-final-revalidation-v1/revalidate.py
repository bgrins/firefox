import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
SELF = Path(__file__).resolve().parent
ROOT = SELF.parents[1]
HERE = ROOT / 'artifacts/css-move-before-promotion-v1'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_settings(policy):
    expected = copy.deepcopy(read(ROOT / policy['pair_capsule'] / 'POLICY.json')['wpt'])
    deleted = policy['deleted_metadata']['path']
    expected['metadata'][deleted.removeprefix('testing/web-platform/meta/')] = {'path': deleted, 'sha256': None}
    for name, item in policy['tests'].items():
        expected['resources'][name.removeprefix('testing/web-platform/tests/')] = {'path': name, 'sha256': item['sha256']}
    expected['harness_revision'] = policy['head']
    expected['phase_revisions'] = {'original': policy['head'], 'candidate': policy['head']}
    assert expected == policy['wpt']


def main():
    assert len(sys.argv) == 6
    revalidation_manifest, manifest, epoch_digest, binding_name, binding_digest = sys.argv[1:]
    policy = read(HERE / 'POLICY.json')
    assert policy['final_validation_requires_separate_enabled_binding']
    relative = Path(binding_name)
    assert not relative.is_absolute() and '..' not in relative.parts and relative.parts[0] == 'artifacts'
    assert not (ROOT / relative).is_symlink() and sha(ROOT / relative) == binding_digest
    binding = read(ROOT / relative)
    assert binding['execution_enabled'] is True and binding['head'] == policy['head']
    assert binding['promotion_manifest_sha256'] == manifest
    assert binding['epoch_sha256'] == epoch_digest
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
               MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
               MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    owner = load('move_final_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    owner.authenticate(HERE, manifest)
    owner.authenticate(SELF, revalidation_manifest)
    for name, pin in read(SELF / 'REFERENCES.json').items():
        assert sha(ROOT / name) == pin
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin
    output = ROOT / policy['runtime_output']
    build = output / policy['build_label']
    required = {str((output / name).relative_to(ROOT)) for name in ('INSTALL-RESULT.json','INSTALLED-EPOCH.json','OWNERSHIP.json','DELETION.json')}
    required |= {str((build / name).relative_to(ROOT)) for name in ('RESULT.json','EPOCH.json','build-RESULT.json','APPLICATION-METADATA.json')}
    assert set(binding['evidence']) == required
    for name, pin in binding['evidence'].items():
        assert sha(ROOT / name) == pin
    validate_settings(policy)
    evidence = load('move_final_evidence', HERE / 'evidence.py')
    evidence.verify(ROOT, policy, None, owner)
    state = owner.load_state(RUNTIME)
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    assert {name: hashlib.sha256(body).hexdigest() for name, body in controls.items()} == binding['controls']
    assert sha(RUNTIME / 'CURRENT-EPOCH.json') == epoch_digest
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
    output = ROOT / policy['runtime_output']
    build = output / policy['build_label']
    assert sha(build / 'EPOCH.json') == epoch_digest
    result, inner = read(build / 'RESULT.json'), read(build / 'build-RESULT.json')
    assert result['command_success'] and result['preservation_verified'] and result['error'] is None
    assert result['publication_errors'] == [] and result['owned_processes'] == {} and result['accepted'] is False
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assert inner['error'] is None and inner['stop_reason'] is None
    metadata = load('move_final_metadata', ROOT / policy['metadata_helper'])
    saved_metadata = read(build / 'APPLICATION-METADATA.json')
    assert metadata.application_metadata(ROOT / policy['application_ini'], policy['head']) == saved_metadata
    marker = epoch['move_before_removal_transition']
    assert marker['role'] == 'candidate' and marker['compiled'] and not marker['accepted']
    assert marker['manifest_sha256'] == binding['promotion_manifest_sha256']
    assert marker['variant'] == 'move-before-removal-invalidation' and marker['last_phase'] == policy['build_label']
    assert marker['source_sha256'] == {n:r['candidate_sha256'] for n,r in policy['sources'].items()}
    for name, expected in policy['preserved_markers'].items():
        assert epoch[name] == expected
    assert epoch['pins']['servo/components/style/custom_properties.rs'] == policy['held_provider_sha256']
    claims = read(output / 'OWNERSHIP.json')
    assert set(claims) == set(policy['sources']) | set(policy['tests'])
    for name, record in policy['preserved_accepted_payload'].items():
        assert epoch['pins'][name] == record['sha256'] and epoch['installed_identities'][name] == record['identity']
        owner.claim(ROOT, name, record['sha256'], record['identity'])
    for name, claim in claims.items():
        pin = policy['sources'][name]['candidate_sha256'] if name in policy['sources'] else policy['tests'][name]['sha256']
        assert epoch['pins'][name] == claim['owned_sha256'] == pin
        assert epoch['installed_identities'][name] == claim['identity']
        owner.claim(ROOT, name, pin, claim['identity'])
    deleted = policy['deleted_metadata']['path']
    assert epoch['pins'][deleted] is None and not os.path.lexists(ROOT / deleted)
    assert deleted not in epoch['installed_identities'] and deleted not in json.loads(controls['OWNED.json'])
    deletion = read(output / 'DELETION.json')
    assert deletion['original_path'] == deleted
    owner.claim(ROOT, deletion['archived_path'], policy['deleted_metadata']['sha256'], deletion['claim']['identity'])
    assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs', *policy['sources'], deleted])
    owner.quiescent(RUNTIME)
    owner.quiescent(output)
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    before = state.a.verify_current(state.h, ROOT, env, epoch)
    flags = {name: state.h.git(ROOT / name, env, 'ls-files', '-v', '-z') for name in ('.', 'artifacts/css-spec-lean')}
    def verify():
        assert metadata.application_metadata(ROOT / policy['application_ini'], policy['head']) == saved_metadata
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        assert not os.path.lexists(ROOT / deleted)
        owner.claim(ROOT, deletion['archived_path'], policy['deleted_metadata']['sha256'], deletion['claim']['identity'])
        assert all(state.h.git(ROOT / name, env, 'ls-files', '-v', '-z') == body for name, body in flags.items())
        current = state.a.verify_current(state.h, ROOT, env, epoch)
        assert current == before
        return current
    phase = output / 'candidate-wpt'
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == before
    phase_metadata = dict(saved_metadata, build_revision=policy['head'],
                          harness_revision=policy['head'], source_role='candidate')
    assert read(phase / 'APPLICATION-METADATA.json') == phase_metadata
    assert read(phase / 'APPLICATION-METADATA-POST.json') == phase_metadata
    assert read(phase / 'BINARY-PINS.json') == {name: epoch['pins'][name] for name in policy['rebuilt_binaries']}
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    owner.group_absent(read(phase / 'PROCESS.json')['pgid'])
    replay = load('completed_run_replay', SELF / 'replay.py')
    assessment, differences = replay.replay()
    assert verify() == before
    evidence.verify(ROOT, policy, None, owner)
    assert verify() == before
    owner.authenticate(SELF, revalidation_manifest)
    for name, pin in read(SELF / 'REFERENCES.json').items():
        assert sha(ROOT / name) == pin
    destination = ROOT / 'artifacts/css-move-before-final-revalidation-runtime-1'
    assert not os.path.lexists(destination)
    destination.mkdir()
    owner.save(destination / 'PRE.json', before)
    owner.save(destination / 'REASSESSED-ASSESSMENT.json', assessment)
    owner.save(destination / 'EXACT-DIFF.json', differences)
    owner.save(destination / 'POST.json', verify())
    owner.save(destination / 'RESULT.json', {
        'success': True, 'browser_execution_performed': False,
        'reassessed_actual_completed_run': True, 'preservation_verified': True,
        'original_browser_child_exit': 0, 'original_wrapper_exit': 1,
        'original_wrapper_exit_source': 'root report64291 terminal9d9000/1',
        'original_assessment_sha256': sha(phase / 'ASSESSMENT.json'),
        'original_result_sha256': sha(phase / 'RESULT.json'),
        'raw_sha256': sha(phase / 'raw.jsonl'),
        'revalidation_manifest_sha256': revalidation_manifest,
        'binding_sha256': binding_digest, 'epoch_sha256': epoch_digest,
        'observed_subtests': 70, 'observed_endings': 12,
        'accepted': False, 'historical_records_unchanged': True})


if __name__ == '__main__':
    main()
