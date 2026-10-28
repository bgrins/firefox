import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import os

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bundle', HERE / 'bundle.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
with tempfile.TemporaryDirectory(prefix='css-lh-bundle-controls-') as scratch:
    work = Path(scratch)
    root = work / 'app';root.mkdir()
    (root / 'nested').mkdir()
    (root / 'XUL').write_bytes(b'original executable');os.chmod(root / 'XUL', 0o755)
    (root / 'nested' / 'resource').write_bytes(b'original resource')
    (root / 'link').symlink_to('/external/unfollowed-target')
    os.lchmod(root / 'link', 0o700)
    (root / 'change-kind').write_bytes(b'old regular')
    initial = b.scan(root);mapping = b.backup(root, initial, work / 'backup')
    (root / 'XUL').write_bytes(b'candidate executable');os.chmod(root / 'XUL',0o644)
    (root / 'nested' / 'resource').unlink()
    (root / 'link').unlink();(root / 'link').symlink_to('/different/target')
    os.lchmod(root / 'link', 0o777)
    (root / 'change-kind').unlink();(root / 'change-kind').mkdir();(root / 'change-kind' / 'added').write_bytes(b'extra')
    (root / 'extra-dir').mkdir();(root / 'extra-dir' / 'extra-file').write_bytes(b'extra')
    post = b.scan(root)
    b.restore(root, initial, post, work / 'backup', mapping)
    assert b.semantic(b.scan(root)) == b.semantic(initial)
    stale = b.scan(root);(root / 'XUL').write_bytes(b'foreign update')
    try:b.restore(root,initial,stale,work/'backup',mapping)
    except AssertionError:pass
    else:raise AssertionError('accepted post-capture byte drift')
    assert (root / 'XUL').read_bytes()==b'foreign update'
    current=b.scan(root);saved=work/'backup'/mapping['XUL'];saved.write_bytes(b'corrupt backup')
    try:b.restore(root,initial,current,work/'backup',mapping)
    except AssertionError:pass
    else:raise AssertionError('accepted corrupt backup')
    assert (root/'XUL').read_bytes()==b'foreign update'
    (root/'nested'/'resource').unlink();(root/'nested').rmdir();(root/'nested').symlink_to(work)
    try:b.parents(root,root/'nested'/'unowned')
    except AssertionError:pass
    else:raise AssertionError('accepted symlink restoration parent')
spec = importlib.util.spec_from_file_location('cleanup', HERE / 'wpt_cleanup.py')
c = importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
with tempfile.TemporaryDirectory(prefix='css-lh-no-launch-') as scratch:
    out = Path(scratch) / 'wpt'
    assert c.no_launch(out)
    out.mkdir();assert c.no_launch(out)
    (out / 'COMMAND.json').write_text('{}');assert not c.no_launch(out)
    (out / 'COMMAND.json').unlink();(out / 'PROCESS.json').write_text('{}');assert not c.no_launch(out)
for p in HERE.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
assert not work.exists()
print(json.dumps({'bundle_roundtrip':True,'negative_controls':3,'scratch_removed':True,'syntax':True,'main_executed':False}))
