import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
source = (HERE / 'run.py').read_text()
main = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == 'main')
outer = next(node for node in main.body if isinstance(node, ast.Try) and node.finalbody)
publication = next(i for i, node in enumerate(main.body) if isinstance(node, ast.If) and 'archive_helper.publish' in ast.get_source_segment(source, node))
tail = main.body[publication:]
assert source.index("archive_helper = load(") < source.index("with lock.open('x')")
spec = importlib.util.spec_from_file_location('actual_archive_helper', HERE / 'archive.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
scratch = Path(tempfile.mkdtemp(prefix='css-archive-publication-check-', dir='/private/tmp'))
results = []


def run_case(label, error, cleanup_error=False, uncaught=False):
    output = scratch / label
    output.mkdir()
    app = output / 'source-app'; app.mkdir()
    (output / 'source').write_bytes(b'restored source')
    backups = output / 'backups'; backups.mkdir(); (backups / 'preserved').write_bytes(b'original backup')
    lock = output / 'lock'; lock.write_text('owned fixture lock')
    directory = Path(tempfile.mkdtemp(prefix='css-font-unit-candidate-', dir='/private/tmp'))
    archive = directory / 'Nightly.app'; archive.mkdir(); (archive / 'file').write_bytes(b'archive')
    record = {'owned_directory': str(directory), 'owned_identity': [directory.stat().st_dev, directory.stat().st_ino],
              'application': str(archive), 'files': helper.inventory(archive, False)['files']}
    saved = []

    def save(path, value):
        helper.save(path, value); saved.append(path.name)

    def publish(value, path):
        if error:
            raise RuntimeError('injected archive publication failure')
        helper.publish(value, path)

    def discard(value):
        if cleanup_error:
            raise AssertionError('injected ownership refusal')
        helper.discard(value)

    scope = {'ROOT': output, 'output': output, 'owned': {}, 'restoration_errors': [], 'stable_controls': lambda: None,
             'touched': [], 'roles': {'source': {}}, 'app': app, 'app_before': {}, 'extra_before': {},
             'backups': backups, 'app_mapping': {}, 'extra_mapping': {}, 'sha': helper.sha,
             'bundle': SimpleNamespace(scan=lambda path: {}, semantic=lambda value: value, restore=lambda *args: None),
             'state': SimpleNamespace(save=save), 'archive_helper': SimpleNamespace(publish=publish, discard=discard),
             'archive_record': record, 'failure': None, 'errors': [], 'phase_result': {'candidate': {'cancellation': {}}},
             'backup_snapshot': {}, 'size': 15, 'lock': lock, 'lock_identity': (lock.stat().st_dev, lock.stat().st_ino),
             'policy': {'provider_source_role': 'fixture candidate', 'head': 'fixture'}, 'shutil': shutil}
    try:
        exec(compile(ast.Module(body=outer.finalbody, type_ignores=[]), '<actual restoration finally>', 'exec'), scope)
        save(output / 'POST.json', {'fixture': 'restored'})
        save(output / 'ARCHIVE-SNAPSHOT.json', record)
        selected = tail
        if uncaught:
            selected = ast.parse('archive_helper.publish(archive_record, output)').body + tail[1:]
        try:
            exec(compile(ast.Module(body=selected, type_ignores=[]), '<actual post-restoration accounting>', 'exec'), scope)
        except (AssertionError, RuntimeError):
            assert error
        if uncaught:
            assert not (output / 'RESULT.json').exists() and lock.exists()
            return
        result = json.loads((output / 'RESULT.json').read_text())
        restoration = json.loads((output / 'RESTORATION.json').read_text())
        cleanup = json.loads((output / 'BACKUP-CLEANUP.json').read_text())
        assert restoration['errors'] == [] and restoration['owned_processes'] == {}
        assert result['restoration_verified'] and result['success'] is (not error)
        assert cleanup['removed'] is (not error) and cleanup['retained_after_failure'] is error
        assert backups.exists() is error and not lock.exists()
        assert saved.index('RESTORATION.json') < saved.index('RESULT.json')
        if error:
            archive_cleanup = json.loads((output / 'ARCHIVE-CLEANUP.json').read_text())
            assert archive_cleanup['removed'] is (not cleanup_error)
            assert directory.exists() is cleanup_error
        results.append({'case': label, 'result_recorded': True, 'restoration_recorded': True,
                        'success': result['success'], 'backup_retained': backups.exists(), 'lock_removed': True})
    finally:
        if directory.exists():
            helper.discard(record)


try:
    run_case('success', False)
    run_case('publication-failure', True)
    run_case('publication-and-cleanup-refusal', True, True)
    run_case('old-uncaught-window-control', True, uncaught=True)
finally:
    shutil.rmtree(scratch)

print(json.dumps({'cases': results, 'uncaught_old_window_control_detected': True,
                  'actual_finally_and_post_restoration_statements_extracted': True,
                  'native_operations': False, 'native_helpers_are_fixture_doubles': True,
                  'scratch_removed': not scratch.exists(), 'source_sha256': hashlib.sha256(source.encode()).hexdigest()}, sort_keys=True))
