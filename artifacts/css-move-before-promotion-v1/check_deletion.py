import ast
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


h = load('deletion_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
create = load('deletion_creation', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
source = (HERE / 'install.py').read_text()
start = source.index("        archived = output / 'DELETED-METADATA.ini'")
end = source.index("        current['pins'][retired] = None", start)
move = compile('if True:\n' + source[start:end], '<actual installer deletion block>', 'exec')
start = source.index('            if retirement is not None:')
end = source.index('            for name in reversed(changed):', start)
restore = compile('if True:\n' + source[start:end], '<actual installer restoration block>', 'exec')
results = []
with tempfile.TemporaryDirectory(prefix='move-metadata-') as temporary:
    scratch = Path(temporary)
    for case in ('roundtrip', 'foreign_original', 'foreign_archive_body', 'foreign_archive_inode'):
        root = scratch / case
        retired = 'testing/web-platform/meta/dom/nodes/moveBefore/example.ini'
        original = root / retired
        original.parent.mkdir(parents=True)
        original.write_bytes(b'[example.html]\n  [test]\n    expected: FAIL\n')
        before = original.read_bytes()
        claim = h.claim(root, retired, h.digest(before))
        output = root / 'artifacts/runtime'
        output.mkdir(parents=True)
        namespace = dict(ROOT=root, output=output, retired=retired, retired_claim=claim,
                         retired_parents=create.parent_pins(root, original), h=h, create=create,
                         os=os, signal=signal, retirement=None, deletion={'sha256': h.digest(before)})
        exec(move, namespace)
        assert not original.exists()
        archived = output / 'DELETED-METADATA.ini'
        assert h.claim(root, str(archived.relative_to(root)), h.digest(before), claim['identity'])
        if case == 'foreign_original':
            original.write_bytes(b'foreign')
        elif case == 'foreign_archive_body':
            archived.write_bytes(b'foreign')
        elif case == 'foreign_archive_inode':
            other = output / 'replacement'
            other.write_bytes(before)
            os.replace(other, archived)
        rejected = False
        try:
            exec(restore, namespace)
        except (AssertionError, RuntimeError):
            rejected = True
        assert rejected == (case != 'roundtrip'), case
        if not rejected:
            assert original.read_bytes() == before
            assert h.claim(root, retired, h.digest(before), claim['identity'])
            assert not archived.exists()
        else:
            assert archived.exists()
            if case == 'foreign_original':
                assert original.read_bytes() == b'foreign'
        results.append({'case': case, 'rejected': rejected})
assert not scratch.exists()
print(json.dumps({'actual_installer_blocks': True, 'cases': results, 'scratch_removed': True,
                  'live_metadata_accessed': False}))
