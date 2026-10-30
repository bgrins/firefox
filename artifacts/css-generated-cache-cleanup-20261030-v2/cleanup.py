import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TARGETS = [
    ROOT / 'objdir-full.noindex/debug/incremental',
    ROOT / 'objdir-full.noindex/aarch64-apple-darwin/debug/incremental',
]
CUTOFF = datetime.datetime(2026, 10, 17, tzinfo=datetime.timezone.utc).timestamp()


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def quiescent():
    rows = subprocess.check_output(['ps', '-axo', 'pid=,comm='], text=True)
    busy = []
    for line in rows.splitlines():
        pid, executable = line.strip().split(None, 1)
        if Path(executable).name in {'cargo', 'rustc', 'sccache', 'make', 'gmake', 'ninja'}:
            busy.append({'pid': int(pid), 'executable': executable})
    assert not busy, busy


def record(path):
    info = path.lstat()
    assert info.st_uid == os.getuid()
    assert stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode), str(path)
    assert info.st_mtime < CUTOFF, str(path)
    return {'path': str(path.relative_to(ROOT)), 'identity': [info.st_dev, info.st_ino],
            'bytes': info.st_size, 'mode': info.st_mode, 'mtime_ns': info.st_mtime_ns}


quiescent()
assert not (ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock').exists()
controls = {}
for name in ['CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json']:
    path = ROOT / 'artifacts/css-registered-number-native-runtime-v1' / name
    body = path.read_bytes()
    assert b'debug/incremental' not in body
    controls[name] = hashlib.sha256(body).hexdigest()
inventory = []
for path in TARGETS:
    assert path.resolve() == path and not path.is_symlink()
    inventory.append(record(path))
    inventory.extend(record(child) for child in sorted(path.rglob('*')))
save('INVENTORY.json', inventory)
before = shutil.disk_usage(ROOT).free
quiescent()
for row in inventory:
    assert record(ROOT / row['path']) == row
for path in TARGETS:
    shutil.rmtree(path)
assert all(not path.exists() for path in TARGETS)
for name, digest in controls.items():
    path = ROOT / 'artifacts/css-registered-number-native-runtime-v1' / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
after = shutil.disk_usage(ROOT).free
result = {'removed': [str(path.relative_to(ROOT)) for path in TARGETS],
          'logical_file_bytes': sum(row['bytes'] for row in inventory if stat.S_ISREG(row['mode'])),
          'latest_modified': max(row['mtime_ns'] for row in inventory),
          'free_bytes_before': before, 'free_bytes_after': after,
          'canonical_controls_unchanged': controls,
          'scope': 'Regenerable debug-profile Rust incremental cache only; release caches and binaries retained'}
save('RESULT.json', result)
print(json.dumps(result))
