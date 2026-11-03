import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = load('actual_archive', HERE / 'archive.py')
validator_path = ROOT / 'artifacts/css-root-self-smil-archived-original-v1/run.py'
validator = load('actual_archive_validator', validator_path)
original_validate = helper.validate
original_copy = shutil.copytree
scratch = Path(tempfile.mkdtemp(prefix='css-archive-seam-check-', dir='/private/tmp'))
owned_archives = []
passed = []


def fixture(label):
    root = scratch / label
    app = root / 'obj/Nightly.app'
    output = root / 'runtime'
    output.mkdir(parents=True)
    (output / 'candidate-build').mkdir()
    (app / 'Contents/MacOS').mkdir(parents=True)
    (app / 'Contents/Resources').mkdir()
    (root / 'data').write_bytes(b'candidate data')
    (root / 'traversal').write_bytes(b'candidate traversal')
    (root / 'app.ini').write_bytes(b'build metadata')
    (root / 'resource').mkdir()
    (root / 'resource/item').write_bytes(b'resource')
    (app / 'Contents/Resources/application.ini').symlink_to(root / 'app.ini')
    (app / 'Contents/Resources/shared').symlink_to(root / 'resource', target_is_directory=True)
    (app / 'Contents/MacOS/firefox').write_bytes(b'not an executable browser')
    (app / 'Contents/MacOS/firefox').chmod(0o751)
    roles = {name: {'candidate_sha256': helper.sha(root / name)} for name in ('data', 'traversal')}
    claims = {name: {'identity': [(root / name).stat().st_dev, (root / name).stat().st_ino]} for name in roles}
    before = {'fixture': label}
    receipt = {'command_success': True, 'browser_build_performed': True, 'preservation_verified': True,
               'error': None, 'snapshot': before, 'native_sources': {name: row['candidate_sha256'] for name, row in roles.items()},
               'application_metadata': {'source_role': 'candidate', 'revision': 'fixture-head', 'sha256': helper.sha(root / 'app.ini')},
               'binaries': {'obj/Nightly.app/Contents/MacOS/firefox': helper.sha(app / 'Contents/MacOS/firefox')}}
    helper.save(output / 'candidate-build/RESULT.json', receipt)
    helper.save(output / 'candidate-build/COMMAND.json', {'fixture_build': True})
    helper.save(output / 'candidate-OUTCOMES.json', {'fixture_complete_observation': True})
    policy = {'head': 'fixture-head', 'archive': {'temporary_parent': '/private/tmp', 'prefix': 'css-font-unit-candidate-',
              'application_name': 'Nightly.app', 'minimum_free_after_copy': 27 * 1024**3}}
    policy['source_context_pins'] = {'servo/ports/geckolib/glue.rs': 'fixture-only', 'servo/components/style/custom_properties.rs': 'fixture-only'}

    def validate(test_root, record, settings):
        validator.ROOT = test_root
        return validator.archive(record, {'archive_application': record['application'], 'archive_role': 'candidate',
             'native_sources': record['native_sources'], 'archive_files': len(record['files']), 'build_revision': 'fixture-head'})

    helper.validate = validate
    return root, app, output, policy, roles, claims, lambda: before, lambda: False


def rejected(label, arrange):
    args = fixture(label)
    args = arrange(args) or args
    try:
        helper.create(*args)
    except (AssertionError, RuntimeError):
        owner_file = args[2] / 'ARCHIVE-OWNERSHIP.json'
        if owner_file.exists():
            record = json.loads(owner_file.read_text())
            owned_archives.append(Path(record['owned_directory']))
            assert not Path(record['owned_directory']).exists()
            assert json.loads((args[2] / 'ARCHIVE-CLEANUP.json').read_text())['removed']
        passed.append(label)
    else:
        raise AssertionError('negative admitted: ' + label)
    finally:
        shutil.copytree = original_copy


try:
    args = fixture('positive')
    record = helper.create(*args)
    owned_archives.append(Path(record['owned_directory']))
    assert len(record['files']) == 3
    assert record['files']['Contents/MacOS/firefox']['mode'] == 0o751
    assert not helper.inventory(Path(record['application']), False)['links']
    (args[0] / 'resource/item').write_bytes(b'changed after copy')
    assert (Path(record['application']) / 'Contents/Resources/shared/item').read_bytes() == b'resource'
    helper.save(args[2] / 'RESTORATION.json', {'errors': [], 'owned_processes': {}})
    helper.save(args[2] / 'POST.json', {'fixture_restored': True})
    helper.publish(record, args[2])
    assert json.loads((args[2] / 'ARCHIVE-HANDOFF.json').read_text())['owner_terminal_and_independent_audit_required']
    helper.discard(record)
    passed.append('dereferenced complete copy, modes, independence, unchanged validator and provisional handoff')

    def partial(args):
        def copier(source, target, **kwargs):
            target.mkdir()
            (target / 'partial').write_bytes(b'partial')
        shutil.copytree = copier
    rejected('incomplete-copy', partial)

    def failed(args):
        def copier(source, target, **kwargs):
            target.mkdir()
            raise RuntimeError('injected copy error')
        shutil.copytree = copier
    rejected('copy-error', failed)

    def changed_mode(args):
        def copier(source, target, **kwargs):
            shutil.copytree = original_copy
            original_copy(source, target, **kwargs)
            (target / 'Contents/MacOS/firefox').chmod(0o600)
        shutil.copytree = copier
    rejected('wrong-mode', changed_mode)

    def replaced_source(args):
        def copier(source, target, **kwargs):
            shutil.copytree = original_copy
            original_copy(source, target, **kwargs)
            path = args[0] / 'data'
            replacement = path.with_name('new-data')
            replacement.write_bytes(path.read_bytes())
            replacement.replace(path)
        shutil.copytree = copier
    rejected('same-byte-source-inode-replacement', replaced_source)

    def cancelled(args):
        calls = [0]
        def stop():
            calls[0] += 1
            return calls[0] > 1
        return (*args[:-1], stop)
    rejected('cancellation-after-copy', cancelled)

    def bad_receipt(args):
        file = args[2] / 'candidate-build/RESULT.json'
        body = json.loads(file.read_text()); body['native_sources']['data'] = '0' * 64
        file.write_text(json.dumps(body))
    rejected('wrong-build-source', bad_receipt)

    def cycle(args):
        (args[1] / 'Contents/loop').symlink_to(args[1], target_is_directory=True)
    rejected('directory-symlink-cycle', cycle)

    args = fixture('cleanup-guards')
    record = helper.create(*args); directory = Path(record['owned_directory']); owned_archives.append(directory)
    bad = copy.deepcopy(record); bad['owned_identity'][1] += 1
    try:
        helper.discard(bad)
    except AssertionError:
        passed.append('wrong-owned-inode-reject')
    else:
        raise AssertionError('wrong-owned-inode admitted')
    changed = Path(record['application']) / 'Contents/MacOS/firefox'
    old_bytes = changed.read_bytes(); changed.write_bytes(b'foreign changed file')
    try:
        helper.discard(record)
    except AssertionError:
        passed.append('changed-archive-inventory-reject')
    else:
        raise AssertionError('changed archive admitted')
    changed.write_bytes(old_bytes)
    helper.discard(record)

    parent = (ROOT / 'artifacts/css-root-font-cancellation-candidate-browser-v2/run.py').read_text()
    candidate = (HERE / 'run.py').read_text()
    def finalbody(source):
        tree = ast.parse(source)
        return ast.dump(next(node for node in ast.walk(tree) if isinstance(node, ast.Try) and node.finalbody), include_attributes=False).split('finalbody=', 1)[1]
    assert finalbody(parent) == finalbody(candidate)
    assert (HERE / 'phases.py').read_bytes() == (ROOT / 'artifacts/css-root-font-cancellation-candidate-browser-v2/phases.py').read_bytes()
finally:
    shutil.copytree = original_copy
    helper.validate = original_validate
    for directory in owned_archives:
        assert not directory.exists(), directory
    shutil.rmtree(scratch)

print(json.dumps({'checks': passed, 'original_finally_and_eight_case_phase_unchanged': True,
      'scratch': str(scratch), 'scratch_removed': not scratch.exists(), 'owned_archives_removed': len(owned_archives),
      'real_native_build_or_browser': False, 'fixture_receipts_are_test_doubles': True,
      'production_validator_body_reused_with_only_fixture_ROOT': True}, sort_keys=True))
