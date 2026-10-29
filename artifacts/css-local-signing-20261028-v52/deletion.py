import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

SOURCES = {'layout/base/PresShell.cpp', 'layout/style/RestyleManager.cpp', 'layout/style/RestyleManager.h'}
LANDING = 'testing/web-platform/tests/dom/nodes/moveBefore/sibling-functions-invalidation.html'
DELETED = 'testing/web-platform/meta/dom/nodes/moveBefore/moveBefore-child-list-selector-invalidation.html.ini'


def verify(root, inputs, epoch, native, parent, commit=None):
    sha = lambda body: hashlib.sha256(body).hexdigest()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    def git(*args):
        return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', *args], cwd=root, env=env)
    def path(name):
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        result = root / relative
        assert all(not part.is_symlink() for part in (result, *result.parents) if part != root.parent)
        return result
    assert set(inputs['native_source_paths']) == SOURCES
    assert set(inputs['native_write_pins']) == SOURCES | {LANDING}
    assert set(inputs['deleted_preimages']) == {DELETED}
    assert native['source_pins'] == inputs['native_write_pins']
    assert native['deleted_preimages'] == inputs['deleted_preimages']
    assert native['files'] == sorted(SOURCES | {LANDING, DELETED})
    assert sha(path(native['patch']).read_bytes()) == native['patch_sha256']
    assert not os.path.lexists(root / DELETED)
    assert DELETED in epoch['pins'] and epoch['pins'][DELETED] is None
    assert DELETED not in epoch['installed_identities']
    owned = json.loads((root / 'artifacts/css-registered-number-native-runtime-v1/OWNED.json').read_bytes())
    assert DELETED not in owned
    for name in SOURCES | {DELETED}:
        row = git('ls-tree', parent, '--', name).decode().strip().split()
        assert len(row) == 4 and row[0:2] == ['100644', 'blob'] and row[3] == name
    assert not git('ls-tree', parent, '--', LANDING)
    assert sha(git('show', parent + ':' + DELETED)) == inputs['deleted_preimages'][DELETED]
    receipt_path = inputs['deletion_receipt']
    assert sha(path(receipt_path).read_bytes()) == inputs['evidence_pins'][receipt_path]
    receipt = json.loads(path(receipt_path).read_bytes())
    assert receipt['original_path'] == DELETED
    assert receipt['archived_path'] == inputs['deleted_archive']
    claim = receipt['claim']
    assert claim['path'] == receipt['archived_path']
    assert claim['owned_sha256'] == inputs['deleted_preimages'][DELETED]
    assert claim['identity'] == inputs['deleted_identity']
    archive = path(receipt['archived_path'])
    info = archive.lstat()
    assert stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == claim['identity']
    assert stat.S_IMODE(info.st_mode) == 0o644
    assert sha(archive.read_bytes()) == inputs['deleted_preimages'][DELETED]
    assert epoch['move_before_removal_transition']['deleted_metadata'] == DELETED
    for name, pin in native['source_pins'].items():
        assert sha(path(name).read_bytes()) == pin
    if commit is not None:
        fields = git('diff-tree', '--no-commit-id', '--no-renames', '--name-status', '-r', '-z', commit).split(b'\0')
        assert fields[-1] == b'' and len(fields[:-1]) == 10
        observed = {fields[i + 1].decode(): fields[i].decode() for i in range(0, len(fields) - 1, 2)}
        assert observed == {**{name: 'M' for name in SOURCES}, LANDING: 'A', DELETED: 'D'}
        assert not git('ls-tree', commit, '--', DELETED)
        for name, pin in native['source_pins'].items():
            row = git('ls-tree', commit, '--', name).decode().strip().split()
            assert len(row) == 4 and row[0:2] == ['100644', 'blob'] and row[3] == name
            assert sha(git('show', commit + ':' + name)) == pin
