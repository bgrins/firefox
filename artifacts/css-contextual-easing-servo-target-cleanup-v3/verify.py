import hashlib
import json
import os
from pathlib import Path
import runpy
import stat
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
proposal = read(HERE / 'PROPOSAL.json')
assert sha(HERE / proposal['inventory']) == proposal['inventory_sha256']
assert sha(HERE / 'PRESERVED-RECEIPTS.json') == proposal['preserved_receipts_sha256']
for name, expected in read(HERE / 'PRESERVED-RECEIPTS.json').items():
    assert sha(ROOT / name) == expected, name
for process in proposal['processes']:
    assert sha(ROOT / process['receipt']) == process['sha256']
    try:
        os.killpg(process['pgid'], 0)
    except ProcessLookupError:
        pass
    else:
        raise AssertionError(('Recorded process group exists', process['pgid']))
completion = ROOT / proposal['completion']
assert sha(completion / 'FILES.json') == proposal['completion_seal']
for name, expected in read(completion / 'FILES.json').items():
    assert sha(completion / name) == expected, name
result = read(ROOT / 'artifacts/css-contextual-easing-servo-compile-runtime-5/RESULT.json')
assert result['success'] and result['owned_processes_absent']
assert result['failure'] is None and result['preservation_error'] is None
assert set(result['phases']) == {'baseline', 'candidate'}
assert all(p['exit'] == 0 and p['owned_group_absent'] and p['cleanup_error'] is None for p in result['phases'].values())
prior_argv = sys.argv
try:
    sys.argv = [str(completion / 'audit_warnings.py'), '--check']
    runpy.run_path(str(completion / 'audit_warnings.py'))
finally:
    sys.argv = prior_argv
inventory = read(HERE / proposal['inventory'])
target = ROOT / proposal['target']
assert target == ROOT / 'artifacts/css-contextual-easing-servo-compile-runtime-5/target'
assert target.is_dir() and not target.is_symlink() and target.resolve() == target
assert [target.stat().st_dev, target.stat().st_ino] == proposal['target_identity'] == inventory['identity']
actual = {}
for directory, dirs, names in os.walk(target, followlinks=False):
    for name in dirs + names:
        path = Path(directory) / name
        info = path.lstat()
        assert stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
        row = {'identity': [info.st_dev, info.st_ino], 'mode': stat.S_IMODE(info.st_mode),
               'size': info.st_size, 'mtime_ns': info.st_mtime_ns,
               'kind': 'file' if stat.S_ISREG(info.st_mode) else 'directory'}
        if row['kind'] == 'file':
            assert info.st_nlink == 1
            row.update(sha256=sha(path), allocated_bytes=info.st_blocks * 512)
        actual[path.relative_to(target).as_posix()] = row
assert actual == inventory['entries']
print('Runtime5 inventory, five absent process groups, preserved receipts and complete retained-source warning audit verified; no deletion performed')
