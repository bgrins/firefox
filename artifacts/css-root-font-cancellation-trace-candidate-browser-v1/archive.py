import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def inventory(app, resolved):
    files, identities, links, directories = {}, {}, {}, {}

    def visit(folder, ancestors):
        real = folder.resolve(strict=True)
        assert real not in ancestors, 'directory symlink cycle'
        info = folder.stat()
        directories[str(folder.relative_to(app))] = [info.st_dev, info.st_ino, stat.S_IMODE(info.st_mode), str(real)]
        for path in sorted(folder.iterdir()):
            name = str(path.relative_to(app))
            if path.is_symlink():
                assert resolved, 'archive contains a symlink'
                info = path.lstat()
                links[name] = [info.st_dev, info.st_ino, os.readlink(path)]
            info = path.stat()
            if stat.S_ISDIR(info.st_mode):
                visit(path, ancestors | {real})
            else:
                assert stat.S_ISREG(info.st_mode), 'nonregular archive input'
                files[name] = {'bytes': info.st_size, 'mode': stat.S_IMODE(info.st_mode), 'sha256': sha(path)}
                identities[name] = [info.st_dev, info.st_ino, str(path.resolve(strict=True))]

    assert not app.is_symlink() and app.is_dir()
    visit(app, set())
    return {'files': files, 'identities': identities, 'links': links, 'directories': directories}


def discard(record):
    directory = Path(record['owned_directory'])
    assert directory.parent == Path('/private/tmp') and directory.name.startswith('css-font-unit-candidate-')
    assert not directory.is_symlink()
    assert [directory.stat().st_dev, directory.stat().st_ino] == record['owned_identity']
    assert set(directory.iterdir()) <= {directory / 'Nightly.app'}
    app = directory / 'Nightly.app'
    current = inventory(app, False) if app.exists() else None
    if record.get('files') is not None:
        assert current is not None and current['files'] == record['files']
    assert (inventory(app, False) if app.exists() else None) == current
    shutil.rmtree(directory)
    assert not directory.exists()


def validate(root, record, settings):
    path = root / settings['validator']
    assert sha(path) == settings['validator_sha256']
    spec = importlib.util.spec_from_file_location('retained_archive_validator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = {'archive_application': record['application'], 'archive_role': 'candidate',
              'native_sources': record['native_sources'], 'archive_files': len(record['files']),
              'build_revision': record['native_head']}
    return module.archive(record, policy)


def create(root, app, output, policy, roles, claims, verify, cancelled):
    settings = policy['archive']
    assert settings['temporary_parent'] == '/private/tmp'
    assert settings['prefix'] == 'css-font-unit-candidate-' and settings['application_name'] == 'Nightly.app'
    assert settings['minimum_free_after_copy'] == 27 * 1024**3
    before = verify()
    build = output / 'candidate-build/RESULT.json'
    receipt_bytes = build.read_bytes()
    receipt = json.loads(receipt_bytes)
    assert receipt['command_success'] and receipt['browser_build_performed'] and receipt['preservation_verified']
    assert receipt['error'] is None and receipt['snapshot'] == before
    assert receipt['native_sources'] == {name: role['candidate_sha256'] for name, role in roles.items()}
    metadata = receipt['application_metadata']
    assert metadata['source_role'] == 'candidate' and metadata['revision'] == policy['head']
    assert sha(app / 'Contents/Resources/application.ini') == metadata['sha256']
    sources = {name: [sha(root / name), (root / name).stat().st_dev, (root / name).stat().st_ino] for name in roles}
    assert all(value == [roles[name]['candidate_sha256'], *claims[name]['identity']] for name, value in sources.items())
    assert all(sha(root / name) == pin for name, pin in receipt['binaries'].items())
    original = inventory(app, True)
    total = sum(row['bytes'] for row in original['files'].values())
    available = os.statvfs('/private/tmp')
    assert available.f_bavail * available.f_frsize >= total + settings['minimum_free_after_copy']
    assert not cancelled()
    directory = Path(tempfile.mkdtemp(prefix=settings['prefix'], dir=settings['temporary_parent']))
    record = {'owned_directory': str(directory), 'owned_identity': [directory.stat().st_dev, directory.stat().st_ino]}
    try:
        save(output / 'ARCHIVE-OWNERSHIP.json', record)
        destination = directory / settings['application_name']
        shutil.copytree(app, destination, symlinks=False)
        assert not cancelled()
        copied = inventory(destination, False)
        assert copied['files'] == original['files']
        assert all((destination / name).stat().st_nlink == 1 and copied['identities'][name][:2] != original['identities'][name][:2] for name in copied['files'])
        assert inventory(app, True) == original
        assert sources == {name: [sha(root / name), (root / name).stat().st_dev, (root / name).stat().st_ino] for name in roles}
        assert build.read_bytes() == receipt_bytes
        assert all(sha(root / name) == pin for name, pin in receipt['binaries'].items())
        assert sha(app / 'Contents/Resources/application.ini') == metadata['sha256']
        assert verify() == before and not cancelled()
        record.update(application=str(destination), files=copied['files'], bytes=total,
                      source_role='candidate', native_head=policy['head'], native_sources=receipt['native_sources'],
                      build_receipt=str(build.relative_to(root)), build_receipt_sha256=sha(build),
                      application_metadata=metadata, binaries=receipt['binaries'], source_claims=sources,
                      build_command_sha256=sha(output / 'candidate-build/COMMAND.json'),
                      candidate_wpt_outcomes_sha256=sha(output / 'candidate-OUTCOMES.json'),
                      unchanged_source_preimages={name: policy['source_context_pins'][name] for name in
                          ('servo/ports/geckolib/glue.rs', 'servo/components/style/custom_properties.rs')},
                      resolved_source_inventory=original, provisional=True,
                      independent_restoration_required=True, diagnostic_run_performed=False)
        validation = validate(root, record, settings)
        save(output / 'ARCHIVE-SNAPSHOT.json', record)
        save(output / 'ARCHIVE-VALIDATION.json', validation)
        return record
    except BaseException as exc:
        try:
            discard(record)
            save(output / 'ARCHIVE-CLEANUP.json', {'removed': True, 'error': repr(exc)})
        except BaseException as cleanup_error:
            save(output / 'ARCHIVE-CLEANUP.json', {'removed': False, 'error': repr(exc), 'cleanup_error': repr(cleanup_error), 'ownership': record})
        raise


def publish(record, output):
    assert record is not None
    assert inventory(Path(record['application']), False)['files'] == record['files']
    restoration = json.loads((output / 'RESTORATION.json').read_bytes())
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    save(output / 'ARCHIVE-HANDOFF.json', {'snapshot_sha256': sha(output / 'ARCHIVE-SNAPSHOT.json'),
         'restoration_sha256': sha(output / 'RESTORATION.json'), 'post_sha256': sha(output / 'POST.json'),
         'application': record['application'], 'owner_terminal_and_independent_audit_required': True,
         'browser_execution_authorized': False})
