import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for name, pin in json.loads((HERE / 'INPUTS.json').read_bytes()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin
spec = importlib.util.spec_from_file_location('owned', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
original_fdopen = os.fdopen
results = []
with tempfile.TemporaryDirectory(prefix='css-owned-write-review-') as scratch:
    root = Path(scratch)
    p = root / 'source.rs'
    before, candidate = b'original source\n', b'candidate source\n'
    for mode in ('short', 'raise_after_prefix', 'fsync_error', 'foreign_content'):
        p.write_bytes(before)
        claim = m.claim(root, 'source.rs', m.digest(before))
        class Stream:
            def __init__(self, inner): self.inner = inner
            def __enter__(self): return self
            def __exit__(self, *args): return self.inner.__exit__(*args)
            def __getattr__(self, name): return getattr(self.inner, name)
            def write(self, data):
                if mode == 'short': return self.inner.write(data[:4])
                if mode == 'raise_after_prefix':
                    self.inner.write(data[:5])
                    raise OSError('injected after prefix')
                if mode == 'foreign_content':
                    self.inner.write(b'foreign')
                    raise OSError('injected unowned content')
                return self.inner.write(data)
        def fdopen(*args, **kwargs): return Stream(original_fdopen(*args, **kwargs))
        original_fsync = os.fsync
        os.fdopen = fdopen
        if mode == 'fsync_error':
            def failed_fsync(fd): raise OSError('injected fsync failure')
            os.fsync = failed_fsync
        try:
            try: m.write_owned(root, claim, candidate)
            except (OSError, RuntimeError): pass
            else: raise AssertionError('fault did not occur')
        finally:
            os.fdopen = original_fdopen
            os.fsync = original_fsync
        if mode == 'foreign_content':
            try: m.write_owned(root, claim, before)
            except RuntimeError: pass
            else: raise AssertionError('overwrote unrecognized bytes')
            assert p.read_bytes() == b'foreign'
        else:
            assert claim['owned_sha256'] == m.digest(p.read_bytes())
            m.write_owned(root, claim, before)
            assert p.read_bytes() == before
        results.append(mode)
    p.write_bytes(before)
    claim = m.claim(root, 'source.rs', m.digest(before))
    other = root / 'replacement.rs';other.write_bytes(before);other.replace(p)
    try: m.write_owned(root, claim, candidate)
    except RuntimeError: pass
    else: raise AssertionError('accepted replacement inode')
    assert p.read_bytes() == before
    results.append('same_bytes_foreign_inode_rejected')
print(json.dumps({'passed':results,'scratch_removed':not root.exists(),'live_paths_written':False}))
