import hashlib
import json
import os
from pathlib import Path
import runpy
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
proposal = read(HERE / 'PROPOSAL.json')
assert sha(HERE / 'TARGET-INVENTORY.json') == proposal['target_inventory_sha256']
assert sha(HERE / 'RETAINED-EVIDENCE.json') == proposal['retained_evidence_sha256']
for key in ('runtime2_result', 'root_terminal'):
    entry = proposal[key]
    assert sha(ROOT / entry['path']) == entry['sha256']
result = read(ROOT / proposal['runtime2_result']['path'])
assert result['candidate_skipped'] and result['owned_processes_absent']
assert result['failure'] is None and result['preservation_error'] is None
assert result['phases']['baseline']['exit'] == 101
assert result['phases']['baseline']['owned_group_absent']
assert result['phases']['baseline']['cleanup_error'] is None
for process in proposal['processes']:
    assert sha(ROOT / process['process_receipt']) == process['sha256']
    try:
        os.killpg(process['pgid'], 0)
    except ProcessLookupError:
        pass
    else:
        raise AssertionError(('Process group exists', process['pgid']))
retained = read(HERE / 'RETAINED-EVIDENCE.json')
assert sha(ROOT / retained['retained_path']) == retained['sha256']
for key in ('sealed_auditor', 'sealed_audit'):
    entry = retained[key]
    assert sha(ROOT / entry['path']) == entry['sha256']
runpy.run_path(str(HERE / 'audit_retained.py'))
inventory = read(HERE / 'TARGET-INVENTORY.json')
target = ROOT / inventory['target']
assert target == ROOT / 'artifacts/css-contextual-easing-servo-compile-runtime-2/target'
assert target.is_dir() and not target.is_symlink() and target.resolve() == target
assert [target.stat().st_dev, target.stat().st_ino] == inventory['identity']
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
print('Runtime2 target matches the owned inventory; retained literal-audit replay passes; no deletion performed')
