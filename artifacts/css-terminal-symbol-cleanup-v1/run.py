import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
read = lambda p: json.loads(p.read_bytes())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def authenticate():
    assert len(sys.argv) == 2 and sha(HERE / 'FILES.json') == sys.argv[1]
    for name, pin in read(HERE / 'FILES.json')['files'].items():
        assert sha(HERE / name) == pin
    for name, pin in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / name) == pin


def safe_path(name):
    relative = Path(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    path = ROOT / relative
    for item in [path, *path.parents]:
        if item == ROOT:
            break
        assert not item.is_symlink(), item
    return path


def regular(path, record):
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode)
    assert [info.st_dev, info.st_ino] == record['identity']
    assert info.st_size == record['bytes']
    if 'mtime_ns' in record:
        assert info.st_mtime_ns == record['mtime_ns']
    assert sha(path) == record['sha256']


def bundle(record, prefix):
    name = record['path']
    assert name.startswith(prefix) and name.endswith('.dSYM')
    path = safe_path(name)
    info = path.lstat()
    assert stat.S_ISDIR(info.st_mode) and [info.st_dev, info.st_ino] == record['identity']
    files, directories = {}, {name: record['identity']}
    for item in path.rglob('*'):
        info = item.lstat()
        assert not stat.S_ISLNK(info.st_mode)
        if stat.S_ISREG(info.st_mode):
            files[str(item.relative_to(path))] = item
        else:
            assert stat.S_ISDIR(info.st_mode)
            directories[str(item.relative_to(ROOT))] = [info.st_dev, info.st_ino]
    assert set(files) == {x['path'] for x in record['files']}
    for item in record['files']:
        regular(files[item['path']], item)
    return directories


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main():
    authenticate()
    policy = read(HERE / 'POLICY.json')
    assert policy['execution_enabled'] is True
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    inventory = ROOT / policy['inventory']
    for name, pin in read(inventory / 'FILES.json')['files'].items():
        assert sha(inventory / name) == pin
    selected = read(inventory / 'CANDIDATES.json')
    receipts = read(HERE / 'RETAINED-RECEIPTS.json')
    assert {n:r['sha256'] for n,r in receipts.items()} == {n:r['sha256'] for n,r in read(inventory / 'RECEIPTS.json').items()}
    assert len(selected) == policy['expected_bundles'] == 57
    assert sum(len(r['files']) for r in selected) == policy['expected_files'] == 171
    names = [r['path'] for r in selected]
    assert len(set(names)) == len(names)
    assert not any(a != b and a.startswith(b + '/') for a in names for b in names)
    epoch = read(HERE / 'INITIAL-EPOCH.json')
    assert sha(HERE / 'INITIAL-EPOCH.json') == policy['epoch_sha256']
    assert epoch['semantic_index']['head'] == policy['expected_head']
    values = list(strings(epoch))
    assert not any(value == name or value.startswith(name + '/') for value in values for name in names)
    spec = importlib.util.spec_from_file_location('cleanup_state', RUNTIME / 'state.py')
    state = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(state)
    controls = {n: (RUNTIME / n).read_bytes() for n in policy['controls']}
    assert all(hashlib.sha256(body).hexdigest() == policy['controls'][name] for name, body in controls.items())
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    assert not state.h.git(ROOT, ENV, 'ls-files', '-z', '--', *names)
    flags = {str(path): state.h.git(path, ENV, 'ls-files', '-v', '-z') for path in [ROOT, ROOT / 'artifacts/css-spec-lean']}
    for record in selected:
        bundle(record, policy['owned_prefix'])

    def retained():
        for record in selected:
            item = record['retain_executable']
            regular(safe_path(item['path']), item)
        for name, record in receipts.items():
            path = safe_path(name)
            regular(path, record)

    retained()
    output = ROOT / policy['output']
    output.mkdir(exist_ok=False)
    save = lambda name, value: state.save(output / name, value)
    removed = []
    error = None
    preserved = False
    try:
        ps = subprocess.run(['ps', '-axo', 'pid=,ppid=,command='], capture_output=True, text=True)
        opened = subprocess.run(['lsof', '-n', '-P', '-Fpn'], capture_output=True, text=True)
        prefix = policy['owned_prefix']
        process_hits = [line for line in ps.stdout.splitlines() if prefix in line]
        open_hits = [line for line in opened.stdout.splitlines() if line.startswith('n') and prefix in line]
        census = {label: {'exit': result.returncode, 'stdout_lines': len(result.stdout.splitlines()), 'stderr_bytes': len(result.stderr.encode())} for label, result in [('ps', ps), ('lsof', opened)]}
        save('ACTIVE-USE.json', {'census': census, 'process_matches': process_hits, 'open_file_matches': open_hits, 'unrelated_arguments_or_paths_saved': False, 'unrelated_processes_untouched': True})
        for label, result in [('ps', ps), ('lsof', opened)]:
            assert result.returncode == 0 and not result.stderr.strip(), (label, result.returncode, len(result.stderr))
        assert not process_hits and not open_hits
        authenticate()
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
        assert not state.h.git(ROOT, ENV, 'ls-files', '-z', '--', *names)
        assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
        retained()
        save('BEFORE.json', {'snapshot': before, 'selected': selected, 'free_bytes': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize})
        with (output / 'REMOVAL.jsonl').open('x') as journal:
            for record in selected:
                directories = bundle(record, prefix)
                for item in record['files']:
                    name = record['path'] + '/' + item['path']
                    path = safe_path(name)
                    regular(path, item)
                    path.unlink()
                    removed.append(name)
                    journal.write(json.dumps({'removed_file': name}) + '\n')
                    journal.flush()
                    os.fsync(journal.fileno())
                for name in sorted(directories, key=lambda x: len(Path(x).parts), reverse=True):
                    path = safe_path(name)
                    info = path.lstat()
                    assert stat.S_ISDIR(info.st_mode) and [info.st_dev, info.st_ino] == directories[name]
                    path.rmdir()
        assert all(not (ROOT / name).exists() and not (ROOT / name).is_symlink() for name in names)
        retained()
        authenticate()
        assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        assert all(state.h.git(Path(path), ENV, 'ls-files', '-v', '-z') == body for path, body in flags.items())
        preserved = True
    except BaseException as failure:
        error = repr(failure)
        raise
    finally:
        save('RESULT.json', {'success': error is None and preserved, 'error': error, 'removed_files': removed, 'preservation_verified': preserved, 'partial_removal_requires_review': bool(error and removed), 'rollback_available': False, 'allocated_bytes_estimate': policy['allocated_bytes_estimate'], 'free_bytes_after': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize, 'native_or_control_writes': False})
    print('Removed exactly57 obsolete symbol bundles; executables, receipts, source, controls and indexes preserved')


if __name__ == '__main__':
    main()
