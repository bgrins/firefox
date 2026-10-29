import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CAPSULE = ROOT / 'artifacts/css-shadow-move-build-cache-cleanup-v1'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())
assert sha(CAPSULE / 'FILES.json') == 'd4c34becfa871c963337b5e23735c47df40c32843e890bd00d81d5a99e10f730'
for name, pin in read(CAPSULE / 'FILES.json').items():
    assert sha(CAPSULE / name) == pin
inventory = json.loads(gzip.decompress((CAPSULE / 'INVENTORY.json.gz').read_bytes()))
retained = read(CAPSULE / 'RETAINED-EVIDENCE.json')['sha256']
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
controls = {name: (runtime / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
pins = read(runtime / 'CURRENT-EPOCH.json')['pins']
expected_names = {'named-container-candidate-v1', '7ef9ece', 'attached-style-candidate-v1'}
assert {Path(d['path']).parents[1].name for d in inventory['directories']} == expected_names

def verify_retained():
    for name, pin in retained.items():
        assert sha(ROOT / name) == pin
    assert all((runtime / name).read_bytes() == body for name, body in controls.items())

def verify_inventory(directory):
    path = ROOT / directory['path']
    assert path.relative_to(ROOT).parts[:4] == ('artifacts', 'css-spec-lean', '.lake', 'research-review')
    assert path.parts[-2:] == ('.lake', 'build')
    assert all(not p.is_symlink() for p in [path, *path.parents])
    assert not any(name == directory['path'] or name.startswith(directory['path'] + '/') for name in pins)
    actual = {}
    for entry in [path, *path.rglob('*')]:
        info = entry.lstat()
        assert stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
        kind = 'file' if stat.S_ISREG(info.st_mode) else 'directory'
        actual[str(entry.relative_to(path))] = dict(kind=kind, identity=[info.st_dev, info.st_ino], mode=stat.S_IMODE(info.st_mode), size=info.st_size, blocks_512=info.st_blocks, nlink=info.st_nlink, mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)
        if kind == 'file':
            assert info.st_nlink == 1
    expected = {name: {key: value for key, value in row.items() if key != 'retained_source'} for name, row in directory['entries'].items()}
    assert actual == expected
    return path

def no_use(path):
    checkout = path.parents[1]
    result = subprocess.run(['/usr/sbin/lsof', '+D', str(checkout)], capture_output=True, text=True)
    assert result.returncode == 1 and result.stdout == '' and result.stderr == '', (str(checkout), result.returncode, result.stdout, result.stderr)
    return {'checkout': str(checkout), 'lsof_exit': result.returncode, 'no_open_files': True}

verify_retained()
paths = [verify_inventory(d) for d in inventory['directories']]
processes = subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,command='], text=True)
process_rows = [line.strip().split(None, 2) for line in processes.splitlines() if line.strip()]
parents = {int(row[0]): int(row[1]) for row in process_rows}
ancestors = {os.getpid()}
pid = os.getpid()
while pid in parents and parents[pid] not in ancestors:
    pid = parents[pid]
    ancestors.add(pid)
matches = [row for row in process_rows if int(row[0]) not in ancestors and len(row) == 3 and any(str(path.parents[1]) in row[2] or str(path.parents[1].relative_to(ROOT)) in row[2] for path in paths)]
assert not matches, matches
usage = [no_use(path) for path in paths]
free = lambda: os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize
result = {'success': False, 'removed': [], 'allocated_generated_bytes': inventory['total_allocated_file_bytes'], 'free_before': free(), 'process_matches': matches, 'open_file_checks': usage, 'canonical_controls_unchanged': False}
assert not (HERE / 'RESULT.json').exists()
try:
    for directory in inventory['directories']:
        path = verify_inventory(directory)
        no_use(path)
        shutil.rmtree(path)
        assert not os.path.lexists(path)
        result['removed'].append(directory['path'])
    verify_retained()
    result['canonical_controls_unchanged'] = True
    result['success'] = True
finally:
    result['free_after'] = free()
    with (HERE / 'RESULT.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
print(json.dumps(result))
