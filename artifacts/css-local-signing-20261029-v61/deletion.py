import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess


def verify(root, pending, epoch, owned, parent):
    removed = pending["deleted_metadata"]
    name = removed["path"]
    assert name == "testing/web-platform/meta/css/css-values/hypot-pow-sqrt-computed.html.ini"
    assert not os.path.lexists(root / name)
    assert name in epoch["pins"] and epoch["pins"][name] is None
    assert name not in epoch["installed_identities"] and name not in owned
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args], cwd=root, env=env)
    sha = lambda body: hashlib.sha256(body).hexdigest()
    row = git("ls-tree", parent, "--", name).decode().strip().split()
    assert len(row) == 4 and row[:2] == ["100644", "blob"] and row[3] == name
    assert sha(git("show", parent + ":" + name)) == removed["sha256"]
    stage = git("ls-files", "--stage", "--", name).decode().strip().split()
    assert len(stage) == 4 and stage[0] == "100644" and stage[2] == "0" and stage[3] == name
    assert sha(git("show", ":" + name)) == removed["sha256"]
    receipt = root / removed["receipt"]
    assert sha(receipt.read_bytes()) == removed["receipt_sha256"]
    record = json.loads(receipt.read_bytes())
    assert record["original_path"] == name and record["archived_path"] == removed["archive"]
    claim = record["claim"]
    assert claim["path"] == removed["archive"] and claim["owned_sha256"] == removed["sha256"]
    assert claim["identity"] == removed["identity"]
    relative = Path(removed["archive"])
    assert not relative.is_absolute() and ".." not in relative.parts
    archive = root / relative
    assert all(not part.is_symlink() for part in (archive, *archive.parents) if part != root.parent)
    info = archive.lstat()
    assert stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o644
    assert [info.st_dev, info.st_ino] == removed["identity"]
    assert sha(archive.read_bytes()) == removed["sha256"]
    assert epoch[pending["transition"]]["deleted_metadata"] == name
