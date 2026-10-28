import hashlib
import os
from pathlib import Path
import shutil
import stat
import tempfile


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def entry(path):
    info = path.lstat()
    record = {'identity': [info.st_dev, info.st_ino], 'mode': stat.S_IMODE(info.st_mode)}
    if stat.S_ISLNK(info.st_mode):
        record.update(kind='symlink', target=os.readlink(path))
    elif stat.S_ISREG(info.st_mode):
        record.update(kind='file', sha256=sha(path), size=info.st_size, nlink=info.st_nlink)
    else:
        assert stat.S_ISDIR(info.st_mode), str(path)
        record.update(kind='directory')
    return record


def scan(root):
    assert root.is_dir() and not root.is_symlink()
    rows = {'.': entry(root)}
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            rows[str(path.relative_to(root))] = entry(path)
    return rows


def semantic(rows):
    return {name: {k: v for k, v in record.items() if k not in ('identity', 'nlink')}
            for name, record in rows.items()}


def parents(root, path):
    assert root.is_dir() and not root.is_symlink()
    for parent in path.parents:
        if parent == root:
            break
        assert parent.is_relative_to(root) and parent.is_dir() and not parent.is_symlink(), str(parent)


def backup(root, rows, destination):
    assert not destination.exists()
    destination.mkdir()
    mapping = {}
    for index, (name, record) in enumerate(sorted(rows.items())):
        if record['kind'] != 'file':
            continue
        path = root / name
        assert entry(path) == record
        saved = destination / str(index)
        with path.open('rb') as source, saved.open('xb') as target:
            shutil.copyfileobj(source, target, 1024 * 1024)
            target.flush()
            os.fsync(target.fileno())
        assert sha(saved) == record['sha256'] and entry(path) == record
        mapping[name] = str(index)
    return mapping


def restore_file(path, post, saved, original, root):
    parents(root, path)
    assert saved.is_file() and not saved.is_symlink() and sha(saved) == original['sha256']
    assert entry(path) == post if post is not None else not path.exists() and not path.is_symlink()
    descriptor, temporary = tempfile.mkstemp(prefix='.css-lh-restore-', dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, 'wb') as target, saved.open('rb') as source:
            shutil.copyfileobj(source, target, 1024 * 1024)
            target.flush()
            os.fsync(target.fileno())
            os.fchmod(target.fileno(), original['mode'])
        assert sha(temporary) == original['sha256']
        assert entry(path) == post if post is not None else not path.exists() and not path.is_symlink()
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def restore(root, original, post, backups, mapping):
    assert scan(root) == post
    remaining = dict(post)
    for name in sorted(post, key=lambda n: len(Path(n).parts), reverse=True):
        if name == '.' or name in original and original[name]['kind'] == post[name]['kind']:
            continue
        path = root / name
        parents(root, path)
        assert entry(path) == post[name]
        if post[name]['kind'] == 'directory':
            path.rmdir()
        else:
            path.unlink()
        remaining.pop(name)
    for name in sorted(original, key=lambda n: len(Path(n).parts)):
        path, old = root / name, original[name]
        current = remaining.get(name)
        if old['kind'] == 'directory':
            if current is None:
                parents(root, path)
                path.mkdir(mode=old['mode'])
            else:
                assert entry(path) == current
            os.chmod(path, old['mode'])
        elif old['kind'] == 'symlink':
            if current is not None and current['target'] != old['target']:
                parents(root, path)
                assert entry(path) == current
                path.unlink()
                current = None
            if current is None:
                parents(root, path)
                path.symlink_to(old['target'])
            assert path.is_symlink() and os.readlink(path) == old['target']
            if stat.S_IMODE(path.lstat().st_mode) != old['mode']:
                os.lchmod(path, old['mode'])
        elif current is None or current['sha256'] != old['sha256'] or current['mode'] != old['mode']:
            restore_file(path, current, backups / mapping[name], old, root)
        else:
            assert entry(path) == current
    assert semantic(scan(root)) == semantic(original)
