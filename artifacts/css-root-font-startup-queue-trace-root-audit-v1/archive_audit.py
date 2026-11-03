import hashlib
import importlib.util
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_archive(root, runtime, policy, roles, claims, result, binding):
    records = binding['archive_records']
    assert isinstance(records, dict)
    actual_records = {path.name: sha(path) for path in runtime.glob('ARCHIVE-*.json')}
    assert records == actual_records
    assert set(records) <= {'ARCHIVE-OWNERSHIP.json', 'ARCHIVE-SNAPSHOT.json',
                            'ARCHIVE-VALIDATION.json', 'ARCHIVE-HANDOFF.json',
                            'ARCHIVE-CLEANUP.json', 'ARCHIVE-PUBLICATION-FAILURE.json'}
    base = {'archive_retained_verified': False, 'browser_execution_authorized': False,
            'native_acceptance': False, 'receipt_hashes': records}
    ownership = read(runtime / 'ARCHIVE-OWNERSHIP.json') if 'ARCHIVE-OWNERSHIP.json' in records else None
    cleanup = read(runtime / 'ARCHIVE-CLEANUP.json') if 'ARCHIVE-CLEANUP.json' in records else None
    if ownership is None and cleanup is not None:
        ownership = cleanup.get('ownership')
    directory = None
    if ownership is not None:
        directory = Path(ownership['owned_directory'])
        assert directory.parent == Path('/private/tmp')
        assert directory.name.startswith('css-font-unit-candidate-')
    if not result['success']:
        exists = directory is not None and (directory.exists() or directory.is_symlink())
        if cleanup is not None and cleanup['removed']:
            assert not exists
        return dict(base, status='failed-retained-untrusted' if exists else 'failed-no-recorded-retained-archive',
                    cleanup=cleanup, ownership=ownership,
                    handoff_is_authority=False, owner_error=result['error'])
    assert result['error'] is None and result['publication_errors'] == []
    assert ownership is not None
    assert set(records) == {'ARCHIVE-OWNERSHIP.json', 'ARCHIVE-SNAPSHOT.json',
                            'ARCHIVE-VALIDATION.json', 'ARCHIVE-HANDOFF.json'}
    assert not directory.is_symlink() and directory.is_dir()
    assert [directory.stat().st_dev, directory.stat().st_ino] == ownership['owned_identity']
    snapshot = read(runtime / 'ARCHIVE-SNAPSHOT.json')
    handoff = read(runtime / 'ARCHIVE-HANDOFF.json')
    app = directory / 'Nightly.app'
    assert set(directory.iterdir()) == {app}
    assert snapshot['owned_directory'] == ownership['owned_directory']
    assert snapshot['owned_identity'] == ownership['owned_identity']
    assert Path(snapshot['application']) == app and handoff['application'] == str(app)
    assert snapshot['provisional'] and snapshot['independent_restoration_required']
    assert not snapshot['diagnostic_run_performed']
    assert handoff['owner_terminal_and_independent_audit_required']
    assert handoff['browser_execution_authorized'] is False
    assert handoff['snapshot_sha256'] == sha(runtime / 'ARCHIVE-SNAPSHOT.json')
    assert handoff['restoration_sha256'] == sha(runtime / 'RESTORATION.json')
    assert handoff['post_sha256'] == sha(runtime / 'POST.json')
    build = read(runtime / 'candidate-build/RESULT.json')
    command = read(runtime / 'candidate-build/COMMAND.json')
    expected_sources = {name: role['candidate_sha256'] for name, role in roles.items()}
    assert snapshot['native_sources'] == build['native_sources'] == command['source_sha256'] == expected_sources
    assert command['owner_manifest'] == binding['owner_manifest_sha256']
    assert snapshot['source_role'] == 'candidate' and snapshot['native_head'] == policy['head']
    assert snapshot['build_receipt'] == str((runtime / 'candidate-build/RESULT.json').relative_to(root))
    assert snapshot['build_receipt_sha256'] == sha(runtime / 'candidate-build/RESULT.json')
    assert snapshot['build_command_sha256'] == sha(runtime / 'candidate-build/COMMAND.json')
    assert snapshot['candidate_wpt_outcomes_sha256'] == sha(runtime / 'candidate-OUTCOMES.json')
    assert snapshot['application_metadata'] == build['application_metadata']
    assert snapshot['binaries'] == build['binaries']
    assert snapshot['source_claims'] == {name: [role['candidate_sha256'], *claims[name]['identity']]
                                          for name, role in roles.items()}
    assert snapshot['unchanged_source_preimages'] == {name: pin for name, pin in policy['source_context_pins'].items()
                                                       if name not in roles}
    owner_dir = root / 'artifacts/css-root-font-startup-queue-trace-candidate-browser-v1'
    assert sha(owner_dir / 'archive.py') == binding['references']['artifacts/css-root-font-startup-queue-trace-candidate-browser-v1/archive.py']
    helper = load('actual_archive_inventory', owner_dir / 'archive.py')
    before = helper.inventory(app, False)
    assert before['files'] == snapshot['files'] == snapshot['resolved_source_inventory']['files']
    assert sum(row['bytes'] for row in before['files'].values()) == snapshot['bytes']
    assert all((app / name).stat().st_nlink == 1 and before['identities'][name][:2] != snapshot['resolved_source_inventory']['identities'][name][:2]
               for name in before['files'])
    bundle = Path(policy['bundle_path'])
    archived_binaries = {str(Path(name).relative_to(bundle)): pin for name, pin in build['binaries'].items()
                         if Path(name).is_relative_to(bundle)}
    assert {'Contents/MacOS/firefox', 'Contents/MacOS/XUL'} <= archived_binaries.keys()
    assert all(before['files'][name]['sha256'] == pin for name, pin in archived_binaries.items())
    validation = helper.validate(root, snapshot, policy['archive'])
    assert validation == read(runtime / 'ARCHIVE-VALIDATION.json')
    assert helper.inventory(app, False) == before
    assert [directory.stat().st_dev, directory.stat().st_ino] == ownership['owned_identity']
    assert {path.name: sha(path) for path in runtime.glob('ARCHIVE-*.json')} == records
    return dict(base, status='verified-retained-candidate', archive_retained_verified=True,
                application=str(app), ownership=ownership, validation=validation,
                build_receipt_sha256=snapshot['build_receipt_sha256'], native_sources=expected_sources,
                retained_inventory_sha256=hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
                owner_terminal_and_restoration_verified=True)
