import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cleanup', HERE / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rejected = []


def rejects(name, action):
    try:
        action()
    except AssertionError:
        rejected.append(name)
    else:
        raise AssertionError(name)


with tempfile.TemporaryDirectory(prefix='terminal-symbol-check-', dir='/private/tmp') as folder:
    root = Path(folder)
    module.ROOT = root
    bundle = root / 'owned/probe.dSYM'
    file = bundle / 'Contents/body'
    file.parent.mkdir(parents=True)
    file.write_bytes(b'known symbol')
    info = file.stat()
    directory = bundle.stat()
    record = {'path': 'owned/probe.dSYM', 'identity': [directory.st_dev, directory.st_ino], 'files': [{'path': 'Contents/body', 'identity': [info.st_dev, info.st_ino], 'bytes': info.st_size, 'mtime_ns': info.st_mtime_ns, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()}]}
    module.bundle(record, 'owned/')
    rejects('parent traversal', lambda: module.safe_path('../foreign'))
    extra = bundle / 'unexpected'
    extra.write_bytes(b'extra')
    rejects('unexpected member', lambda: module.bundle(record, 'owned/'))
    extra.unlink()
    file.write_bytes(b'other symbol')
    os.utime(file, ns=(info.st_atime_ns, info.st_mtime_ns))
    rejects('changed body same size/mtime', lambda: module.bundle(record, 'owned/'))
    file.write_bytes(b'known symbol')
    os.utime(file, ns=(info.st_atime_ns, info.st_mtime_ns))
    saved = root / 'retained'
    file.rename(saved)
    file.write_bytes(b'known symbol')
    os.utime(file, ns=(info.st_atime_ns, info.st_mtime_ns))
    rejects('foreign inode', lambda: module.bundle(record, 'owned/'))
    file.unlink()
    saved.rename(file)
    link = bundle / 'linked-directory'
    link.symlink_to(root, target_is_directory=True)
    rejects('symlink directory member', lambda: module.bundle(record, 'owned/'))
    link.unlink()
    parent_link = root / 'alias'
    parent_link.symlink_to(root / 'owned', target_is_directory=True)
    rejects('symlink ancestor', lambda: module.safe_path('alias/probe.dSYM'))
    module.bundle(record, 'owned/')
    scratch = str(root)
assert not Path(scratch).exists()
result = {'positive_checks': 2, 'rejected': rejected, 'scratch_removed': True, 'main_executed': False, 'live_guards_run': False}
with (HERE / 'CHECK.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
